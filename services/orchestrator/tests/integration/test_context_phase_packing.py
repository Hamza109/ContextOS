"""Phase packing integration — two phases differ (T042)."""

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
def test_context_phase_packing_differs(tmp_path: Path, monkeypatch) -> None:
    url = "http://localhost:6333"
    if not _qdrant_available(url):
        pytest.skip("Qdrant not available at localhost:6333")

    root = tmp_path / "repo"
    root.mkdir()
    (root / "service.py").write_text(
        "class Service:\n    def run(self):\n        return 1\n",
        encoding="utf-8",
    )
    (root / "tests" ).mkdir()
    (root / "tests" / "test_service.py").write_text(
        "def test_run():\n    assert True\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")

    settings = Settings(qdrant_url=url, pack_cache_dir=tmp_path / "packs")
    run_index(
        str(root),
        "phase_demo",
        settings=settings,
        embedder=HashEmbedder(),
        store=QdrantStore(settings),
    )

    client = TestClient(app)
    body = {"query": "Service run", "repo": "phase_demo", "top_k": 5}
    r_dev = client.post("/context", json={**body, "phase": "Dev"})
    r_test = client.post("/context", json={**body, "phase": "Test"})
    assert r_dev.status_code == 200
    assert r_test.status_code == 200
    assert r_dev.json()["final_context"] != r_test.json()["final_context"]
    assert 'phase="Dev"' in r_dev.json()["final_context"]
    assert 'phase="Test"' in r_test.json()["final_context"]
    # No L4 gate required
    trace = r_dev.json()["metrics"]["trace"]
    if isinstance(trace, dict):
        assert trace.get("l4_gate") is False
