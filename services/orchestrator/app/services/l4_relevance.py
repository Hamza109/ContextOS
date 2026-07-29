"""Proposed L4 relevance scoring (EP-008 / US-023).

Algorithm is **Proposed** — reuse hybrid hit scores + phase_role boosts.
Optional recency only when already present on the unit (do not invent store fields).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RelevanceUnit:
    """One compressible unit (file/chunk) with score inputs."""

    path: str
    content: str
    hit_score: float = 0.0
    phase_role: str = "implementation"
    # Optional — only when caller already has a signal (mtime epoch / age days). Missing → omit.
    recency: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ScoredUnit:
    path: str
    content: str
    score: float
    phase_role: str
    reasons: tuple[str, ...]
    hit_score: float = 0.0
    recency: float | None = None


# Proposed phase_role boosts (not Confirmed product weights).
_PHASE_ROLE_BOOST: dict[str, float] = {
    "primary_test": 0.20,
    "under_test": 0.08,
    "requirement_signal": 0.12,
    "design_surface": 0.15,
    "deploy_entrypoint": 0.18,
    "runtime_related": 0.05,
    "implementation": 0.10,
}


def score_unit(unit: RelevanceUnit) -> ScoredUnit:
    """Score one unit: hybrid hit score + phase_role boost + optional recency.

    Proposed formula (v1 heuristic):
      base = clamp(hit_score, 0..1)
      + phase_role boost (table)
      + 0.05 * clamp(recency, 0..1) when recency is provided
    """
    reasons: list[str] = []
    base = _clamp01(float(unit.hit_score))
    reasons.append(f"hit_score={base:.4f}")

    boost = _PHASE_ROLE_BOOST.get(unit.phase_role, 0.05)
    reasons.append(f"phase_role={unit.phase_role}+{boost:.2f}")

    recency_term = 0.0
    if unit.recency is not None:
        recency_term = 0.05 * _clamp01(float(unit.recency))
        reasons.append(f"recency+{recency_term:.4f}")

    total = _clamp01(base + boost + recency_term)
    return ScoredUnit(
        path=unit.path,
        content=unit.content,
        score=total,
        phase_role=unit.phase_role,
        reasons=tuple(reasons),
        hit_score=base,
        recency=unit.recency,
    )


def score_units(units: list[RelevanceUnit]) -> list[ScoredUnit]:
    """Score and return units sorted by descending relevance (stable for ties)."""
    scored = [score_unit(u) for u in units]
    return sorted(scored, key=lambda s: (-s.score, s.path))


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
