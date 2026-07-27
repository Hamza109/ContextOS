"""Integration: Pack Context safe-edit enrichment on POST /context (T058).

Must not break Confirmed response fields; no invented Appendix D keys (SC-009).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.embeddings import HashEmbedder
from app.adapters.qdrant_store import QdrantStore
from app.config import Settings
from app.main import app
from app.services.l3_symbol import SAFE_EDIT_BEGIN, is_symbol_scoped_plan
from app.services.l5_index import run_index


def _qdrant_available(url: str) -> bool:
    try:
        from qdrant_client import QdrantClient

        QdrantClient(url=url, timeout=2).get_collections()
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.requires_qdrant
def test_context_safe_edit_enrichment(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "svc.py").write_text("def charge():\n    return 1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")
    monkeypatch.setenv("CONTEXTOS_SERENA_USE_TEST_DOUBLE", "1")
    monkeypatch.setenv("CONTEXTOS_CONTEXT_SAFE_EDIT_ENRICHMENT", "1")

    settings = Settings(
        qdrant_url=url,
        pack_cache_dir=tmp_path / "packs",
        serena_use_test_double=True,
        context_safe_edit_enrichment=True,
    )
    run_index(
        str(root),
        "safe_edit_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    from app.config import get_settings

    get_settings.cache_clear()

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={
            "query": "charge payment",
            "file": "svc.py",
            "repo": "safe_edit_demo",
            "top_k": 3,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    # Confirmed fields present
    for key in (
        "final_context",
        "metrics",
        "blast_radius",
        "memory",
        "relevant_files",
        "is_real",
    ):
        assert key in data
    # Must NOT invent Confirmed Appendix D L3 fields
    assert "safe_edit_plan" not in data
    assert "symbol_definition" not in data
    assert SAFE_EDIT_BEGIN in data["final_context"]
    assert is_symbol_scoped_plan(data["final_context"])
