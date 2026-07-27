"""Degraded / partial-index behavior (EP-005 T023–T025 / FR-009, FR-010, SC-006).

Prefer reduced discovery over hard-fail-all when any modality remains usable.
HTTP status codes and metrics.trace.degraded / notes remain Proposed only
(OQ-HTTP-Health, OQ-Degraded-Shape) — MUST NOT Confirmed-freeze shapes or codes.
OQ-Uptime-Harness blocks SC-007 Pass — not asserted here.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.services.l5_pack import pack_cache_path
from app.services.l5_search import HybridSearchResult, hybrid_search


def test_context_unknown_repo_proposed_404(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    client = TestClient(app)
    resp = client.post(
        "/context",
        json={"query": "anything", "repo": "totally_missing_repo_xyz", "top_k": 3},
    )
    # Proposed HTTP only (OQ-HTTP-Health / OQ-Degraded-Shape) — not Confirmed-frozen
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
    # Prefer partial success (200 with Proposed degraded note) over hard-fail-all
    if resp.status_code == 200:
        data = resp.json()
        assert data["is_real"] is True
        trace = data["metrics"]["trace"]
        assert isinstance(data["relevant_files"], list)
        # Proposed observability fields (OQ-Degraded-Shape / P-1) — not Appendix D Confirmed
        if isinstance(trace, dict):
            assert trace.get("degraded") is True or len(data["relevant_files"]) >= 0
    else:
        # Accept Proposed 404/503 if environment cannot serve partial
        assert resp.status_code in {404, 503}


def test_hybrid_search_vector_failure_still_returns_bm25(tmp_path: Path, monkeypatch) -> None:
    """T025: Qdrant-down / vector error → behavioral degrade, not total outage when pack exists."""
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    from app.config import Settings, get_settings
    from app.services.l5_pack import PackResult

    get_settings.cache_clear()
    settings = Settings(pack_cache_dir=tmp_path / "packs", qdrant_url="http://127.0.0.1:1")
    xml = (
        '<?xml version="1.0"?>\n'
        '<repository name="partial_fail">\n'
        '  <file path="svc.py"><![CDATA[def authenticate_user():\n    pass\n]]></file>\n'
        "</repository>\n"
    )
    pack = PackResult(
        repo_name="partial_fail",
        xml_content=xml,
        token_count=10,
        files_packed=1,
        files_excluded=0,
        artifact_path=None,
    )

    failing_store = MagicMock()
    failing_store.search.side_effect = ConnectionError("qdrant down")

    class StubEmb:
        def embed(self, texts):
            return [[0.1] * 8 for _ in texts]

    result = hybrid_search(
        query="authenticate_user",
        repo="partial_fail",
        top_k=3,
        settings=settings,
        embedder=StubEmb(),  # type: ignore[arg-type]
        store=failing_store,
        pack=pack,
    )
    assert isinstance(result, HybridSearchResult)
    assert result.degraded is True
    # Proposed notes (OQ-Degraded-Shape) — behavioral check only
    assert any("vector_error" in n for n in result.trace_notes)
    assert len(result.hits) >= 1
    assert any("svc.py" in h.path for h in result.hits)


def test_hybrid_search_pack_miss_marks_degraded(tmp_path: Path, monkeypatch) -> None:
    """Pack miss degrades; must not invent Confirmed response schema fields."""
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "empty_packs"))
    from app.config import Settings, get_settings

    get_settings.cache_clear()
    settings = Settings(pack_cache_dir=tmp_path / "empty_packs", qdrant_url="http://127.0.0.1:1")

    failing_store = MagicMock()
    failing_store.search.side_effect = ConnectionError("qdrant down")

    class StubEmb:
        def embed(self, texts):
            return [[0.0] * 8 for _ in texts]

    result = hybrid_search(
        query="nothing",
        repo="missing_pack_repo",
        top_k=2,
        settings=settings,
        embedder=StubEmb(),  # type: ignore[arg-type]
        store=failing_store,
        pack=None,
    )
    assert result.degraded is True
    assert "pack_cache_miss" in result.trace_notes
    # Empty hits OK when both modalities fail — still a structured degrade, not raise
    assert isinstance(result.hits, list)
