"""OpenTelemetry-compatible /context helpers (exporter-agnostic; ADR-011 / OQ-OTEL open)."""

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


def get_tracer(name: str = "contextos.context"):
    if trace is None:
        return None
    return trace.get_tracer(name)


@contextmanager
def context_span(
    name: str = "context.request",
    *,
    repo: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Create an OTel span for POST /context; no-ops safely if SDK/exporter unset."""
    tracer = get_tracer()
    attrs: dict[str, Any] = {}
    if repo:
        attrs["repo"] = repo
    if attributes:
        attrs.update(attributes)

    if tracer is None:
        yield _NullSpan()
        return

    with tracer.start_as_current_span(name) as span:
        for k, v in attrs.items():
            span.set_attribute(k, v)
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            if Status is not None and StatusCode is not None:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            span.record_exception(exc)
            raise


@contextmanager
def child_span(name: str, *, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    """Proposed child spans: vector / BM25 / MMR / pack.assemble."""
    tracer = get_tracer()
    if tracer is None:
        yield _NullSpan()
        return
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for k, v in attributes.items():
                span.set_attribute(k, v)
        yield span


def record_duration_ms(span: Any, key: str, duration_ms: float) -> None:
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute(key, float(duration_ms))


def record_search_counts(
    span: Any,
    *,
    vector_hits: int,
    bm25_hits: int,
    mmr_selected: int,
) -> None:
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("search.vector_hits", vector_hits)
    span.set_attribute("search.bm25_hits", bm25_hits)
    span.set_attribute("search.mmr_selected", mmr_selected)


class _NullSpan:
    def set_attribute(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def record_exception(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def set_status(self, *_args: Any, **_kwargs: Any) -> None:
        return None
