"""Query-time external LLM consent gate (US-016).

Deny-by-default when consent/configuration is absent (FR-018, FR-021).
Does NOT invent consent UX/storage/CRUD APIs (OQ-US016 open).
Index path must never call external LLMs regardless of consent (FR-009).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ConsentDecision(StrEnum):
    DENY_EXTERNAL = "deny_external"
    ALLOW_EXTERNAL_PACKED_CONTEXT_ONLY = "allow_external_packed_context_only"
    USE_LOCAL_INFERENCE = "use_local_inference"


@dataclass(frozen=True)
class ConsentContext:
    """Minimal consent/configuration snapshot — flag/config only (OQ-US016)."""

    external_llm_consent: bool = False
    local_inference_configured: bool = False


@dataclass(frozen=True)
class AllowedTransmission:
    """FR-019: when consent present, only packed/compressed context path is allowed.

    Full L4 compression product is out of scope for EP-001 — this is a security
    boundary hook, not an EP-002 `/context` delivery.
    """

    may_send_external: bool
    content_kind: str  # "packed_or_compressed_context_only" | "none" | "local_only"
    reason: str


def evaluate_query_time_llm(ctx: ConsentContext) -> ConsentDecision:
    """Decide query-time LLM routing. Index path must not use this for embeddings."""
    if ctx.local_inference_configured and not ctx.external_llm_consent:
        # Local Ollama-style path may operate without external exfil (FR-020)
        return ConsentDecision.USE_LOCAL_INFERENCE
    if ctx.external_llm_consent:
        return ConsentDecision.ALLOW_EXTERNAL_PACKED_CONTEXT_ONLY
    return ConsentDecision.DENY_EXTERNAL


def assert_external_llm_allowed(ctx: ConsentContext) -> None:
    """Raise PermissionError if external LLM would be invoked without consent."""
    decision = evaluate_query_time_llm(ctx)
    if decision == ConsentDecision.DENY_EXTERNAL:
        raise PermissionError(
            "External LLM use denied: consent/configuration absent (deny-by-default; OQ-US016)"
        )
    if decision == ConsentDecision.USE_LOCAL_INFERENCE:
        raise PermissionError(
            "External LLM use denied: local inference configured; use local path (FR-020)"
        )


def allowed_transmission_for_external(ctx: ConsentContext) -> AllowedTransmission:
    """FR-019 behavioral boundary: consented external path = packed/compressed context only."""
    decision = evaluate_query_time_llm(ctx)
    if decision == ConsentDecision.DENY_EXTERNAL:
        return AllowedTransmission(
            may_send_external=False,
            content_kind="none",
            reason="consent absent — deny-by-default",
        )
    if decision == ConsentDecision.USE_LOCAL_INFERENCE:
        return AllowedTransmission(
            may_send_external=False,
            content_kind="local_only",
            reason="local inference configured — no external exfil",
        )
    return AllowedTransmission(
        may_send_external=True,
        content_kind="packed_or_compressed_context_only",
        reason="consent present — Appendix C packed/compressed path only (L4 product N/A EP-001)",
    )


def index_path_may_call_external_llm() -> bool:
    """Hard guarantee for US-002 / FR-009 — always False."""
    return False
