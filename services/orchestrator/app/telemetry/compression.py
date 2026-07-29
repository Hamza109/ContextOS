"""OpenTelemetry-compatible L4 compression telemetry (EP-008 / US-024).

Exporter vendor **[NEEDS CLARIFICATION: OQ-09]** — attrs only, exporter-agnostic.
Cost $ rates Missing Evidence — token-delta is primary ``compression.cost_saved``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.l4_compression import compression_ratio, saving_percent
from app.telemetry.context import _NullSpan


@dataclass
class CompressionTelemetryEvent:
    """In-memory last-event store for Proposed token dashboard (OQ-08)."""

    tokens_before: int = 0
    tokens_after: int = 0
    saving_percent: float = 0.0
    ratio: float = 1.0
    cost_saved: float = 0.0
    recall_at_k: float | None = None
    phase: str = ""
    repo: str = ""
    budget_status: str = ""
    extras: dict[str, Any] = field(default_factory=dict)


_LAST_EVENT: CompressionTelemetryEvent | None = None


def get_last_compression_event() -> CompressionTelemetryEvent | None:
    return _LAST_EVENT


def reset_last_compression_event() -> None:
    global _LAST_EVENT
    _LAST_EVENT = None


def compute_cost_saved(
    tokens_before: int,
    tokens_after: int,
    *,
    rate_per_1k_tokens: float | None = None,
) -> float:
    """Primary: token-delta. Optional $ when rate provided (rates Missing Evidence)."""
    tokens_saved = max(0, int(tokens_before) - int(tokens_after))
    if rate_per_1k_tokens is None:
        return float(tokens_saved)
    return round(tokens_saved / 1000.0 * float(rate_per_1k_tokens), 6)


def record_compression_attributes(
    span: Any,
    *,
    tokens_before: int,
    tokens_after: int,
    recall_at_k: float | None = None,
    rate_per_1k_tokens: float | None = None,
    phase: str = "",
    repo: str = "",
    budget_status: str = "",
    enabled: bool = True,
) -> dict[str, Any]:
    """Emit OTel-compatible attrs; honor enabled flag (OQ-EP008-b non-bypass)."""
    global _LAST_EVENT

    ratio = compression_ratio(tokens_before, tokens_after)
    saved_pct = saving_percent(tokens_before, tokens_after)
    cost_saved = compute_cost_saved(
        tokens_before,
        tokens_after,
        rate_per_1k_tokens=rate_per_1k_tokens,
    )

    attrs: dict[str, Any] = {
        "compression.ratio": ratio,
        "compression.cost_saved": cost_saved,
        "compression.tokens_before": int(tokens_before),
        "compression.tokens_after": int(tokens_after),
        "compression.saving_percent": saved_pct,
    }
    if recall_at_k is not None:
        attrs["compression.recall_at_k"] = float(recall_at_k)
    if phase:
        attrs["compression.phase"] = phase
    if budget_status:
        attrs["compression.budget_status"] = budget_status

    _LAST_EVENT = CompressionTelemetryEvent(
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        saving_percent=saved_pct,
        ratio=ratio,
        cost_saved=cost_saved,
        recall_at_k=recall_at_k,
        phase=phase,
        repo=repo,
        budget_status=budget_status,
    )

    if not enabled:
        return attrs

    if span is None or isinstance(span, _NullSpan):
        return attrs

    for key, value in attrs.items():
        try:
            span.set_attribute(key, value)
        except Exception:  # noqa: BLE001
            continue
    return attrs
