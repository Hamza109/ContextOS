"""Unit: L4 budget enforce with injectable ceilings (EP-008 T019)."""

from __future__ import annotations

from app.services.l4_budgets import enforce_budget
from app.services.l4_relevance import ScoredUnit


def _unit(path: str, score: float, tokens_ish: int) -> ScoredUnit:
    # estimate_tokens splits on whitespace — pad with words
    content = " ".join(f"w{i}" for i in range(tokens_ish))
    return ScoredUnit(path=path, content=content, score=score, phase_role="implementation", reasons=())


def test_under_budget_ok() -> None:
    units = [_unit("a.py", 0.9, 20), _unit("b.py", 0.8, 20)]
    out = enforce_budget(units, phase="Dev", phase_budgets={"Dev": 10_000})
    assert out.status == "ok"
    assert len(out.units) == 2
    assert out.pruned_paths == ()


def test_over_budget_degrades_then_ok() -> None:
    units = [
        _unit("high.py", 0.9, 40),
        _unit("mid.py", 0.5, 40),
        _unit("low.py", 0.1, 40),
    ]
    # Ceiling tight enough to force prune of lowest
    out = enforce_budget(units, phase="Dev", phase_budgets={"Dev": 70})
    assert out.status in {"degraded", "ok"}
    assert "low.py" in out.pruned_paths or out.tokens_after <= 70
    assert out.tokens_after <= 70


def test_hard_fail_when_unmet() -> None:
    units = [_unit("huge.py", 0.9, 200)]
    out = enforce_budget(units, phase="Dev", phase_budgets={"Dev": 10})
    assert out.status == "hard_fail"
    assert out.tokens_after > 10


def test_no_budget_configured() -> None:
    units = [_unit("a.py", 0.5, 30)]
    out = enforce_budget(units, phase="Dev", phase_budgets={})
    assert out.status == "no_budget"
