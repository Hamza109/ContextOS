"""OpenTelemetry-compatible indexing helpers (exporter-agnostic; OQ-OTEL open)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.trace import Span, Status, StatusCode
except ImportError:  # pragma: no cover - SDK listed in deps; fallback for isolation
    trace = None  # type: ignore
    Span = Any  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore


def get_tracer(name: str = "contextos.indexing"):
    if trace is None:
        return None
    return trace.get_tracer(name)


@contextmanager
def index_span(
    name: str = "index.repository",
    *,
    repo_name: str | None = None,
    mode: str = "full",
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Create an OTel span for indexing; no-ops safely if SDK/exporter unset."""
    tracer = get_tracer()
    attrs: dict[str, Any] = {"index.mode": mode}
    if repo_name:
        attrs["repo_name"] = repo_name
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


def record_index_counts(
    span: Any,
    *,
    files_indexed: int,
    embeddings: int,
    graph_nodes: int,
    time_ms: int,
    exclusions: int | None = None,
) -> None:
    """Align span attributes to confirmed POST /index response fields."""
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("files_indexed", files_indexed)
    span.set_attribute("embeddings", embeddings)
    span.set_attribute("graph_nodes", graph_nodes)
    span.set_attribute("time_ms", time_ms)
    if exclusions is not None:
        # Exclusion counts only — never secret file contents
        span.set_attribute("files_excluded", exclusions)


def record_pack_attributes(
    span: Any, *, token_count: int, files_packed: int, exclusions: int
) -> None:
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("pack.token_count", token_count)
    span.set_attribute("pack.files", files_packed)
    span.set_attribute("pack.exclusions", exclusions)


def record_l1_attributes(
    span: Any,
    *,
    parse_ms: int,
    persist_ms: int,
    parsed_files: int,
    graph_nodes: int,
    unsupported_files: int,
    malformed_files: int,
) -> None:
    """Record aggregate L1 measurements only; never paths or source content."""
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("l1.parse_ms", parse_ms)
    span.set_attribute("l1.persist_ms", persist_ms)
    span.set_attribute("l1.parsed_files", parsed_files)
    span.set_attribute("l1.graph_nodes", graph_nodes)
    span.set_attribute("l1.unsupported_files", unsupported_files)
    span.set_attribute("l1.malformed_files", malformed_files)


def record_okf_attributes(
    span: Any,
    *,
    status: str,
    concepts_written: int,
    sources_used: int,
    duration_ms: int,
) -> None:
    """Record Proposed OKF generate counts/timings/status only — never content."""
    if span is None or isinstance(span, _NullSpan):
        return
    span.set_attribute("okf.status", status)
    span.set_attribute("okf.concepts_written", concepts_written)
    span.set_attribute("okf.sources_used", sources_used)
    span.set_attribute("okf.duration_ms", duration_ms)


class _NullSpan:
    def set_attribute(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def record_exception(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def set_status(self, *_args: Any, **_kwargs: Any) -> None:
        return None
