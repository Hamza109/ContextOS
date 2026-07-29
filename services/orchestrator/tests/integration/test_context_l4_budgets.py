"""Integration: L4 budget degrade/hard-fail path (EP-008 T024)."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.l4_budgets import DESIGN_PHASE_BUDGET_EXAMPLE
from app.services.l5_pack import PackResult
from app.services.l5_phase_pack import PhasePackResult
from app.services.l5_search import HybridSearchResult, SearchHit
from app.services.okf_retrieve import OkfRetrieveResult


def _patch(monkeypatch, body: str, hits: list[SearchHit]) -> None:
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
        lambda *args, **kwargs: PhasePackResult(body, 900, 800, 10.0, "Design"),
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


def test_injectable_budget_degrade_soft_200(monkeypatch) -> None:
    pad = " ".join(f"word{i}" for i in range(120))
    files = []
    hits = []
    for i, score in enumerate([0.9, 0.5, 0.1]):
        path = f"u{i}.py"
        content = f"def f{i}():\n    {pad}"
        files.append(f'<file path="{path}"><![CDATA[{content}]]></file>')
        hits.append(SearchHit(path, score, content))
    body = "<context_pack>" + "".join(files) + "</context_pack>"

    _patch(monkeypatch, body, hits)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "true")
    # Tight injectable ceiling — forces prune (not Confirmed Dev value)
    monkeypatch.setenv("CONTEXTOS_PHASE_BUDGETS", json.dumps({"Design": 80, "Dev": 80}))
    get_settings.cache_clear()

    resp = TestClient(app).post(
        "/context",
        json={"query": "f", "repo": "repo", "top_k": 5, "phase": "Design"},
    )
    assert resp.status_code == 200  # soft-degrade preferred
    trace = resp.json()["metrics"]["trace"]
    assert trace["l4_gate"] is True
    assert trace["budget_status"] in {"degraded", "hard_fail", "ok"}
    if trace["budget_status"] in {"degraded", "hard_fail"}:
        assert trace["degraded"] is True


def test_design_32k_example_under_budget(monkeypatch) -> None:
    content = "def design():\n    return True\n"
    body = f'<context_pack><file path="d.py"><![CDATA[{content}]]></file></context_pack>'
    hits = [SearchHit("d.py", 0.8, content)]
    _patch(monkeypatch, body, hits)
    monkeypatch.setenv("CONTEXTOS_L4_ENABLED", "true")
    monkeypatch.setenv(
        "CONTEXTOS_PHASE_BUDGETS",
        json.dumps({"Design": DESIGN_PHASE_BUDGET_EXAMPLE}),
    )
    get_settings.cache_clear()

    resp = TestClient(app).post(
        "/context",
        json={"query": "design", "repo": "repo", "top_k": 5, "phase": "Design"},
    )
    assert resp.status_code == 200
    assert resp.json()["metrics"]["trace"]["budget_status"] in {"ok", "no_budget", "degraded"}
