"""Proposed L4 CompressionService (EP-008 / US-023 + US-022).

Pipeline: score → summarize low-relevance → budget enforce → re-estimate tokens.
Reuses ``estimate_tokens`` from l5_pack. Metrics keys map to Confirmed /context fields
when L4 is enabled (pre-L4 vs post-L4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping
from xml.sax.saxutils import escape

from app.adapters.headroom_summarizer import filter_summarize_inputs, summarize_unit
from app.config import Settings, get_settings
from app.security.consent_gate import ConsentContext
from app.security.ignore_policy import path_is_hard_excluded
from app.services.l4_budgets import BudgetOutcome, enforce_budget
from app.services.l4_relevance import RelevanceUnit, ScoredUnit, score_units
from app.services.l5_pack import estimate_tokens
from app.services.l5_phase_pack import phase_role
from app.services.l5_search import SearchHit

_FILE_BLOCK = re.compile(
    r'(<file\s+[^>]*path=")([^"]+)("[\s\S]*?>)(.*?)(</file>)',
    re.DOTALL | re.IGNORECASE,
)
_CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)


@dataclass(frozen=True)
class CompressionResult:
    tokens_before: int
    tokens_after: int
    saving_percent: float
    final_context: str
    ratio: float
    provenance: dict[str, Any] = field(default_factory=dict)
    budget: BudgetOutcome | None = None
    scored_units: tuple[ScoredUnit, ...] = ()


class CompressionService:
    """Headroom-style compressor — Proposed adapter-backed implementation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def compress(
        self,
        *,
        final_context: str,
        hits: list[SearchHit] | None = None,
        phase: str = "Dev",
        query: str = "",
        phase_budgets: Mapping[str, int] | None = None,
        consent: ConsentContext | None = None,
        prefer_external: bool = False,
    ) -> CompressionResult:
        """Compress assembled pack body; return L4-meaningful token metrics."""
        tokens_before = estimate_tokens(final_context) if final_context.strip() else 0
        units, parse_excluded = self._units_from_context_or_hits(
            final_context, hits or [], phase=phase
        )

        # Never feed IgnorePolicy-excluded paths into summarizer input.
        raw_pairs = [(u.path, u.content) for u in units]
        kept, filter_excluded = filter_summarize_inputs(raw_pairs)
        excluded = list(dict.fromkeys([*parse_excluded, *filter_excluded]))
        kept_paths = {p for p, _ in kept}
        units = [u for u in units if u.path in kept_paths]

        scored = score_units(units)
        threshold = float(self.settings.l4_relevance_summarize_threshold)
        summarized: list[ScoredUnit] = []
        summarize_notes: list[dict[str, Any]] = []

        for unit in scored:
            aggressive = unit.score <= threshold
            if aggressive:
                result = summarize_unit(
                    unit.path,
                    unit.content,
                    aggressive=True,
                    consent=consent,
                    prefer_external=prefer_external,
                )
                summarize_notes.append(
                    {
                        "path": unit.path,
                        "mode": result.mode,
                        "preserved_lines": result.preserved_lines,
                        "dropped_lines": result.dropped_lines,
                        "score": unit.score,
                    }
                )
                summarized.append(
                    ScoredUnit(
                        path=unit.path,
                        content=result.content,
                        score=unit.score,
                        phase_role=unit.phase_role,
                        reasons=unit.reasons + (f"summarized:{result.mode}",),
                        hit_score=unit.hit_score,
                        recency=unit.recency,
                    )
                )
            else:
                summarized.append(unit)

        budgets = phase_budgets if phase_budgets is not None else self.settings.phase_budgets
        budget = enforce_budget(summarized, phase=phase, phase_budgets=budgets)

        compressed = self._rebuild_context(
            final_context,
            {u.path: u.content for u in budget.units},
            retained_paths={u.path for u in budget.units},
        )
        tokens_after = estimate_tokens(compressed) if compressed.strip() else 0
        if tokens_before > 0:
            saving = max(0.0, (tokens_before - tokens_after) / tokens_before * 100.0)
            ratio = tokens_after / tokens_before
        else:
            saving = 0.0
            ratio = 1.0

        provenance: dict[str, Any] = {
            "algorithm": "proposed_headroom_local_heuristic",
            "phase": phase,
            "query_present": bool(query),
            "excluded_paths": excluded,
            "summarize": summarize_notes,
            "budget_status": budget.status,
            "budget_steps": list(budget.steps),
            "pruned_paths": list(budget.pruned_paths),
            # Security note: no secret bodies — paths/modes/counts only (T032).
        }

        return CompressionResult(
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            saving_percent=round(saving, 4),
            final_context=compressed,
            ratio=round(ratio, 6),
            provenance=provenance,
            budget=budget,
            scored_units=tuple(budget.units),
        )

    def _units_from_context_or_hits(
        self,
        final_context: str,
        hits: list[SearchHit],
        *,
        phase: str,
    ) -> tuple[list[RelevanceUnit], list[str]]:
        hit_by_path = {h.path: h for h in hits}
        units: list[RelevanceUnit] = []
        excluded: list[str] = []

        for match in _FILE_BLOCK.finditer(final_context or ""):
            path = match.group(2)
            if path_is_hard_excluded(path):
                excluded.append(path)
                continue
            inner = match.group(4)
            cdata = _CDATA.search(inner)
            content = cdata.group(1) if cdata else inner.strip()
            hit = hit_by_path.get(path)
            score = float(hit.score) if hit else 0.0
            # Optional recency: only if SearchHit somehow carried it — currently absent → omit.
            recency = None
            if hit is not None and hasattr(hit, "recency"):
                recency = getattr(hit, "recency", None)
            role = phase_role(hit, phase) if hit is not None else "implementation"
            units.append(
                RelevanceUnit(
                    path=path,
                    content=content,
                    hit_score=score,
                    phase_role=role,
                    recency=recency,
                )
            )

        if units or excluded:
            # Also mark excluded hits not present in XML
            for hit in hits:
                if path_is_hard_excluded(hit.path) and hit.path not in excluded:
                    excluded.append(hit.path)
            return units, excluded

        # Fallback: hits only (no parseable file blocks).
        for hit in hits:
            if path_is_hard_excluded(hit.path):
                excluded.append(hit.path)
                continue
            units.append(
                RelevanceUnit(
                    path=hit.path,
                    content=hit.content or "",
                    hit_score=float(hit.score),
                    phase_role=phase_role(hit, phase),
                )
            )
        return units, excluded

    def _rebuild_context(
        self,
        original: str,
        content_by_path: dict[str, str],
        *,
        retained_paths: set[str],
    ) -> str:
        if not original.strip():
            # Rebuild minimal pack from retained units.
            parts = ['<?xml version="1.0" encoding="UTF-8"?>', "<context_pack l4=\"true\">"]
            for path, content in content_by_path.items():
                parts.append(f'<file path="{escape(path)}">')
                parts.append(f"<![CDATA[{_safe_cdata(content)}]]>")
                parts.append("</file>")
            parts.append("</context_pack>")
            return "\n".join(parts)

        def _replace(match: re.Match[str]) -> str:
            path = match.group(2)
            if path not in retained_paths:
                return ""  # pruned
            if path not in content_by_path:
                return match.group(0)
            new_content = content_by_path[path]
            prefix = match.group(1) + path + match.group(3)
            # Preserve surrounding structure; replace CDATA or whole inner.
            inner = match.group(4)
            if _CDATA.search(inner):
                new_inner = _CDATA.sub(
                    lambda _m: f"<![CDATA[{_safe_cdata(new_content)}]]>",
                    inner,
                    count=1,
                )
            else:
                new_inner = f"<![CDATA[{_safe_cdata(new_content)}]]>"
            return prefix + new_inner + match.group(5)

        rebuilt = _FILE_BLOCK.sub(_replace, original)
        # Collapse excessive blank lines from pruned files
        rebuilt = re.sub(r"\n{3,}", "\n\n", rebuilt)
        return rebuilt


def _safe_cdata(text: str) -> str:
    return (text or "").replace("]]>", "]]]]><![CDATA[>")


def saving_percent(tokens_before: int, tokens_after: int) -> float:
    """Shared savings math helper for telemetry/tests."""
    if tokens_before <= 0:
        return 0.0
    return round(max(0.0, (tokens_before - tokens_after) / tokens_before * 100.0), 4)


def compression_ratio(tokens_before: int, tokens_after: int) -> float:
    if tokens_before <= 0:
        return 1.0
    return round(tokens_after / tokens_before, 6)
