"""Telemetry smoke for L3 spans (T034/T045/T053/T068/T077) — exporter vendor open."""

from __future__ import annotations

from app.adapters.serena_mcp import InMemorySerenaDouble, SerenaMCPAdapter, SerenaMCPConfig
from app.services.l3_symbol import SymbolService
from app.telemetry import symbol as symbol_tel


def test_symbol_spans_noop_without_exporter() -> None:
    """Spans must not raise when OTel exporter unset (NullSpan path)."""
    with symbol_tel.symbol_span("symbol.definition", attributes={"path": "a.py"}):
        pass
    svc = SymbolService(
        adapter=SerenaMCPAdapter(
            SerenaMCPConfig(use_test_double=True), session=InMemorySerenaDouble()
        )
    )
    svc.get_definition(path="a.py", line=1, symbol="x")
    svc.find_references(path="a.py", line=1, symbol="x")
    svc.analyze_rename_scope(path="a.py", line=1, symbol="x")
    svc.compose_safe_edit_plan(path="a.py", line=1, symbol="x", query="x")
