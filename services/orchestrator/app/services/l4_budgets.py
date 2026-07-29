"""Proposed L4 phase token budgets (EP-008 / US-022).

Design=32k is an evidenced FR-11 example constant only.
Dev canonical value is injectable until OQ-07 resolves — do NOT hard-code 8k/12k as truth.
Degradation algorithm: Proposed iterative prune of lowest-relevance units (OQ-EP008-a open).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from app.services.l4_relevance import ScoredUnit
from app.services.l5_pack import estimate_tokens

# Evidenced FR-11 Design-phase example — OK in tests/fixtures. Not a Dev Confirmed value.
DESIGN_PHASE_BUDGET_EXAMPLE = 32_000

# Minimum units retained before hard-fail (Proposed).
_MIN_RETAIN = 1


@dataclass(frozen=True)
class BudgetOutcome:
    units: list[ScoredUnit]
    tokens_after: int
    max_tokens: int | None
    status: str  # "ok" | "degraded" | "hard_fail" | "no_budget"
    pruned_paths: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    provenance: dict[str, object] = field(default_factory=dict)


def resolve_phase_budget(
    phase: str,
    phase_budgets: Mapping[str, int] | None,
) -> int | None:
    """Return max_tokens for phase from injectable map, or None if unset."""
    if not phase_budgets:
        return None
    if phase in phase_budgets:
        return int(phase_budgets[phase])
    # Case-insensitive fallback
    lower = {k.lower(): int(v) for k, v in phase_budgets.items()}
    return lower.get(phase.lower())


def estimate_units_tokens(units: list[ScoredUnit]) -> int:
    body = "\n".join(u.content or "" for u in units)
    return estimate_tokens(body) if body.strip() else 0


def enforce_budget(
    units: list[ScoredUnit],
    *,
    phase: str,
    phase_budgets: Mapping[str, int] | None,
    max_tokens: int | None = None,
) -> BudgetOutcome:
    """Enforce phase budget via Proposed iterative lowest-relevance prune.

    Steps (Proposed / OQ-EP008-a Missing Evidence for exact product table):
      1. If no ceiling → status=no_budget, return as-is.
      2. While over budget and >_MIN_RETAIN units: drop lowest-score unit.
      3. If still over after prune → status=hard_fail (caller may soft-degrade on 200).
      4. If any prune occurred and under budget → status=degraded.
      5. Else → status=ok.
    """
    ceiling = max_tokens if max_tokens is not None else resolve_phase_budget(phase, phase_budgets)
    steps: list[str] = [f"phase={phase}"]

    if ceiling is None:
        tokens = estimate_units_tokens(units)
        steps.append("no_budget_configured")
        return BudgetOutcome(
            units=list(units),
            tokens_after=tokens,
            max_tokens=None,
            status="no_budget",
            steps=tuple(steps),
            provenance={"algorithm": "proposed_iterative_prune_oq_ep008_a"},
        )

    steps.append(f"ceiling={ceiling}")
    remaining = sorted(units, key=lambda u: (-u.score, u.path))
    pruned: list[str] = []
    tokens = estimate_units_tokens(remaining)

    while tokens > ceiling and len(remaining) > _MIN_RETAIN:
        # Drop lowest relevance (last in descending sort).
        dropped = remaining.pop()
        pruned.append(dropped.path)
        steps.append(f"prune:{dropped.path}:score={dropped.score:.4f}")
        tokens = estimate_units_tokens(remaining)

    if tokens > ceiling:
        steps.append("hard_fail:unmet_after_prune")
        return BudgetOutcome(
            units=remaining,
            tokens_after=tokens,
            max_tokens=ceiling,
            status="hard_fail",
            pruned_paths=tuple(pruned),
            steps=tuple(steps),
            provenance={"algorithm": "proposed_iterative_prune_oq_ep008_a"},
        )

    status = "degraded" if pruned else "ok"
    steps.append(f"status={status}")
    return BudgetOutcome(
        units=remaining,
        tokens_after=tokens,
        max_tokens=ceiling,
        status=status,
        pruned_paths=tuple(pruned),
        steps=tuple(steps),
        provenance={"algorithm": "proposed_iterative_prune_oq_ep008_a"},
    )
