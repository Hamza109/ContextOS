"""POST /index → Qdrant upsert integration (T035). Skips if Qdrant unavailable."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.embeddings import HashEmbedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings
from app.services.l5_index import run_index


def _qdrant_available(url: str) -> bool:
    try:
        from qdrant_client import QdrantClient

        QdrantClient(url=url, timeout=2).get_collections()
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.requires_qdrant
def test_index_upserts_to_qdrant(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    store = QdrantStore(settings)
    result = run_index(
        str(root),
        "itest",
        settings=settings,
        embedder=HashEmbedder(),
        store=store,
    )
    assert result.files_indexed >= 1
    assert result.embeddings >= 1
    assert result.graph_nodes > 0
    assert result.time_ms >= 0
