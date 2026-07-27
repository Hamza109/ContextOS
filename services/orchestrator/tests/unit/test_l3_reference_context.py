"""Unit: reference call-site context window = 2 before + 2 after (T037; FR-004)."""

from __future__ import annotations

from app.adapters.serena_mcp import SerenaReferencePayload, enrich_reference_context
from app.services.l3_symbol import REFERENCE_CONTEXT_LINES, ensure_reference_window, map_reference


def test_enrich_reference_context_window_is_two() -> None:
    assert REFERENCE_CONTEXT_LINES == 2
    file_lines = [f"line{i}" for i in range(1, 11)]  # lines 1..10
    ref = SerenaReferencePayload(path="a.py", line=5, column=0)
    enriched = enrich_reference_context(ref, file_lines=file_lines, window=2)
    assert enriched.context_before == ["line3", "line4"]
    assert enriched.context_after == ["line6", "line7"]
    assert enriched.line_text == "line5"
    hit = map_reference(enriched)
    assert ensure_reference_window(hit, window=2)
    assert len(hit.context_before) == 2
    assert len(hit.context_after) == 2


def test_enrich_reference_near_file_edges() -> None:
    file_lines = ["only", "two"]
    ref = SerenaReferencePayload(path="b.py", line=1)
    enriched = enrich_reference_context(ref, file_lines=file_lines, window=2)
    assert enriched.context_before == []
    assert enriched.context_after == ["two"]
    assert len(enriched.context_after) <= 2
