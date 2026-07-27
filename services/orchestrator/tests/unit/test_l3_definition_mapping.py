"""Unit: Serena payload → Definition Result attributes (T025).

No invented Confirmed REST schema asserts (FR-001; SC-001).
"""

from __future__ import annotations

from app.adapters.serena_mcp import SerenaDefinitionPayload
from app.services.l3_symbol import DefinitionResult, map_definition


def test_map_definition_file_line_signature_docstring() -> None:
    payload = SerenaDefinitionPayload(
        path="src/auth.py",
        line=42,
        signature="def login(user: str) -> Token",
        docstring="Authenticate a user and return a token.",
        column=4,
    )
    result = map_definition(payload)
    assert isinstance(result, DefinitionResult)
    assert result.path == "src/auth.py"
    assert result.line == 42
    assert result.file_line == "src/auth.py:42"
    assert result.signature == "def login(user: str) -> Token"
    assert result.docstring == "Authenticate a user and return a token."
    assert result.unresolved is False


def test_map_definition_unresolved_partial() -> None:
    payload = SerenaDefinitionPayload(
        path="a.py",
        line=1,
        unresolved=True,
        partial=True,
        message="no definition found",
    )
    result = map_definition(payload)
    assert result.unresolved is True
    assert result.partial is True
    assert result.file_line == "a.py:1"
    assert result.signature is None
