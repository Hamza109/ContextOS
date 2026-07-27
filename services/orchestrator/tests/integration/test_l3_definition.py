"""Integration: definition lookup via Serena test double (T027; SC-001).

Proposed fixture language subset (python) — OQ-Lang-Set remains open (T022).
"""

from __future__ import annotations

from app.adapters.serena_mcp import (
    InMemorySerenaDouble,
    SerenaDefinitionPayload,
    SerenaMCPAdapter,
    SerenaMCPConfig,
)
from app.services.l3_symbol import SymbolService, proposed_fixture_languages


def test_definition_lookup_python_fixture() -> None:
    assert "python" in proposed_fixture_languages()
    session = InMemorySerenaDouble(
        definitions={
            "login": SerenaDefinitionPayload(
                path="auth.py",
                line=12,
                signature="def login(user: str) -> Token",
                docstring="Log the user in.",
                language="python",
            )
        }
    )
    svc = SymbolService(
        adapter=SerenaMCPAdapter(SerenaMCPConfig(use_test_double=True), session=session)
    )
    result = svc.get_definition(path="auth.py", line=12, symbol="login", language="python")
    assert result.file_line == "auth.py:12"
    assert result.signature is not None
    assert result.docstring is not None
    assert result.unresolved is False


def test_unsupported_language_returns_partial() -> None:
    svc = SymbolService(
        adapter=SerenaMCPAdapter(
            SerenaMCPConfig(use_test_double=True),
            session=InMemorySerenaDouble(),
        )
    )
    result = svc.get_definition(
        path="main.cobol", line=1, symbol="FOO", language="cobol"
    )
    assert result.unresolved is True
    assert result.partial is True
    assert "unsupported language" in (result.message or "")
