"""Unit: OTel-compatible compression attrs (EP-008 T027). Exporter vendor not asserted (OQ-09)."""

from __future__ import annotations

from app.telemetry.compression import (
    get_last_compression_event,
    record_compression_attributes,
    reset_last_compression_event,
)


class _RecordingSpan:
    def __init__(self) -> None:
        self.attrs: dict = {}

    def set_attribute(self, key: str, value) -> None:
        self.attrs[key] = value


def test_otel_attrs_emitted() -> None:
    reset_last_compression_event()
    span = _RecordingSpan()
    attrs = record_compression_attributes(
        span,
        tokens_before=1000,
        tokens_after=250,
        recall_at_k=0.95,
        phase="Dev",
        budget_status="ok",
        enabled=True,
    )
    assert attrs["compression.ratio"] == 0.25
    assert attrs["compression.cost_saved"] == 750.0
    assert attrs["compression.recall_at_k"] == 0.95
    assert span.attrs["compression.ratio"] == 0.25
    event = get_last_compression_event()
    assert event is not None
    assert event.tokens_before == 1000


def test_telemetry_opt_out_skips_span_but_computes() -> None:
    reset_last_compression_event()
    span = _RecordingSpan()
    attrs = record_compression_attributes(
        span,
        tokens_before=100,
        tokens_after=40,
        enabled=False,
    )
    assert attrs["compression.ratio"] == 0.4
    assert span.attrs == {}
