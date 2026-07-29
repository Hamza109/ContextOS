"""Integration: L4-on vs packing-off metrics semantics (EP-008 T026 / T030)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.l5_pack import PackResult
from app.services.l5_phase_pack import PhasePackResult
from app.services.l5_search import HybridSearchResult, SearchHit
from app.services.okf_retrieve import OkfRetrieveResult


def _patch(monkeypatch, body: str, hits: list[SearchHit], *, tb: int = 100, ta: int = 40) -> None:
    monkeypatch.setenv("CONTEXTOS_CONTEXT_SAFE_EDIT_ENRICHMENT", "false")
    monkeypatch.setattr(
        "app.api.context.load_pack_by_repo",
        lambda *args, **kwargs: PackResult("repo", "<base/>", 10, 1, 0, None),
    )
    monkeypatch.setattr(
        "app.api.context.hybrid_search",
        lambda **kwargs: HybridSearchResult(hits, 1, 0, False, [], None),
    )
    monkeypatch.setattr(
        "app.api.context.pack_for_phase",
        lambda *args, **kwargs: PhasePackResult(body, tb, ta, 60.0, "Dev"),
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


def test_l4_off_packing_estimate_semantics(monkeypatch) -> None:
    body = '<context_pack><file path="a.py"><![CDATA[x]]></file></context_pack>'
    _patch(monkeypatch, body, [SearchHit("a.py", 0.5, "x")], tb=111, ta=55)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "false")
    get_settings.cache_clear()
    data = TestClient(app).post(
        "/context", json={"query": "x", "repo": "repo", "top_k": 3}
    ).json()
    assert data["metrics"]["tokens_before"] == 111
    assert data["metrics"]["tokens_after"] == 55
    assert data["metrics"]["saving_percent"] == 60.0
    assert data["metrics"]["trace"]["l4_gate"] is False


def test_l4_on_metrics_are_l4_outcomes(monkeypatch) -> None:
    pad = "\n".join(f"print({i})" for i in range(300))
    content = f"def keep():\n    # TODO: keep\n{pad}"
    body = f'<context_pack><file path="a.py" score="0.1"><![CDATA[{content}]]></file></context_pack>'
    _patch(monkeypatch, body, [SearchHit("a.py", 0.1, content)], tb=999, ta=900)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "true")
    get_settings.cache_clear()
    data = TestClient(app).post(
        "/context", json={"query": "keep", "repo": "repo", "top_k": 3}
    ).json()
    m = data["metrics"]
    assert m["trace"]["l4_gate"] is True
    # L4 outcomes replace packing estimates (not the stubbed 999/900).
    assert m["tokens_before"] != 999 or m["tokens_after"] != 900
    assert m["tokens_after"] <= m["tokens_before"]
    assert set(m.keys()) == {"tokens_before", "tokens_after", "saving_percent", "trace"}
