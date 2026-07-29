"""FastAPI-owned L1 parse/persist orchestration.

This service never walks a repository. Callers must supply only paths returned by
the shared IgnorePolicy/walk_allowed_files eligibility boundary.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.adapters.falkordb_store import PersistResult, get_graph_store
from app.adapters.l1_parser import L1Parser, ParseResult, StructuralNode, TreeSitterL1Parser
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache, get_l1_entity_cache


class L1Store(Protocol):
    def persist(
        self,
        repo: str,
        revision: str,
        nodes: list[StructuralNode],
        edges: list,
        *,
        affected_paths: list[str] | None = None,
    ) -> PersistResult: ...

    def get_entities(
        self, repo: str, revision: str, *, terms=(), limit: int = 100
    ) -> list[StructuralNode]: ...


@dataclass(frozen=True)
class L1GraphResult:
    graph_nodes: int
    index_revision: str
    parse_ms: int
    persist_ms: int
    parsed_files: int
    unsupported_files: int
    malformed_files: int


class L1GraphService:
    def __init__(
        self,
        settings: Settings,
        *,
        parser: L1Parser | None = None,
        store: L1Store | None = None,
        cache: L1EntityCache | None = None,
    ) -> None:
        self.parser = parser if parser is not None else TreeSitterL1Parser()
        # Shared memory:// store so index → blast/graph share revision evidence.
        self.store = store if store is not None else get_graph_store(settings)
        self.cache = cache if cache is not None else get_l1_entity_cache()

    def generate(
        self,
        repo: str,
        root: Path,
        allowed_paths: list[Path],
        *,
        affected_paths: list[str] | None = None,
    ) -> L1GraphResult:
        _validate_allowed_paths(root, allowed_paths)
        revision = _index_revision(repo, root, allowed_paths)

        parse_started = time.perf_counter()
        parsed: ParseResult = self.parser.parse_paths(repo, root, allowed_paths, revision)
        persist_nodes = parsed.nodes
        persist_edges = parsed.edges
        if affected_paths:
            affected = set(affected_paths)
            persist_nodes = [
                node for node in parsed.nodes if node.source_path in affected
            ]
            affected_ids = {node.entity_id for node in persist_nodes}
            persist_edges = [
                edge
                for edge in parsed.edges
                if edge.source_path in affected
                or edge.source_id in affected_ids
                or edge.target_id in affected_ids
            ]
        parse_ms = int((time.perf_counter() - parse_started) * 1000)

        persist_started = time.perf_counter()
        persisted = self.store.persist(
            repo,
            revision,
            persist_nodes,
            persist_edges,
            affected_paths=affected_paths,
        )
        persist_ms = int((time.perf_counter() - persist_started) * 1000)

        # Persistence is the commit boundary: cache changes only after this point.
        warm_entities = self.store.get_entities(repo, revision, limit=self.cache.max_entries)
        self.cache.refresh(repo, revision, warm_entities)
        return L1GraphResult(
            graph_nodes=persisted.node_count,
            index_revision=revision,
            parse_ms=parse_ms,
            persist_ms=persist_ms,
            parsed_files=parsed.parsed_files,
            unsupported_files=parsed.unsupported_files,
            malformed_files=parsed.malformed_files,
        )


def _validate_allowed_paths(root: Path, paths: list[Path]) -> None:
    resolved_root = root.resolve()
    for path in paths:
        resolved = path.resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError("L1 path is outside the repository policy boundary") from exc
        if not resolved.is_file():
            raise ValueError("L1 path must be an existing policy-approved file")


def _index_revision(repo: str, root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256(repo.encode("utf-8"))
    for path in sorted(paths):
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        digest.update(b"\0")
        digest.update(rel.encode("utf-8"))
        # Local digest is provenance/freshness only; source bytes leave neither
        # the process nor telemetry.
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()
