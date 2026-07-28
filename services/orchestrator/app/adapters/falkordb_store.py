"""FalkorDB persistence boundary for revision-scoped EP-006 graph evidence."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Any, Protocol

from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings

NODE_LABELS = {"File", "Module", "Class", "Method", "Call"}
EDGE_TYPES = {"CONTAINS", "DECLARES", "MAKES_CALL", "IMPORTS"}


class GraphQuery(Protocol):
    def query(self, query: str, params: dict[str, Any] | None = None) -> Any: ...


@dataclass(frozen=True)
class PersistResult:
    node_count: int


class FalkorDBStore:
    """Official-client adapter; graph names and Cypher types are allow-listed."""

    def __init__(
        self,
        settings: Settings,
        *,
        graph: GraphQuery | None = None,
        repo: str | None = None,
    ) -> None:
        self.settings = settings
        self._graph = graph
        self._repo = repo

    def for_repo(self, repo: str) -> FalkorDBStore:
        return FalkorDBStore(self.settings, graph=self._graph, repo=repo)

    @property
    def graph(self) -> GraphQuery:
        if self._graph is not None:
            return self._graph
        if self._repo is None:
            raise ValueError("repository must be selected before graph access")
        from falkordb import FalkorDB

        timeout = self.settings.falkordb_timeout_seconds
        client = FalkorDB.from_url(
            self.settings.falkordb_url,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
        )
        self._graph = client.select_graph(_graph_name(self.settings, self._repo))
        return self._graph

    def persist(
        self,
        repo: str,
        revision: str,
        nodes: list[StructuralNode],
        edges: list[StructuralEdge],
        *,
        affected_paths: list[str] | None = None,
    ) -> PersistResult:
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        if affected_paths:
            graph.query(
                "MATCH (n {repo: $repo}) WHERE n.source_path IN $paths DETACH DELETE n",
                {"repo": repo, "paths": affected_paths},
            )
            graph.query(
                "MATCH (n {repo: $repo}) SET n.index_revision = $revision",
                {"repo": repo, "revision": revision},
            )
            graph.query(
                "MATCH ()-[r {repo: $repo}]->() SET r.index_revision = $revision",
                {"repo": repo, "revision": revision},
            )

        for label in NODE_LABELS:
            rows = [node.as_properties() for node in nodes if node.entity_kind == label]
            if not rows:
                continue
            graph.query(
                f"UNWIND $rows AS row "
                f"MERGE (n:{label} {{repo: row.repo, entity_id: row.entity_id}}) "
                "SET n = row",
                {"rows": rows},
            )

        for edge_type in EDGE_TYPES:
            rows = [
                {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    **edge.as_properties(),
                }
                for edge in edges
                if edge.edge_kind == edge_type
            ]
            if not rows:
                continue
            graph.query(
                "UNWIND $rows AS row "
                "MATCH (a {repo: row.repo, entity_id: row.source_id}) "
                "MATCH (b {repo: row.repo, entity_id: row.target_id}) "
                f"MERGE (a)-[r:{edge_type} {{repo: row.repo, source_path: row.source_path}}]->(b) "
                "SET r.index_revision = row.index_revision",
                {"rows": rows},
            )

        graph.query(
            "MERGE (r:IndexRevision {repo: $repo}) "
            "SET r.index_revision = $revision, r.active = true",
            {"repo": repo, "revision": revision},
        )
        if not affected_paths:
            graph.query(
                "MATCH (n {repo: $repo}) "
                "WHERE NOT n:IndexRevision AND n.index_revision <> $revision "
                "DETACH DELETE n",
                {"repo": repo, "revision": revision},
            )
            graph.query(
                "MATCH ()-[r {repo: $repo}]->() "
                "WHERE r.index_revision IS NULL OR r.index_revision <> $revision "
                "DELETE r",
                {"repo": repo, "revision": revision},
            )
        return PersistResult(node_count=len({node.entity_id for node in nodes}))

    def latest_revision(self, repo: str) -> str | None:
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        result = graph.query(
            "MATCH (r:IndexRevision {repo: $repo, active: true}) RETURN r.index_revision LIMIT 1",
            {"repo": repo},
        )
        rows = getattr(result, "result_set", [])
        return str(rows[0][0]) if rows else None

    def get_entities(
        self,
        repo: str,
        revision: str,
        *,
        terms: Iterable[str] = (),
        limit: int = 100,
    ) -> list[StructuralNode]:
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        normalized = [term.lower() for term in terms if term]
        result = graph.query(
            "MATCH (n {repo: $repo, index_revision: $revision}) "
            "WHERE n.entity_kind IN ['File','Module','Class','Method'] "
            "AND (size($terms) = 0 OR any(term IN $terms "
            "WHERE toLower(n.qualified_name) CONTAINS term)) "
            "RETURN n.entity_id, n.repo, n.source_path, n.entity_kind, "
            "n.qualified_name, n.start_line, n.end_line, n.index_revision "
            "ORDER BY n.source_path, n.start_line LIMIT $limit",
            {"repo": repo, "revision": revision, "terms": normalized, "limit": limit},
        )
        rows = getattr(result, "result_set", [])
        return [StructuralNode(*row) for row in rows]

    def health(self) -> str:
        try:
            from falkordb import FalkorDB

            timeout = self.settings.falkordb_timeout_seconds
            client = FalkorDB.from_url(
                self.settings.falkordb_url,
                socket_timeout=timeout,
                socket_connect_timeout=timeout,
            )
            return "ok" if client.connection.ping() else "error"
        except Exception:  # dependency health must not expose connection details
            return "error"


class InMemoryFalkorStore:
    """Metadata-only deterministic store for unit/contract tests."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, StructuralNode]] = {}
        self.edges: dict[str, list[StructuralEdge]] = {}
        self.revisions: dict[str, str] = {}

    def persist(
        self,
        repo: str,
        revision: str,
        nodes: list[StructuralNode],
        edges: list[StructuralEdge],
        *,
        affected_paths: list[str] | None = None,
    ) -> PersistResult:
        current = self.nodes.setdefault(repo, {})
        if affected_paths:
            affected = set(affected_paths)
            removed_ids = {
                entity_id
                for entity_id, node in current.items()
                if node.source_path in affected
            }
            current = {
                entity_id: replace(node, index_revision=revision)
                for entity_id, node in current.items()
                if node.source_path not in affected
            }
            retained_edges = [
                replace(edge, index_revision=revision)
                for edge in self.edges.get(repo, [])
                if edge.source_path not in affected
                and edge.source_id not in removed_ids
                and edge.target_id not in removed_ids
            ]
        else:
            current = {}
            retained_edges = []
        current.update({node.entity_id: node for node in nodes})
        self.nodes[repo] = current
        self.edges[repo] = [*retained_edges, *edges]
        self.revisions[repo] = revision
        return PersistResult(node_count=len({node.entity_id for node in nodes}))

    def latest_revision(self, repo: str) -> str | None:
        return self.revisions.get(repo)

    def get_entities(
        self,
        repo: str,
        revision: str,
        *,
        terms: Iterable[str] = (),
        limit: int = 100,
    ) -> list[StructuralNode]:
        if self.revisions.get(repo) != revision:
            return []
        wanted = [term.lower() for term in terms if term]
        values = (
            node
            for node in self.nodes.get(repo, {}).values()
            if node.entity_kind in {"File", "Module", "Class", "Method"}
            and (not wanted or any(term in node.qualified_name.lower() for term in wanted))
        )
        return sorted(values, key=lambda node: (node.source_path, node.start_line))[:limit]

    def health(self) -> str:
        return "ok"


def _graph_name(settings: Settings, repo: str) -> str:
    prefix = re.sub(r"[^A-Za-z0-9_]", "_", settings.falkordb_graph_prefix)
    digest = hashlib.sha256(repo.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
