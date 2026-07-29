"""Confirmed GET /blast schemas (api-contract §2.4) + Proposed extensions."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

RiskLiteral = Literal["HIGH", "MEDIUM", "LOW"]


class BlastResponse(BaseModel):
    """Confirmed FR-08 blast fields + Proposed owners / index_revision."""

    direct_dependents: list[str] = Field(
        ..., description="Confirmed: 1-hop reverse-IMPORTS dependents (paths)"
    )
    transitive: list[str] = Field(
        ..., description="Confirmed: N-hop reverse-IMPORTS dependents beyond direct"
    )
    db_tables: list[str] = Field(
        ...,
        description="Confirmed key; V1 Proposed always [] (L2 Missing Evidence)",
    )
    risk: RiskLiteral = Field(..., description="Confirmed enum HIGH|MEDIUM|LOW")
    tests_to_run: list[str] = Field(
        ...,
        description=(
            "Confirmed key; V1 Proposed path-derived candidates only "
            "(no Confirmed L2 linkage)"
        ),
    )
    owners: list[Any] = Field(
        default_factory=list,
        description="Proposed OQ-15: empty array only — no Confirmed element schema",
    )
    index_revision: str | None = Field(
        default=None,
        description=(
            "Proposed freshness signal (EP-007 / US-027) — NOT a Confirmed §2.4 field"
        ),
    )
