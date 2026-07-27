"""Serena MCP client adapter (Proposed — ADR-005).

Owns connection/session hooks for definition / references / hover / rename-scope.
Exact Serena SDK package pins: **NEEDS CLARIFICATION** (OQ / ADR-005 trade-off).

MVP transport: MCP-first Option A — this adapter is for **orchestrator** enrichment
(Pack Context / SymbolService). IDE FR-04..06 paths use extension MCP DX separately.
Do **not** expose Confirmed symbol REST (api-contract §3; OQ-Symbol-REST open).

OQ-MCP-Fallback: when unavailable, raise SerenaUnavailableError with a clear message;
optional regex fallback is Proposed only and must be labeled as degraded.
OQ-Lang-Set: language inventory beyond "12+" remains open — callers use Proposed fixture subset.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class SerenaUnavailableError(RuntimeError):
    """Proposed: MCP/Serena session unavailable (OQ-MCP-Fallback — clear error, not Confirmed UX)."""


class SerenaUnsupportedLanguageError(ValueError):
    """Proposed: language not in session capability set (OQ-Lang-Set open)."""


@dataclass(frozen=True)
class SymbolLocation:
    """Proposed location payload mapped from Serena — not a Confirmed REST schema."""

    path: str
    line: int
    column: int | None = None


@dataclass(frozen=True)
class SerenaDefinitionPayload:
    """Raw-ish Serena definition result before SymbolService attribute mapping."""

    path: str
    line: int
    signature: str | None = None
    docstring: str | None = None
    column: int | None = None
    language: str | None = None
    unresolved: bool = False
    partial: bool = False
    message: str | None = None


@dataclass(frozen=True)
class SerenaReferencePayload:
    path: str
    line: int
    column: int | None = None
    # Call-site lines as returned by Serena or filled by adapter from file read
    context_before: list[str] = field(default_factory=list)
    context_after: list[str] = field(default_factory=list)
    line_text: str | None = None


@dataclass(frozen=True)
class SerenaHoverPayload:
    """Hover/docs passthrough — do not invent undocumented fields beyond Serena content."""

    contents: str
    path: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class SerenaRenameScopePayload:
    """Rename-scope **analysis** only — no execute/apply (BRD §6; FR-007)."""

    symbol_name: str
    safe_scope_paths: list[str]
    breaking_change_count: int
    notes: str | None = None


class SerenaSession(Protocol):
    """Minimal session protocol — concrete SDK binding NEEDS CLARIFICATION."""

    def find_definition(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaDefinitionPayload: ...

    def find_references(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> list[SerenaReferencePayload]: ...

    def hover(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaHoverPayload: ...

    def rename_scope_analysis(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaRenameScopePayload: ...

    def supported_languages(self) -> frozenset[str]: ...

    def close(self) -> None: ...


# Proposed AC fixture language subset until OQ-Lang-Set inventory Confirmed (T007/T022).
PROPOSED_FIXTURE_LANGUAGES: frozenset[str] = frozenset({"python", "typescript", "javascript"})


@dataclass
class SerenaMCPConfig:
    """Proposed knobs — not Confirmed product freeze (config.py mirrors these)."""

    enabled: bool = True
    command: str | None = None
    args: list[str] = field(default_factory=list)
    cwd: str | None = None
    timeout_seconds: float = 30.0
    # When True, InMemorySerenaDouble is used (tests / degraded local without live MCP).
    use_test_double: bool = False


class InMemorySerenaDouble:
    """Test double for Serena MCP — fixtures only; not a production LSP.

    Seeded catalog supports Proposed fixture languages (python/ts/js).
    """

    def __init__(
        self,
        *,
        definitions: dict[str, SerenaDefinitionPayload] | None = None,
        references: dict[str, list[SerenaReferencePayload]] | None = None,
        hovers: dict[str, SerenaHoverPayload] | None = None,
        rename_scopes: dict[str, SerenaRenameScopePayload] | None = None,
        languages: frozenset[str] | None = None,
        available: bool = True,
    ) -> None:
        self._definitions = definitions or {}
        self._references = references or {}
        self._hovers = hovers or {}
        self._rename_scopes = rename_scopes or {}
        self._languages = languages or PROPOSED_FIXTURE_LANGUAGES
        self._available = available

    def _ensure(self) -> None:
        if not self._available:
            raise SerenaUnavailableError(
                "Serena MCP unavailable (Proposed clear error; OQ-MCP-Fallback open)"
            )

    def _key(self, path: str, line: int, symbol: str | None) -> str:
        return f"{path}:{line}:{symbol or ''}"

    def find_definition(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaDefinitionPayload:
        self._ensure()
        key = self._key(path, line, symbol)
        if key in self._definitions:
            return self._definitions[key]
        if symbol and symbol in self._definitions:
            return self._definitions[symbol]
        # Unresolved / ambiguous — Proposed no/partial (OQ-Unresolved-Symbol); no L1 expand.
        return SerenaDefinitionPayload(
            path=path,
            line=line,
            column=column,
            unresolved=True,
            partial=True,
            message="no definition found (Proposed unresolved; OQ-Unresolved-Symbol)",
        )

    def find_references(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> list[SerenaReferencePayload]:
        self._ensure()
        key = self._key(path, line, symbol)
        if key in self._references:
            return list(self._references[key])
        if symbol and symbol in self._references:
            return list(self._references[symbol])
        return []

    def hover(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaHoverPayload:
        self._ensure()
        key = self._key(path, line, symbol)
        if key in self._hovers:
            return self._hovers[key]
        if symbol and symbol in self._hovers:
            return self._hovers[symbol]
        return SerenaHoverPayload(contents="", path=path, line=line)

    def rename_scope_analysis(
        self, *, path: str, line: int, column: int, symbol: str | None = None
    ) -> SerenaRenameScopePayload:
        self._ensure()
        key = self._key(path, line, symbol)
        if key in self._rename_scopes:
            return self._rename_scopes[key]
        if symbol and symbol in self._rename_scopes:
            return self._rename_scopes[symbol]
        name = symbol or Path(path).stem
        return SerenaRenameScopePayload(
            symbol_name=name,
            safe_scope_paths=[path],
            breaking_change_count=0,
            notes="Proposed default analysis — zero breaking changes valid (FR-006)",
        )

    def supported_languages(self) -> frozenset[str]:
        return self._languages

    def close(self) -> None:
        return None


class SerenaMCPAdapter:
    """Orchestrator-side Serena MCP adapter.

    Live process launch is Proposed; when command unset or use_test_double, uses
    InMemorySerenaDouble (or raises SerenaUnavailableError if disabled).
    """

    def __init__(
        self,
        config: SerenaMCPConfig | None = None,
        *,
        session: SerenaSession | None = None,
    ) -> None:
        self.config = config or SerenaMCPConfig()
        self._session: SerenaSession | None = session
        self._owned_session = session is None

    def connect(self) -> SerenaSession:
        """Open or return an existing session.

        Exact SDK package/version pins: NEEDS CLARIFICATION — no invented pin.
        """
        if self._session is not None:
            return self._session
        if not self.config.enabled:
            raise SerenaUnavailableError(
                "Serena MCP disabled via Proposed config (CONTEXTOS_SERENA_ENABLED)"
            )
        if self.config.use_test_double or not self.config.command:
            # Proposed: no live command → test double / empty session for local/dev.
            # Production should set CONTEXTOS_SERENA_COMMAND when live Serena is available.
            logger.info(
                "Serena MCP: using InMemorySerenaDouble "
                "(command unset or use_test_double; live SDK pin NEEDS CLARIFICATION)"
            )
            self._session = InMemorySerenaDouble()
            return self._session
        # Live MCP stdio/SSE binding deferred — SDK pin open. Fail clearly rather than invent.
        raise SerenaUnavailableError(
            "Live Serena MCP SDK binding not configured "
            "(Proposed; package pin NEEDS CLARIFICATION). "
            "Set CONTEXTOS_SERENA_USE_TEST_DOUBLE=1 for fixture paths or provide session."
        )

    def close(self) -> None:
        if self._session is not None and self._owned_session:
            self._session.close()
        self._session = None

    def __enter__(self) -> SerenaMCPAdapter:
        self.connect()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # --- Convenience ops (delegate to session) ---

    def find_definition(
        self, *, path: str, line: int, column: int = 0, symbol: str | None = None
    ) -> SerenaDefinitionPayload:
        return self.connect().find_definition(
            path=path, line=line, column=column, symbol=symbol
        )

    def find_references(
        self, *, path: str, line: int, column: int = 0, symbol: str | None = None
    ) -> list[SerenaReferencePayload]:
        return self.connect().find_references(
            path=path, line=line, column=column, symbol=symbol
        )

    def hover(
        self, *, path: str, line: int, column: int = 0, symbol: str | None = None
    ) -> SerenaHoverPayload:
        return self.connect().hover(path=path, line=line, column=column, symbol=symbol)

    def rename_scope_analysis(
        self, *, path: str, line: int, column: int = 0, symbol: str | None = None
    ) -> SerenaRenameScopePayload:
        return self.connect().rename_scope_analysis(
            path=path, line=line, column=column, symbol=symbol
        )

    def supported_languages(self) -> frozenset[str]:
        return self.connect().supported_languages()


def enrich_reference_context(
    ref: SerenaReferencePayload,
    *,
    file_lines: list[str] | None,
    window: int = 2,
) -> SerenaReferencePayload:
    """Attach ±``window`` lines (Confirmed FR-05 behavior: 2 before + 2 after).

    If Serena already supplied context, preserve it. ``file_lines`` is 0-indexed text.
    """
    if file_lines is None:
        return ref
    idx = max(0, ref.line - 1)
    before = file_lines[max(0, idx - window) : idx]
    after = file_lines[idx + 1 : idx + 1 + window]
    line_text = file_lines[idx] if 0 <= idx < len(file_lines) else ref.line_text
    return SerenaReferencePayload(
        path=ref.path,
        line=ref.line,
        column=ref.column,
        context_before=list(before) if not ref.context_before else list(ref.context_before),
        context_after=list(after) if not ref.context_after else list(ref.context_after),
        line_text=line_text if line_text is not None else ref.line_text,
    )
