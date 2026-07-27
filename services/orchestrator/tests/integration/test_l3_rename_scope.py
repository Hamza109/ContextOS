"""Integration: Serena-backed rename-scope analysis (T048; SC-005). Analysis only."""

from __future__ import annotations

from app.adapters.serena_mcp import (
    InMemorySerenaDouble,
    SerenaMCPAdapter,
    SerenaMCPConfig,
    SerenaRenameScopePayload,
)
from app.services.l3_symbol import SymbolService


def test_rename_scope_analysis_fixture_symbol() -> None:
    session = InMemorySerenaDouble(
        rename_scopes={
            "Widget": SerenaRenameScopePayload(
                symbol_name="Widget",
                safe_scope_paths=["ui/widget.py", "tests/test_widget.py"],
                breaking_change_count=1,
                notes="1 external import may break",
            )
        }
    )
    svc = SymbolService(
        adapter=SerenaMCPAdapter(SerenaMCPConfig(use_test_double=True), session=session)
    )
    result = svc.analyze_rename_scope(path="ui/widget.py", line=1, symbol="Widget")
    assert result.symbol_name == "Widget"
    assert "ui/widget.py" in result.safe_scope_paths
    assert result.breaking_change_count == 1
    assert result.execution_supported is False
