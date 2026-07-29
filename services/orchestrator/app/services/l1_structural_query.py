"""Local structural-intent matching and cited L1 evidence composition.

EP-007: blast-intent queries no longer permanently short-circuit as
``blast_declined`` without allowing ``POST /context`` to populate
``blast_radius``. Status ``blast_intent`` signals context.py to attach blast
via ``l1_blast`` (final_context left unchanged for blast asks). Non-blast L1
location/ownership enrichment is unchanged.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from html import escape

from app.adapters.falkordb_store import FalkorDBStore
from app.adapters.l1_parser import StructuralNode
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache, get_l1_entity_cache

_STRUCTURAL_HINTS = (
    "where is",
    "where does",
    "defined",
    "located",
    "which class",
    "which module",
    "who owns",
    "what owns",
    "implementation of",
)
_BLAST_HINTS = ("blast radius", "what breaks", "affected by", "impact of changing")
_STOP_WORDS = {
    "where",
    "does",
    "which",
    "class",
    "module",
    "what",
    "who",
    "owns",
    "owned",
    "located",
    "defined",
    "implementation",
    "the",
    "this",
    "that",
    "for",
    "from",
    "with",
    "blast",
    "radius",
    "breaks",
    "affected",
    "impact",
    "changing",
}


def is_blast_intent(query: str) -> bool:
    """True when query matches EP-006/007 blast hint phrases."""
    lowered = (query or "").casefold()
    return any(hint in lowered for hint in _BLAST_HINTS)


@dataclass(frozen=True)
class StructuralEnrichment:
    final_context: str
    status: str
    cache_hit: bool
    entity_count: int
    duration_ms: int


class StructuralQueryService:
    def __init__(
        self,
        settings: Settings,
        *,
        cache: L1EntityCache | None = None,
        store=None,
    ) -> None:
        self.cache = cache if cache is not None else get_l1_entity_cache()
        self.store = (
            store
            if store is not None
            else (
                None
                if settings.falkordb_url.startswith("memory://")
                else FalkorDBStore(settings)
            )
        )

    def enrich(self, final_context: str, *, repo: str, query: str) -> StructuralEnrichment:
        started = time.perf_counter()
        lowered = query.casefold()
        if is_blast_intent(query):
            # EP-007: do not permanently decline — context.py populates blast_radius.
            return self._result(final_context, "blast_intent", False, 0, started)
        if not any(hint in lowered for hint in _STRUCTURAL_HINTS):
            return self._result(final_context, "unsupported", False, 0, started)

        terms = _query_terms(query)
        if not terms:
            return self._result(final_context, "unsupported", False, 0, started)
        lookup = self.cache.lookup(repo, terms)
        entities = lookup.entities
        revision = lookup.revision
        cache_hit = lookup.hit

        if not entities and self.store is not None:
            try:
                revision = revision or self.store.latest_revision(repo)
                if revision:
                    entities = self.store.get_entities(
                        repo, revision, terms=terms, limit=20
                    )
                    if entities:
                        if self.cache.current_revision(repo) != revision:
                            self.cache.refresh(repo, revision, entities)
                        else:
                            for entity in entities:
                                self.cache.put(entity)
            except Exception:
                return self._result(final_context, "l1_unavailable", False, 0, started)

        if not entities or not revision:
            return self._result(final_context, "l1_miss", False, 0, started)
        block = _evidence_block(repo, revision, entities)
        return self._result(
            f"{final_context.rstrip()}\n\n{block}\n",
            "attached",
            cache_hit,
            len(entities),
            started,
        )

    @staticmethod
    def _result(
        final_context: str,
        status: str,
        cache_hit: bool,
        count: int,
        started: float,
    ) -> StructuralEnrichment:
        return StructuralEnrichment(
            final_context=final_context,
            status=status,
            cache_hit=cache_hit,
            entity_count=count,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )


def _query_terms(query: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", query.casefold())
    return [token for token in tokens if token not in _STOP_WORDS][:8]


def _evidence_block(repo: str, revision: str, entities: list[StructuralNode]) -> str:
    lines = [
        (
            f'<l1_structural_evidence repo="{escape(repo, quote=True)}" '
            f'index_revision="{escape(revision, quote=True)}">'
        )
    ]
    for entity in entities:
        lines.append(
            "  "
            f'<entity id="{escape(entity.entity_id, quote=True)}" '
            f'kind="{escape(entity.entity_kind, quote=True)}" '
            f'qualified_name="{escape(entity.qualified_name, quote=True)}" '
            f'path="{escape(entity.source_path, quote=True)}" '
            f'start_line="{entity.start_line}" end_line="{entity.end_line}" '
            f'citation="{escape(entity.source_path, quote=True)}:{entity.start_line}" />'
        )
    lines.append("</l1_structural_evidence>")
    return "\n".join(lines)
