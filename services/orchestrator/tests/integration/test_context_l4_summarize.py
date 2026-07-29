"""Integration: L4 summarize on /context (EP-008 T018)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.l5_pack import PackResult
from app.services.l5_phase_pack import PhasePackResult
from app.services.l5_search import HybridSearchResult, SearchHit
from app.services.okf_retrieve import OkfRetrieveResult


def _verbose(n: int = 200) -> str:
    lines = ["class S:", "    def run(self):", "        # TODO: x", "        pass"]
    lines += [f"        print('pad {i}')" for i in range(n)]
    return "\n".join(lines)


def _patch_l5(monkeypatch, *, hits: list[SearchHit], packed_body: str, tokens_before: int = 500) -> None:
    monkeypatch.setenv("CONTEXTOS_CONTEXT_SAFE_EDIT_ENRICHMENT", "false")
    monkeypatch.setattr(
        "app.api.context.load_pack_by_repo",
        lambda *args, **kwargs: PackResult("repo", "<base/>", 10, 1, 0, None),
    )
    monkeypatch.setattr(
        "app.api.context.hybrid_search",
        lambda **kwargs: HybridSearchResult(hits, len(hits), 0, False, [], None),
    )
    monkeypatch.setattr(
        "app.api.context.pack_for_phase",
        lambda *args, **kwargs: PhasePackResult(packed_body, tokens_before, 200, 60.0, "Dev"),
    )
    monkeypatch.setattr("app.api.context.get_embedder", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.api.context.QdrantStore", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        "app.api.context.retrieve_okf",
        lambda *args, **kwargs: OkfRetrieveResult(
            status="miss",
            concepts=[],
            duration_ms=0,
            evidence_block="",
            matched_ids=[],
        ),
    )
    # Disable L1 enrichment side effects
    monkeypatch.setattr(
        "app.api.context.StructuralQueryService",
        lambda settings: type(
            "S",
            (),
            {
                "enrich": lambda self, fc, **kw: type(
                    "E",
                    (),
                    {
                        "final_context": fc,
                        "status": "l1_miss",
                        "cache_hit": False,
                        "entity_count": 0,
                        "duration_ms": 0,
                    },
                )()
            },
        )(),
    )


def test_l4_on_compresses_final_context(monkeypatch) -> None:
    verbose = _verbose(250)
    body = (
        '<?xml version="1.0"?><context_pack>'
        f'<file path="noise.py" score="0.1"><![CDATA[{verbose}]]></file>'
        '<file path="core.py" score="0.95"><![CDATA[def core():\n    return 1]]></file>'
        "</context_pack>"
    )
    hits = [
        SearchHit("noise.py", 0.1, verbose),
        SearchHit("core.py", 0.95, "def core():\n    return 1"),
    ]
    _patch_l5(monkeypatch, hits=hits, packed_body=body, tokens_before=800)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "true")
    get_settings.cache_clear()

    resp = TestClient(app).post(
        "/context",
        json={"query": "core", "repo": "repo", "top_k": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["metrics"]["trace"]["l4_gate"] is True
    assert "l4_compress" in data["metrics"]["trace"]["l4_stage_order"]
    assert data["metrics"]["tokens_after"] < data["metrics"]["tokens_before"]
    assert len(data["final_context"]) < len(body)
    assert "def core" in data["final_context"]


def test_l4_off_preserves_packing_metrics(monkeypatch) -> None:
    body = '<context_pack><file path="a.py"><![CDATA[hello]]></file></context_pack>'
    hits = [SearchHit("a.py", 0.5, "hello")]
    _patch_l5(monkeypatch, hits=hits, packed_body=body, tokens_before=42)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "false")
    get_settings.cache_clear()

    resp = TestClient(app).post(
        "/context",
        json={"query": "hello", "repo": "repo", "top_k": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["metrics"]["trace"]["l4_gate"] is False
    assert data["metrics"]["tokens_before"] == 42
    assert data["metrics"]["tokens_after"] == 200
    assert data["final_context"] == body
