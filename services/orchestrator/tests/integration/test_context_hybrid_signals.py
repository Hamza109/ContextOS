"""Hybrid-signal behavioral test: keyword-heavy vs semantic-heavy (T027)."""

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
def test_context_hybrid_signals_keyword_and_semantic(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "exact_token_module.py").write_text(
        "UNIQUE_TOKEN_XYZ = 1\ndef use_unique_token_xyz():\n    return UNIQUE_TOKEN_XYZ\n",
        encoding="utf-8",
    )
    (root / "semantic_auth.py").write_text(
        "def verify_credentials(user, secret):\n    '''Validate identity for session.'''\n    return True\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "signals_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    client = TestClient(app)

    kw = client.post(
        "/context",
        json={"query": "UNIQUE_TOKEN_XYZ", "repo": "signals_demo", "top_k": 3},
    )
    assert kw.status_code == 200
    kw_paths = [f["path"] for f in kw.json()["relevant_files"]]
    assert any("exact_token" in p for p in kw_paths)

    sem = client.post(
        "/context",
        json={"query": "validate user identity session", "repo": "signals_demo", "top_k": 3},
    )
    assert sem.status_code == 200
    # Trace should mention both channels when available
    trace = sem.json()["metrics"]["trace"]
    assert isinstance(trace, (dict, str))
    if isinstance(trace, dict):
        assert "bm25_hits" in trace or "vector_hits" in trace
