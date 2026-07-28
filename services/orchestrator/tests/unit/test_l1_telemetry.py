from __future__ import annotations

from app.telemetry.indexing import record_l1_attributes


class Span:
    def __init__(self) -> None:
        self.attributes: dict[str, int] = {}

    def set_attribute(self, key: str, value: int) -> None:
        self.attributes[key] = value


def test_l1_telemetry_contains_counts_and_timings_only() -> None:
    span = Span()
    record_l1_attributes(
        span,
        parse_ms=3,
        persist_ms=4,
        parsed_files=5,
        graph_nodes=6,
        unsupported_files=1,
        malformed_files=1,
    )
    assert span.attributes["l1.graph_nodes"] == 6
    assert not any("path" in key or "source" in key or "content" in key for key in span.attributes)
