"""Unit: OKF indexing telemetry attributes (EP-013 T016)."""

from __future__ import annotations

from app.telemetry.indexing import _NullSpan, record_okf_attributes


class _RecordingSpan:
    def __init__(self) -> None:
        self.attrs: dict[str, object] = {}

    def set_attribute(self, key: str, value: object) -> None:
        self.attrs[key] = value


def test_record_okf_attributes_counts_only() -> None:
    span = _RecordingSpan()
    record_okf_attributes(
        span,
        status="ok",
        concepts_written=6,
        sources_used=6,
        duration_ms=12,
    )
    assert span.attrs == {
        "okf.status": "ok",
        "okf.concepts_written": 6,
        "okf.sources_used": 6,
        "okf.duration_ms": 12,
    }
    record_okf_attributes(
        _NullSpan(),
        status="error",
        concepts_written=0,
        sources_used=0,
        duration_ms=1,
    )
