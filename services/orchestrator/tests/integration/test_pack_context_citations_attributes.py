"""Integration: citation attributes on packed output after L3 enrichment (T059; OQ-11).

Assert file:line + confidence attributes only — no invented Confirmed JSON keys.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings, get_settings
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
def test_pack_context_citation_attributes_with_enrichment(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "mod.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")
    monkeypatch.setenv("CONTEXTOS_SERENA_USE_TEST_DOUBLE", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "cite_l3_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )
    get_settings.cache_clear()

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "foo", "repo": "cite_l3_demo", "top_k": 3},
    )
    assert resp.status_code == 200
    packed = resp.json()["final_context"]
    assert citations_present(packed)
    # OQ-11: do not require invented Confirmed citation JSON keys
    assert "citation_id" not in packed
    assert '"sources"' not in packed
