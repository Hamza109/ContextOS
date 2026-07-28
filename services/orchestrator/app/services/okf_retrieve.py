"""Proposed OKF-first retrieval (EP-013 / US-047).

Exact + token-normalized match over concept id/title/tags/description.
Bounded markdown link expansion. Never fabricates concepts on miss.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from html import escape
from app.adapters.okf_bundle import (
    OkfBundle,
    OkfConcept,
    extract_markdown_links,
    okf_bundle_root,
)
from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "what",
        "where",
        "when",
        "how",
        "does",
        "about",
        "into",
        "over",
        "under",
    }
)


@dataclass(frozen=True)
class OkfRetrieveResult:
    status: str  # hit | miss | error | disabled | absent
    concepts: list[OkfConcept]
    duration_ms: int
    evidence_block: str
    matched_ids: list[str]


def retrieve_okf(
    repo: str,
    query: str,
    *,
    settings: Settings | None = None,
    bundle: OkfBundle | None = None,
) -> OkfRetrieveResult:
    """Lookup OKF concepts for a query; miss returns empty evidence (no fabrication)."""
    cfg = settings or get_settings()
    started = time.perf_counter()
    if not cfg.okf_enabled:
        return _empty("disabled", started)

    try:
        okf = bundle or OkfBundle(okf_bundle_root(cfg.okf_cache_dir, repo))
        if not okf.root.is_dir():
            return _empty("absent", started)
        concepts = okf.list_concepts()
        if not concepts:
            return _empty("miss", started)

        hits = _match_concepts(query, concepts)
        if not hits:
            return _empty("miss", started)

        expand_limit = int(cfg.okf_link_expand_limit)
        expanded = _expand_links(hits, concepts, limit=expand_limit)
        ordered = _dedupe_preserve(hits + expanded)
        block = _evidence_block(repo, ordered)
        return OkfRetrieveResult(
            status="hit",
            concepts=ordered,
            duration_ms=int((time.perf_counter() - started) * 1000),
            evidence_block=block,
            matched_ids=[c.concept_id for c in ordered],
        )
    except Exception as exc:  # noqa: BLE001 — degrade to L5/L1
        logger.warning("OKF retrieve failed for repo=%s: %s", repo, exc, exc_info=True)
        return OkfRetrieveResult(
            status="error",
            concepts=[],
            duration_ms=int((time.perf_counter() - started) * 1000),
            evidence_block="",
            matched_ids=[],
        )


def attach_okf_evidence(final_context: str, result: OkfRetrieveResult) -> str:
    """Append cited OKF evidence inside Confirmed final_context string only."""
    if result.status != "hit" or not result.evidence_block:
        return final_context
    return f"{final_context.rstrip()}\n\n{result.evidence_block}\n"


def _empty(status: str, started: float) -> OkfRetrieveResult:
    return OkfRetrieveResult(
        status=status,
        concepts=[],
        duration_ms=int((time.perf_counter() - started) * 1000),
        evidence_block="",
        matched_ids=[],
    )


def _normalize_tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.casefold()) if t not in _STOP}


def _match_concepts(query: str, concepts: list[OkfConcept]) -> list[OkfConcept]:
    q = query.strip()
    if not q:
        return []
    q_fold = q.casefold()
    q_tokens = _normalize_tokens(q)
    scored: list[tuple[int, OkfConcept]] = []
    for concept in concepts:
        haystacks = [
            concept.concept_id.casefold(),
            concept.title.casefold(),
            concept.description.casefold(),
            " ".join(concept.tags).casefold(),
        ]
        # Exact substring on any field
        if any(q_fold in h for h in haystacks if h):
            scored.append((100, concept))
            continue
        # Token-normalized overlap
        concept_tokens = set()
        for h in haystacks:
            concept_tokens |= _normalize_tokens(h)
        if not q_tokens or not concept_tokens:
            continue
        overlap = q_tokens & concept_tokens
        if not overlap:
            continue
        # Require majority of query tokens OR at least 2 overlapping meaningful tokens
        if len(overlap) >= max(1, (len(q_tokens) + 1) // 2) or len(overlap) >= 2:
            scored.append((len(overlap), concept))
    scored.sort(key=lambda item: (-item[0], item[1].concept_id))
    return [c for _, c in scored[:8]]


def _expand_links(
    seeds: list[OkfConcept],
    all_concepts: list[OkfConcept],
    *,
    limit: int,
) -> list[OkfConcept]:
    by_id = {c.concept_id: c for c in all_concepts}
    seen = {c.concept_id for c in seeds}
    expanded: list[OkfConcept] = []
    for seed in seeds:
        for linked_id in extract_markdown_links(seed.body):
            if linked_id in seen:
                continue
            target = by_id.get(linked_id)
            if target is None:
                continue
            expanded.append(target)
            seen.add(linked_id)
            if len(expanded) >= limit:
                return expanded
    return expanded


def _dedupe_preserve(concepts: list[OkfConcept]) -> list[OkfConcept]:
    seen: set[str] = set()
    out: list[OkfConcept] = []
    for concept in concepts:
        if concept.concept_id in seen:
            continue
        seen.add(concept.concept_id)
        out.append(concept)
    return out


def _evidence_block(repo: str, concepts: list[OkfConcept]) -> str:
    lines = [
        f'<okf_evidence repo="{escape(repo, quote=True)}" count="{len(concepts)}">'
    ]
    for concept in concepts:
        sources = concept.sources
        source_uris = []
        for item in sources:
            if isinstance(item, dict) and item.get("uri"):
                source_uris.append(str(item["uri"]))
            elif isinstance(item, str):
                source_uris.append(item)
        provenance = ",".join(source_uris) if source_uris else "generated"
        generated = concept.generated or {}
        generated_by = str(generated.get("by") or "")
        lines.append(
            "  "
            f'<concept id="{escape(concept.concept_id, quote=True)}" '
            f'type="{escape(concept.type, quote=True)}" '
            f'title="{escape(concept.title, quote=True)}" '
            f'citation="okf:{escape(concept.concept_id, quote=True)}" '
            f'provenance="{escape(provenance, quote=True)}" '
            f'generated_by="{escape(generated_by, quote=True)}" />'
        )
        if concept.description:
            lines.append(f"  <summary>{escape(concept.description)}</summary>")
    lines.append("</okf_evidence>")
    return "\n".join(lines)


def bundle_exists(repo: str, *, settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    root = okf_bundle_root(cfg.okf_cache_dir, repo)
    return root.is_dir() and any(root.rglob("*.md"))
