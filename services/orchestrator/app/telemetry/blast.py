"""OpenTelemetry-compatible blast/graph helpers (Proposed attrs; ADR-011 / OQ-OTEL)."""

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


def get_tracer(name: str = "contextos.blast"):
    if trace is None:
        return None
    return trace.get_tracer(name)


@contextmanager
def blast_span(
    name: str = "blast.request",
    *,
    repo: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
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
        for key, value in attrs.items():
            span.set_attribute(key, value)
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            if Status is not None and StatusCode is not None:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            span.record_exception(exc)
            raise


@contextmanager
def graph_span(
    name: str = "graph.html",
    *,
    repo: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    with blast_span(name, repo=repo, attributes=attributes) as span:
        yield span


def record_blast_attributes(
    span: Any,
    *,
    duration_ms: int,
    hop_depth: int,
    node_count: int,
    direct_count: int,
    transitive_count: int,
) -> None:
    """Proposed non-sensitive blast attrs — never paths or source bodies."""
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("blast.duration_ms", int(duration_ms))
    span.set_attribute("blast.hop_depth", int(hop_depth))
    span.set_attribute("blast.node_count", int(node_count))
    span.set_attribute("blast.direct_count", int(direct_count))
    span.set_attribute("blast.transitive_count", int(transitive_count))


def record_graph_attributes(
    span: Any,
    *,
    duration_ms: int,
    node_count: int,
    edge_count: int,
    depth: int,
) -> None:
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("graph.duration_ms", int(duration_ms))
    span.set_attribute("graph.node_count", int(node_count))
    span.set_attribute("graph.edge_count", int(edge_count))
    span.set_attribute("graph.depth", int(depth))


class _NullSpan:
    def set_attribute(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def record_exception(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def set_status(self, *_args: Any, **_kwargs: Any) -> None:
        return None
