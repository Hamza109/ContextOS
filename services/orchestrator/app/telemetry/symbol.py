"""OpenTelemetry-compatible L3 symbol helpers (exporter-agnostic; ADR-011).

Exact metric / span names are **Proposed** — Missing Evidence for Confirmed names.
Exporter vendor remains open (OQ-OTEL / ADR-011).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
except ImportError:  # pragma: no cover
    trace = None  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore


def get_tracer(name: str = "contextos.symbol"):
    if trace is None:
        return None
    return trace.get_tracer(name)


@contextmanager
def symbol_span(
    name: str,
    *,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Proposed spans: symbol.definition / references / rename_scope / pack_context.enrichment."""
    tracer = get_tracer()
    if tracer is None:
        yield _NullSpan()
        return

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    span.set_attribute(k, v)
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            if Status is not None and StatusCode is not None:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            span.record_exception(exc)
            raise


def record_duration_ms(span: Any, key: str, duration_ms: float) -> None:
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute(key, float(duration_ms))


class _NullSpan:
    def set_attribute(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def record_exception(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def set_status(self, *_args: Any, **_kwargs: Any) -> None:
        return None
