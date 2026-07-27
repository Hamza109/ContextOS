"""Integration: POST /context hybrid search (T026). Skips if Qdrant unavailable."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings
from app.main import app
from app.services.l5_index import run_index


def _qdrant_available(url: str) -> bool:
    try:
        from qdrant_client import QdrantClient

        QdrantClient(url=url, timeout=2).get_collections()
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.requires_qdrant
def test_context_hybrid_search_ranked_files(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "auth_service.py").write_text(
        "def authenticate_user(username, password):\n    return username == 'admin'\n",
        encoding="utf-8",
    )
    (root / "utils.py").write_text("def helper():\n    return 42\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "hybrid_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={
            "query": "authenticate_user password login",
            "repo": "hybrid_demo",
            "top_k": 5,
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["is_real"] is True
    assert isinstance(data["relevant_files"], list)
    assert len(data["relevant_files"]) >= 1
    # Proposed item shape carries scores
    assert "score" in data["relevant_files"][0]
    assert "path" in data["relevant_files"][0]
    # MVP empty allowed
    assert data["blast_radius"] in ({}, None) or data["blast_radius"] == {}
    assert data["memory"] in ({}, None) or data["memory"] == {}
    assert "final_context" in data
    assert "metrics" in data
