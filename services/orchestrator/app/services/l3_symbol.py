"""L3 SymbolService — definition / references / rename-scope / hover / safe-edit (Proposed).

Used when the orchestrator needs symbols (Pack Context enrichment per ADR-005).
No Confirmed REST exposure (FR-012; OQ-Symbol-REST — MCP-first Option A).

Security: reuse ignore_policy + consent_gate from EP-001 — do NOT invent a second ignore
engine (FR-013; T014). RBAC hook reserved — OQ-01 Missing Evidence.

OQ notes (Proposed only — do not Confirmed-freeze):
- OQ-12: 99% accuracy measure blocked — no Pass invent
- OQ-Lang-Set: Proposed fixture subset via PROPOSED_FIXTURE_LANGUAGES
- OQ-Unresolved-Symbol: no/partial definition; no L1 blast expand
- OQ-Safe-Edit-Shape: delimited text block interim — not Confirmed JSON schema
- OQ-MCP-Fallback: clear SerenaUnavailableError; optional regex labeled Proposed/degraded
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.adapters.serena_mcp import (
    PROPOSED_FIXTURE_LANGUAGES,
    SerenaDefinitionPayload,
    SerenaHoverPayload,
    SerenaMCPAdapter,
    SerenaMCPConfig,
    SerenaReferencePayload,
    SerenaRenameScopePayload,
    SerenaUnavailableError,
    SerenaUnsupportedLanguageError,
    enrich_reference_context,
)
from app.config import Settings, get_settings
from app.security.consent_gate import ConsentContext, evaluate_query_time_llm
from app.security.ignore_policy import IgnorePolicy
from app.telemetry.symbol import (
    record_duration_ms,
    symbol_span,
)

logger = logging.getLogger(__name__)

# Confirmed FR-05 call-site window
REFERENCE_CONTEXT_LINES = 2

# Proposed safe-edit interim markers (OQ-Safe-Edit-Shape) — behavioral discriminator only.
SAFE_EDIT_BEGIN = "<!-- CONTEXTOS_SAFE_EDIT_PLAN_PROPOSED begin -->"
SAFE_EDIT_END = "<!-- CONTEXTOS_SAFE_EDIT_PLAN_PROPOSED end -->"


@dataclass(frozen=True)
class DefinitionResult:
    """Mapped definition attributes (FR-001) — not Confirmed REST schema."""

    path: str
    line: int
    file_line: str
    signature: str | None = None
    docstring: str | None = None
    column: int | None = None
    unresolved: bool = False
    partial: bool = False
    message: str | None = None


@dataclass(frozen=True)
class ReferenceHit:
    """Reference with ±2 line context (FR-004/FR-005)."""

    path: str
    line: int
    file_line: str
    context_before: list[str] = field(default_factory=list)
    context_after: list[str] = field(default_factory=list)
    line_text: str | None = None
    column: int | None = None


@dataclass(frozen=True)
class HoverDocs:
    """Hover/docs passthrough (FR-014) — no invented undocumented fields."""

    contents: str
    path: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class RenameScopeAnalysis:
    """Safe scope + breaking-change count (FR-006). Analysis only — no execute (FR-007)."""

    symbol_name: str
    safe_scope_paths: list[str]
    breaking_change_count: int
    notes: str | None = None
    execution_supported: bool = False  # Always False in ContextOS MVP (BRD §6)


@dataclass(frozen=True)
class SafeEditPlan:
    """Proposed interim safe edit plan (OQ-Safe-Edit-Shape).

    Behavioral: symbol-scoped guidance — MUST NOT be a “rewrite entire file” directive.
    Machine JSON schema Not evidenced — do not invent Confirmed Appendix D fields.
    """

    symbol_name: str | None
    guidance_text: str
    definition_file_line: str | None = None
    reference_count: int = 0
    breaking_change_count: int = 0
    markers_ok: bool = True


def map_definition(payload: SerenaDefinitionPayload) -> DefinitionResult:
    """Map Serena definition payload → Definition Result attributes (T025/T030)."""
    file_line = f"{payload.path}:{payload.line}"
    return DefinitionResult(
        path=payload.path,
        line=payload.line,
        file_line=file_line,
        signature=payload.signature,
        docstring=payload.docstring,
        column=payload.column,
        unresolved=payload.unresolved,
        partial=payload.partial,
        message=payload.message,
    )


def map_hover(payload: SerenaHoverPayload) -> HoverDocs:
    """Map hover without inventing undocumented schema fields (T026/T031)."""
    return HoverDocs(contents=payload.contents, path=payload.path, line=payload.line)


def map_reference(payload: SerenaReferencePayload) -> ReferenceHit:
    return ReferenceHit(
        path=payload.path,
        line=payload.line,
        file_line=f"{payload.path}:{payload.line}",
        context_before=list(payload.context_before),
        context_after=list(payload.context_after),
        line_text=payload.line_text,
        column=payload.column,
    )


def map_rename_scope(payload: SerenaRenameScopePayload) -> RenameScopeAnalysis:
    count = max(0, int(payload.breaking_change_count))
    return RenameScopeAnalysis(
        symbol_name=payload.symbol_name,
        safe_scope_paths=list(payload.safe_scope_paths),
        breaking_change_count=count,
        notes=payload.notes,
        execution_supported=False,
    )


def filter_references_by_file_type(
    refs: list[ReferenceHit],
    file_types: list[str] | None,
) -> list[ReferenceHit]:
    """Filter by extension/suffix (FR-005). Empty filtered set is conceptually valid (T036).

    Exact empty-result contract Not evidenced — return ``[]`` without inventing schema.
    """
    if not file_types:
        return list(refs)
    suffixes = {_normalize_suffix(t) for t in file_types}
    out: list[ReferenceHit] = []
    for ref in refs:
        path_suffix = Path(ref.path).suffix.lower()
        if path_suffix in suffixes or path_suffix.lstrip(".") in {
            s.lstrip(".") for s in suffixes
        }:
            out.append(ref)
    return out


def _normalize_suffix(token: str) -> str:
    t = token.strip().lower()
    if not t:
        return t
    if not t.startswith("."):
        t = f".{t}"
    return t


def ensure_reference_window(hit: ReferenceHit, window: int = REFERENCE_CONTEXT_LINES) -> bool:
    """Assert behavioral window sizes for tests (≤ window lines each side)."""
    return len(hit.context_before) <= window and len(hit.context_after) <= window


def format_safe_edit_plan_block(plan: SafeEditPlan) -> str:
    """Proposed interim delimited block for embedding in/alongside final_context.

    Does **not** add Confirmed Appendix D response fields — content lives in the
    Confirmed ``final_context`` string only (T054/T065).
    """
    lines = [
        SAFE_EDIT_BEGIN,
        "# Safe edit plan (Proposed interim — OQ-Safe-Edit-Shape open)",
        "# Intent: symbol-scoped edits — NOT a rewrite-entire-file directive",
        f"symbol: {plan.symbol_name or '(unresolved)'}",
    ]
    if plan.definition_file_line:
        lines.append(f"definition: {plan.definition_file_line}")
    lines.append(f"references: {plan.reference_count}")
    lines.append(f"breaking_change_count: {plan.breaking_change_count}")
    lines.append("guidance:")
    for gline in plan.guidance_text.strip().splitlines() or ["(no guidance)"]:
        lines.append(f"  {gline}")
    lines.append(SAFE_EDIT_END)
    return "\n".join(lines)


def attach_safe_edit_plan(final_context: str, plan: SafeEditPlan) -> str:
    """Append Proposed safe-edit block to packed context without new response keys."""
    block = format_safe_edit_plan_block(plan)
    if SAFE_EDIT_BEGIN in final_context:
        return final_context
    return f"{final_context.rstrip()}\n\n{block}\n"


def is_symbol_scoped_plan(text: str) -> bool:
    """Behavioral discriminator: markers present and no whole-file rewrite directive."""
    if SAFE_EDIT_BEGIN not in text or SAFE_EDIT_END not in text:
        return False
    lowered = text.lower()
    start = lowered.find(SAFE_EDIT_BEGIN.lower())
    end = lowered.find(SAFE_EDIT_END.lower())
    section = lowered[start:end] if start >= 0 and end > start else lowered
    # Affirmative whole-file rewrite directive (not our negation guidance)
    if re.search(
        r"(?:^|\n)\s*(?:#\s*)?(?:please\s+)?rewrite entire file\b",
        section,
    ) and not re.search(r"\b(?:do not|don't|not a)\b.{0,40}rewrite entire file", section):
        return False
    return "symbol-scoped" in section or "symbol:" in section


def build_safe_edit_plan_from_signals(
    *,
    symbol: str | None,
    definition: DefinitionResult | None,
    references: list[ReferenceHit],
    rename: RenameScopeAnalysis | None,
) -> SafeEditPlan:
    """Compose Serena-informed safe edit guidance (behavioral FR-008)."""
    def_fl = definition.file_line if definition and not definition.unresolved else None
    break_n = rename.breaking_change_count if rename else 0
    scope = rename.safe_scope_paths if rename else [r.path for r in references]
    guidance_parts = [
        "Prefer edits limited to the resolved symbol and its reference sites.",
        "Review rename-scope analysis before applying any rename outside ContextOS.",
        "Do not rewrite entire files; change only symbol-scoped call sites and definition.",
    ]
    if def_fl:
        guidance_parts.insert(0, f"Anchor edits at definition {def_fl}.")
    if scope:
        guidance_parts.append(f"Safe scope paths ({len(scope)}): " + ", ".join(scope[:20]))
    if break_n:
        guidance_parts.append(
            f"Breaking-change count={break_n}: review dependents before rename execution elsewhere."
        )
    return SafeEditPlan(
        symbol_name=symbol,
        guidance_text="\n".join(guidance_parts),
        definition_file_line=def_fl,
        reference_count=len(references),
        breaking_change_count=break_n,
        markers_ok=True,
    )


class SymbolService:
    """Orchestrator SymbolService (FR-04..06) — Pack Context enrichment entrypoint."""

    def __init__(
        self,
        adapter: SerenaMCPAdapter | None = None,
        *,
        settings: Settings | None = None,
        ignore_policy: IgnorePolicy | None = None,
        workspace_root: Path | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.adapter = adapter or SerenaMCPAdapter(
            SerenaMCPConfig(
                enabled=self.settings.serena_enabled,
                command=self.settings.serena_command,
                args=[a for a in (self.settings.serena_args or "").split() if a],
                cwd=self.settings.serena_cwd,
                timeout_seconds=self.settings.serena_timeout_seconds,
                use_test_double=self.settings.serena_use_test_double,
            )
        )
        self.workspace_root = workspace_root
        # Reuse EP-001 IgnorePolicy when workspace known — never invent a second engine (T014).
        if ignore_policy is not None:
            self.ignore_policy: IgnorePolicy | None = ignore_policy
        elif workspace_root is not None:
            self.ignore_policy = IgnorePolicy.from_repo(workspace_root)
        else:
            self.ignore_policy = None
        # OQ-01: RBAC/authn hook reserved — Missing Evidence; local MCP loopback MAY apply.
        # if not rbac_allows(actor, repo): raise PermissionError(...)

    def _consent_note(self) -> None:
        """Reuse consent_gate evaluation — L3 must not invent a second consent engine."""
        ctx = ConsentContext(
            external_llm_consent=self.settings.external_llm_consent,
            local_inference_configured=bool(self.settings.local_inference_enabled),
        )
        # Symbol ops are local Serena MCP — not external LLM. Still call gate for inheritance.
        _ = evaluate_query_time_llm(ctx)

    def _check_path_allowed(self, path: str) -> None:
        """Inherit EP-001 ignore — do not walk .env/secrets via 'helpful' reads (T072)."""
        p = Path(path)
        check = p
        if self.workspace_root is not None and not p.is_absolute():
            check = self.workspace_root / p
        name = check.name
        if name.startswith(".env") or name.endswith(".pem") or name.endswith(".key"):
            raise PermissionError(
                f"path excluded by ignore/secrets policy (EP-001 inheritance): {path}"
            )
        if self.ignore_policy is not None and self.ignore_policy.is_excluded(check):
            raise PermissionError(f"path excluded by ignore_policy: {path}")

    def _read_file_lines(self, path: str) -> list[str] | None:
        try:
            self._check_path_allowed(path)
        except PermissionError:
            logger.warning("skip context read for excluded path: %s", path)
            return None
        root = self.workspace_root
        candidate = Path(path)
        if root is not None and not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.is_file():
            return None
        try:
            return candidate.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None

    def get_definition(
        self,
        *,
        path: str,
        line: int,
        column: int = 0,
        symbol: str | None = None,
        language: str | None = None,
    ) -> DefinitionResult:
        self._consent_note()
        with symbol_span(
            "symbol.definition",
            attributes={"path": path, "line": line, "symbol": symbol or ""},
        ) as span:
            import time

            t0 = time.perf_counter()
            try:
                if language and language.lower() not in {
                    x.lower() for x in self.adapter.supported_languages()
                }:
                    # Unsupported language — clear no/partial (T035); Proposed UX only.
                    result = DefinitionResult(
                        path=path,
                        line=line,
                        file_line=f"{path}:{line}",
                        unresolved=True,
                        partial=True,
                        message=(
                            f"unsupported language '{language}' "
                            f"(Proposed fixture subset / OQ-Lang-Set open)"
                        ),
                    )
                    record_duration_ms(span, "duration_ms", (time.perf_counter() - t0) * 1000)
                    return result
                payload = self.adapter.find_definition(
                    path=path, line=line, column=column, symbol=symbol
                )
                result = map_definition(payload)
                record_duration_ms(span, "duration_ms", (time.perf_counter() - t0) * 1000)
                return result
            except SerenaUnavailableError:
                record_duration_ms(span, "duration_ms", (time.perf_counter() - t0) * 1000)
                raise

    def get_hover(
        self,
        *,
        path: str,
        line: int,
        column: int = 0,
        symbol: str | None = None,
    ) -> HoverDocs:
        self._consent_note()
        with symbol_span("symbol.hover", attributes={"path": path, "line": line}):
            payload = self.adapter.hover(
                path=path, line=line, column=column, symbol=symbol
            )
            return map_hover(payload)

    def find_references(
        self,
        *,
        path: str,
        line: int,
        column: int = 0,
        symbol: str | None = None,
        file_types: list[str] | None = None,
    ) -> list[ReferenceHit]:
        self._consent_note()
        with symbol_span(
            "symbol.references",
            attributes={"path": path, "line": line, "symbol": symbol or ""},
        ) as span:
            import time

            t0 = time.perf_counter()
            raw = self.adapter.find_references(
                path=path, line=line, column=column, symbol=symbol
            )
            hits: list[ReferenceHit] = []
            for ref in raw:
                lines = self._read_file_lines(ref.path)
                enriched = enrich_reference_context(
                    ref, file_lines=lines, window=REFERENCE_CONTEXT_LINES
                )
                # If still empty and we have line_text only, pad empty windows (valid)
                hit = map_reference(enriched)
                hits.append(hit)
            filtered = filter_references_by_file_type(hits, file_types)
            record_duration_ms(span, "duration_ms", (time.perf_counter() - t0) * 1000)
            span.set_attribute("references.count", len(filtered))
            return filtered

    def analyze_rename_scope(
        self,
        *,
        path: str,
        line: int,
        column: int = 0,
        symbol: str | None = None,
    ) -> RenameScopeAnalysis:
        """Rename-scope **analysis only** — no execution sandbox (T046/T051)."""
        self._consent_note()
        with symbol_span(
            "symbol.rename_scope",
            attributes={"path": path, "line": line, "symbol": symbol or ""},
        ) as span:
            import time

            t0 = time.perf_counter()
            payload = self.adapter.rename_scope_analysis(
                path=path, line=line, column=column, symbol=symbol
            )
            result = map_rename_scope(payload)
            assert result.execution_supported is False
            record_duration_ms(span, "duration_ms", (time.perf_counter() - t0) * 1000)
            span.set_attribute("rename.breaking_change_count", result.breaking_change_count)
            return result

    def compose_safe_edit_plan(
        self,
        *,
        path: str | None,
        line: int | None = None,
        column: int = 0,
        symbol: str | None = None,
        query: str | None = None,
    ) -> SafeEditPlan | None:
        """Serena-informed safe edit plan for Pack Context enrichment (T065).

        Returns None when path/symbol insufficient or Serena unavailable (Proposed
        degraded — do not invent Confirmed fallback Pass).
        """
        with symbol_span(
            "symbol.pack_context.enrichment",
            attributes={"symbol": symbol or "", "path": path or ""},
        ):
            if not path or line is None:
                # Query-only Pack Context: Proposed minimal plan from query token
                sym = symbol or _guess_symbol(query)
                if not sym:
                    return None
                return SafeEditPlan(
                    symbol_name=sym,
                    guidance_text=(
                        "Prefer symbol-scoped edits for the queried symbol. "
                        "Resolve definition via Serena when file selection is available. "
                        "Do not rewrite entire files."
                    ),
                    reference_count=0,
                    breaking_change_count=0,
                )
            try:
                definition = self.get_definition(
                    path=path, line=line, column=column, symbol=symbol
                )
                refs = self.find_references(
                    path=path, line=line, column=column, symbol=symbol
                )
                rename = self.analyze_rename_scope(
                    path=path, line=line, column=column, symbol=symbol
                )
            except SerenaUnavailableError as exc:
                logger.warning("safe edit enrichment skipped: %s", exc)
                return None
            except SerenaUnsupportedLanguageError:
                return None
            sym = symbol or (definition.signature.split("(")[0] if definition.signature else None)
            return build_safe_edit_plan_from_signals(
                symbol=sym,
                definition=definition,
                references=refs,
                rename=rename,
            )


def _guess_symbol(query: str | None) -> str | None:
    if not query:
        return None
    # Proposed heuristic — not Confirmed symbol extraction
    m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", query)
    return m.group(1) if m else None


def proposed_fixture_languages() -> frozenset[str]:
    """Proposed AC fixture language subset (T007/T022) — OQ-Lang-Set remains open."""
    return PROPOSED_FIXTURE_LANGUAGES
