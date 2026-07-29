"""Proposed Headroom-style adaptive summarizer adapter (EP-008 / US-023).

Primary path: local/heuristic extractive summarization preserving symbols/types/TODOs.
External LLM summarize only when ``consent_gate.evaluate_query_time_llm`` allows.
Never summarize IgnorePolicy-excluded paths (filter before summarize input).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Callable

from app.security.consent_gate import ConsentContext, ConsentDecision, evaluate_query_time_llm
from app.security.ignore_policy import path_is_hard_excluded

logger = logging.getLogger(__name__)

# Preserve: defs/classes, TODO/FIXME, type-ish lines, imports.
_PRESERVE_RE = re.compile(
    r"^\s*(?:"
    r"def\s+\w+|class\s+\w+|async\s+def\s+\w+"
    r"|import\s+|from\s+\S+\s+import"
    r"|@(?:\w+\.)?\w+"  # decorators
    r"|#\s*(?:TODO|FIXME|XXX|HACK)\b"
    r"|//\s*(?:TODO|FIXME|XXX|HACK)\b"
    r"|/\*\s*(?:TODO|FIXME)"
    r"|type\s+\w+\s*="
    r"|interface\s+\w+|enum\s+\w+|struct\s+\w+"
    r"|fn\s+\w+|func\s+\w+|public\s+(?:class|interface|enum)"
    r")",
    re.IGNORECASE,
)

_TODO_INLINE_RE = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b", re.IGNORECASE)


@dataclass(frozen=True)
class SummarizeResult:
    path: str
    content: str
    mode: str  # "local_heuristic" | "external_skipped" | "external" | "passthrough" | "excluded"
    preserved_lines: int
    dropped_lines: int


def filter_summarize_inputs(
    units: list[tuple[str, str]],
) -> tuple[list[tuple[str, str]], list[str]]:
    """Drop IgnorePolicy-excluded paths from summarize input (FR-011)."""
    kept: list[tuple[str, str]] = []
    excluded: list[str] = []
    for path, content in units:
        if path_is_hard_excluded(path):
            excluded.append(path)
            continue
        kept.append((path, content))
    return kept, excluded


def summarize_local(content: str, *, aggressive: bool = True) -> tuple[str, int, int]:
    """Heuristic extractive summary preserving symbols/types/TODOs.

    When aggressive (low relevance): keep preserve lines + short head.
    When not aggressive: keep preserve lines + larger head/tail.
    """
    lines = (content or "").splitlines()
    if not lines:
        return "", 0, 0

    preserve_idx: set[int] = set()
    for i, line in enumerate(lines):
        if _PRESERVE_RE.search(line) or _TODO_INLINE_RE.search(line):
            preserve_idx.add(i)

    if aggressive:
        head_n = min(4, len(lines))
        keep: set[int] = set(range(head_n)) | preserve_idx
    else:
        head_n = min(20, len(lines))
        tail_n = min(8, len(lines))
        keep = set(range(head_n)) | set(range(max(0, len(lines) - tail_n), len(lines))) | preserve_idx

    out_lines: list[str] = []
    for i, line in enumerate(lines):
        if i in keep:
            out_lines.append(line)

    # Ensure at least one preserve marker line survives when present.
    if preserve_idx and not any(i in keep for i in preserve_idx):
        for i in sorted(preserve_idx):
            out_lines.append(lines[i])

    preserved = len(preserve_idx)
    dropped = max(0, len(lines) - len(out_lines))
    summary = "\n".join(out_lines)
    if aggressive and summary.strip():
        summary = f"[L4_SUMMARY]\n{summary}"
    return summary, preserved, dropped


def summarize_unit(
    path: str,
    content: str,
    *,
    aggressive: bool = True,
    consent: ConsentContext | None = None,
    prefer_external: bool = False,
    external_summarizer: Callable[[str, str], str] | None = None,
) -> SummarizeResult:
    """Summarize one unit. External path requires consent; else local heuristic."""
    if path_is_hard_excluded(path):
        return SummarizeResult(
            path=path,
            content="",
            mode="excluded",
            preserved_lines=0,
            dropped_lines=0,
        )

    if prefer_external:
        ctx = consent or ConsentContext()
        decision = evaluate_query_time_llm(ctx)
        if decision == ConsentDecision.ALLOW_EXTERNAL_PACKED_CONTEXT_ONLY and external_summarizer:
            try:
                out = external_summarizer(path, content)
                return SummarizeResult(
                    path=path,
                    content=out,
                    mode="external",
                    preserved_lines=0,
                    dropped_lines=0,
                )
            except Exception:  # noqa: BLE001
                logger.warning("external summarizer failed; falling back to local", exc_info=True)
        else:
            # No silent exfil — local path only.
            logger.info(
                "external summarize skipped (consent=%s); using local heuristic",
                decision.value,
            )
            text, preserved, dropped = summarize_local(content, aggressive=aggressive)
            return SummarizeResult(
                path=path,
                content=text,
                mode="external_skipped",
                preserved_lines=preserved,
                dropped_lines=dropped,
            )

    text, preserved, dropped = summarize_local(content, aggressive=aggressive)
    return SummarizeResult(
        path=path,
        content=text,
        mode="local_heuristic",
        preserved_lines=preserved,
        dropped_lines=dropped,
    )


def may_call_external_summarizer(consent: ConsentContext) -> bool:
    """True only when consent gate allows external packed/compressed transmission."""
    return evaluate_query_time_llm(consent) == ConsentDecision.ALLOW_EXTERNAL_PACKED_CONTEXT_ONLY
