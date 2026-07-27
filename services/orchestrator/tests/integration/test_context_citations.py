"""Citations in successful POST /context final_context (T052)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings
from app.main import app
from app.services.l5_citations import citations_present
from app.services.l5_index import run_index


def _qdrant_available(url: str) -> bool:
    try:
        from qdrant_client import QdrantClient

        QdrantClient(url=url, timeout=2).get_collections()
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.requires_qdrant
def test_context_citations_in_final_context(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "mod.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "cite_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "foo", "repo": "cite_demo", "top_k": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_real"] is True
    assert citations_present(data["final_context"])
    assert "metrics" in data
    assert isinstance(data["relevant_files"], list)
