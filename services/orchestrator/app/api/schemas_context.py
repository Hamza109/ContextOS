"""Confirmed POST /context Pydantic models (api-contract §2.3) + Proposed extensions.

OQ-16 / OQ-11 / OQ-MVP-metrics / OQ-HTTP remain OPEN — Proposed fields labeled only.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ContextMetrics(BaseModel):
    """Confirmed metrics object keys (Appendix D).

    MVP values may be packing token counts only (OQ-MVP-metrics / A-06) — Proposed semantics.
    """

    tokens_before: int = Field(..., description="Confirmed key; MVP packing count Proposed (OQ-MVP-metrics)")
    tokens_after: int = Field(..., description="Confirmed key; MVP packing count Proposed (OQ-MVP-metrics)")
    saving_percent: float = Field(
        ...,
        description="Confirmed key; no invent pass thresholds (OQ-MVP-metrics)",
    )
    trace: str | dict[str, Any] = Field(
        ...,
        description="Confirmed key; pipeline trace string or object",
    )


class RelevantFileItem(BaseModel):
    """Proposed item shape for relevant_files entries — not Confirmed Appendix D keys."""

    path: str = Field(..., description="Proposed: file path")
    score: float = Field(..., description="Proposed: hybrid+MMR score")
    start_line: int | None = Field(default=None, description="Proposed: optional start line")
    end_line: int | None = Field(default=None, description="Proposed: optional end line")
    snippet: str | None = Field(default=None, description="Proposed: optional snippet")


class ContextRequest(BaseModel):
    """Confirmed request fields: query, file (optional), repo, top_k.

    Optional ``phase`` is **Proposed** only (OQ-16) — not Appendix D Confirmed.
    """

    query: str = Field(..., description="Confirmed: natural-language search / ask query")
    file: str | None = Field(
        default=None,
        description="Confirmed optional: cursor/file context bias",
    )
    repo: str = Field(..., description="Confirmed: logical repository name")
    top_k: int = Field(
        ...,
        description=(
            "Confirmed: positive integer only until product Confirms bounds (OQ-top_k). "
            "FR-02 'top 8' is illustrative — not Confirmed AC."
        ),
    )
    # Proposed (OQ-16) — phase selection; default applied in router when absent → Dev
    phase: str | None = Field(
        default=None,
        description=(
            "Proposed (OQ-16): SDLC phase Requirements|Design|Dev|Test|Deploy — "
            "NOT Appendix D Confirmed. Default Dev when omitted."
        ),
    )

    @field_validator("query")
    @classmethod
    def _query_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("query must be a non-empty string")
        return v

    @field_validator("repo")
    @classmethod
    def _repo_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("repo must be a non-empty string")
        # Light path-traversal sanitization — reject obvious escapes
        if ".." in v or v.startswith("/") or "\\" in v:
            raise ValueError("repo contains invalid path characters")
        return v.strip()

    @field_validator("top_k")
    @classmethod
    def _top_k_positive(cls, v: int) -> int:
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            raise ValueError("top_k must be a positive integer (OQ-top_k — no Confirmed bounds)")
        return v

    @field_validator("file")
    @classmethod
    def _file_sanitize(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if ".." in v or v.startswith("/") or "\\" in v:
            raise ValueError("file contains invalid path characters")
        return v

    @field_validator("phase")
    @classmethod
    def _phase_proposed(cls, v: str | None) -> str | None:
        if v is None:
            return None
        allowed = {"Requirements", "Design", "Dev", "Test", "Deploy"}
        if v not in allowed:
            raise ValueError(
                f"phase must be one of {sorted(allowed)} (Proposed OQ-16 — not Confirmed)"
            )
        return v


class ContextResponse(BaseModel):
    """Confirmed response fields only (api-contract §2.3).

    blast_radius / memory MAY be empty/null in MVP (**Proposed**).
    Citations live inside final_context string (OQ-11 open) — no parallel Confirmed JSON object.
    """

    final_context: str = Field(..., description="Confirmed: packed XML/context string")
    metrics: ContextMetrics
    blast_radius: dict[str, Any] | None = Field(
        default=None,
        description="Confirmed key; empty/null MVP (Proposed V1 blast)",
    )
    memory: dict[str, Any] | None = Field(
        default=None,
        description="Confirmed key; empty/null MVP (Proposed V2 memory)",
    )
    relevant_files: list[Any] = Field(
        ...,
        description=(
            "Confirmed key; item shape Proposed (path/score/...). "
            "FR-019: future CLI/extension Ask SHOULD call this API — no DX here."
        ),
    )
    is_real: bool = Field(..., description="Confirmed: true when retrieval is live")
