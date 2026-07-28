"""Bounded process-local metadata cache for EP-006 structural entities."""

from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import lru_cache

from app.adapters.l1_parser import StructuralNode
from app.config import get_settings

CacheKey = tuple[str, str, str]


@dataclass(frozen=True)
class CacheLookup:
    entities: list[StructuralNode]
    hit: bool
    revision: str | None


class L1EntityCache:
    def __init__(
        self,
        max_entries: int = 10_000,
        ttl_seconds: float = 300.0,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_entries < 1 or ttl_seconds <= 0:
            raise ValueError("cache bounds and TTL must be positive")
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: OrderedDict[CacheKey, tuple[float, StructuralNode]] = OrderedDict()
        self._revisions: dict[str, str] = {}

    def refresh(self, repo: str, revision: str, entities: Iterable[StructuralNode]) -> None:
        """Invalidate the prior repository revision, then warm committed metadata."""
        self.invalidate_repo(repo)
        self._revisions[repo] = revision
        for entity in entities:
            if entity.repo != repo or entity.index_revision != revision:
                continue
            if entity.entity_kind not in {"File", "Module", "Class", "Method"}:
                continue
            self.put(entity)

    def invalidate_repo(self, repo: str) -> None:
        for key in [key for key in self._entries if key[0] == repo]:
            del self._entries[key]
        self._revisions.pop(repo, None)

    def put(self, entity: StructuralNode) -> None:
        key = (entity.repo, entity.index_revision, entity.entity_id)
        self._entries.pop(key, None)
        self._entries[key] = (self._clock() + self.ttl_seconds, entity)
        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)

    def get(self, repo: str, revision: str, entity_id: str) -> StructuralNode | None:
        key = (repo, revision, entity_id)
        item = self._entries.get(key)
        if item is None:
            return None
        expires_at, entity = item
        if expires_at <= self._clock():
            del self._entries[key]
            return None
        self._entries.move_to_end(key)
        return entity

    def lookup(self, repo: str, terms: Iterable[str], *, limit: int = 20) -> CacheLookup:
        revision = self._revisions.get(repo)
        if revision is None:
            return CacheLookup([], False, None)
        normalized = [term.casefold() for term in terms if term]
        entities: list[StructuralNode] = []
        expired: list[CacheKey] = []
        for key, (expires_at, entity) in self._entries.items():
            if key[0] != repo or key[1] != revision:
                continue
            if expires_at <= self._clock():
                expired.append(key)
                continue
            haystack = f"{entity.qualified_name} {entity.source_path}".casefold()
            if not normalized or any(term in haystack for term in normalized):
                entities.append(entity)
        for key in expired:
            self._entries.pop(key, None)
        entities.sort(key=lambda item: (item.source_path, item.start_line, item.entity_id))
        return CacheLookup(entities[:limit], bool(entities), revision)

    def current_revision(self, repo: str) -> str | None:
        return self._revisions.get(repo)

    def __len__(self) -> int:
        return len(self._entries)


@lru_cache
def get_l1_entity_cache() -> L1EntityCache:
    settings = get_settings()
    return L1EntityCache(settings.l1_cache_max_entries, settings.l1_cache_ttl_seconds)
