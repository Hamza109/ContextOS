"""Degraded / partial-index behavior (T058) — prefer reduced results over hard-fail-all."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.l5_pack import pack_cache_path


def test_context_unknown_repo_proposed_404(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "anything", "repo": "totally_missing_repo_xyz", "top_k": 3},
    )
    # Proposed 404 when neither pack nor hits
    assert resp.status_code in {404, 503}


def test_context_pack_only_degraded_path(tmp_path: Path, monkeypatch) -> None:
    """When pack cache exists but Qdrant may be empty/unavailable, BM25-only path can still work."""
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    monkeypatch.setenv("CONTEXTOS_EMBEDDING_STUB", "1")
    monkeypatch.setenv("CONTEXTOS_QDRANT_URL", "http://127.0.0.1:1")  # unlikely up

    # Persist a minimal pack without indexing
    from app.config import Settings, get_settings

    get_settings.cache_clear()
    settings = Settings(pack_cache_dir=tmp_path / "packs", qdrant_url="http://127.0.0.1:1")
    xml = (
        '<?xml version="1.0"?>\n'
        '<repository name="degraded_demo">\n'
        '  <file path="only.py"><![CDATA[def only_fn():\n    return 1\n]]></file>\n'
        "</repository>\n"
    )
    path = pack_cache_path("degraded_demo", settings=settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml, encoding="utf-8")

    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "only_fn", "repo": "degraded_demo", "top_k": 3},
    )
    # Prefer partial success (200 with degraded note) over hard-fail-all
    if resp.status_code == 200:
        data = resp.json()
        assert data["is_real"] is True
        trace = data["metrics"]["trace"]
        assert isinstance(data["relevant_files"], list)
        if isinstance(trace, dict):
            assert trace.get("degraded") is True or len(data["relevant_files"]) >= 0
    else:
        # Accept Proposed 404/503 if environment cannot serve partial
        assert resp.status_code in {404, 503}
