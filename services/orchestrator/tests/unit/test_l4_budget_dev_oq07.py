"""OQ-07 gated Dev numeric AC — skip until product resolves 8k vs 12k (EP-008 T021)."""

from __future__ import annotations

import pytest

from app.services.l4_budgets import enforce_budget
from app.services.l4_relevance import ScoredUnit


@pytest.mark.skip(reason="OQ-07 unresolved: Dev budget 8k (§5) vs 12k (FR-11) — do not invent Confirmed")
@pytest.mark.parametrize("dev_budget", [8_000, 12_000])
def test_dev_canonical_budget_oq07(dev_budget: int) -> None:
    """Placeholder: unlock in T037 when OQ-07 resolves; until then injectable-only."""
    content = " ".join(f"t{i}" for i in range(50))
    units = [ScoredUnit("a.py", content, 0.5, "implementation", ())]
    out = enforce_budget(units, phase="Dev", phase_budgets={"Dev": dev_budget})
    assert out.max_tokens == dev_budget
