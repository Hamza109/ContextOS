"""Unit: rename-scope analysis safe scope + breaking-change count (T047; FR-006).

Analysis only — execution_supported always False (FR-007; BRD §6).
"""

from __future__ import annotations

from app.adapters.serena_mcp import SerenaRenameScopePayload
from app.services.l3_symbol import map_rename_scope


def test_rename_scope_zero_breaking_valid() -> None:
    payload = SerenaRenameScopePayload(
        symbol_name="foo",
        safe_scope_paths=["a.py", "b.py"],
        breaking_change_count=0,
    )
    result = map_rename_scope(payload)
    assert result.symbol_name == "foo"
    assert result.safe_scope_paths == ["a.py", "b.py"]
    assert result.breaking_change_count == 0
    assert result.execution_supported is False


def test_rename_scope_nonzero_breaking() -> None:
    payload = SerenaRenameScopePayload(
        symbol_name="Bar",
        safe_scope_paths=["pkg/x.py"],
        breaking_change_count=3,
    )
    result = map_rename_scope(payload)
    assert result.breaking_change_count == 3
    assert result.execution_supported is False


def test_rename_scope_clamps_negative_to_zero() -> None:
    payload = SerenaRenameScopePayload(
        symbol_name="z",
        safe_scope_paths=[],
        breaking_change_count=-1,
    )
    assert map_rename_scope(payload).breaking_change_count == 0
