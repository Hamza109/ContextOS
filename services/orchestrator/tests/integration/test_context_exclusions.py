"""Privacy inheritance: /context must not introduce excluded paths (T028, T063)."""

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
def test_context_excludes_env_and_secrets(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "app.py").write_text("SECRET_REF = 'safe'\n", encoding="utf-8")
    (root / ".env").write_text("API_KEY=supersecret\n", encoding="utf-8")
    (root / "credentials.json").write_text('{"password":"leak"}\n', encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "excl_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "API_KEY password secret", "repo": "excl_demo", "top_k": 10},
    )
    assert resp.status_code == 200
    blob = resp.text.lower()
    paths = [f["path"].lower() for f in resp.json()["relevant_files"]]
    assert ".env" not in paths
    assert "credentials.json" not in paths
    assert "supersecret" not in blob
    assert "api_key=supersecret" not in blob
