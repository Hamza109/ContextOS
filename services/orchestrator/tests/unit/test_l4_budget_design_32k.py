"""Unit: Design phase 32k evidenced FR-11 example (EP-008 T020)."""

from __future__ import annotations

from app.services.l4_budgets import DESIGN_PHASE_BUDGET_EXAMPLE, enforce_budget
from app.services.l4_relevance import ScoredUnit


def test_design_32k_example_constant() -> None:
    assert DESIGN_PHASE_BUDGET_EXAMPLE == 32_000


def test_design_budget_32k_under_succeeds() -> None:
    content = " ".join(f"tok{i}" for i in range(100))
    units = [
        ScoredUnit("d.py", content, 0.8, "design_surface", ()),
    ]
    out = enforce_budget(
        units,
        phase="Design",
        phase_budgets={"Design": DESIGN_PHASE_BUDGET_EXAMPLE},
    )
    assert out.status == "ok"
    assert out.max_tokens == 32_000
    assert out.tokens_after <= 32_000
