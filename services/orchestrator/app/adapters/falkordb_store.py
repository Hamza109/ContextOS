"""FalkorDB persistence boundary for revision-scoped EP-006 graph evidence.

EP-007 Proposed read helpers (blast/graph) return metadata/path/ids only —
never source bodies. Traversal is reverse IMPORTS for dependents plus bounded
N-hop expansion (BRD pattern IMPORTS*1..3 for blast latency context).
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Any, Protocol

from app.adapters.l1_parser import StructuralEdge, StructuralNode
from app.config import Settings

NODE_LABELS = {"File", "Module", "Class", "Method", "Call"}
EDGE_TYPES = {"CONTAINS", "DECLARES", "MAKES_CALL", "IMPORTS"}
# Keep Cypher UNWIND payloads bounded so socket timeouts stay recoverable.
_PERSIST_BATCH_SIZE = 250
# Proposed graph.html payload cap (nodes + edges each).
_GRAPH_PAYLOAD_CAP = 2000


class GraphQuery(Protocol):
    def query(self, query: str, params: dict[str, Any] | None = None) -> Any: ...


@dataclass(frozen=True)
class PersistResult:
    node_count: int


def _batched(
    rows: list[dict[str, Any]], size: int = _PERSIST_BATCH_SIZE
) -> list[list[dict[str, Any]]]:
    if not rows:
        return []
    return [rows[i : i + size] for i in range(0, len(rows), size)]


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
            for batch in _batched(rows):
                graph.query(
                    f"UNWIND $rows AS row "
                    f"MERGE (n:{label} {{repo: row.repo, entity_id: row.entity_id}}) "
                    "SET n = row",
                    {"rows": batch},
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
            for batch in _batched(rows):
                graph.query(
                    "UNWIND $rows AS row "
                    "MATCH (a {repo: row.repo, entity_id: row.source_id}) "
                    "MATCH (b {repo: row.repo, entity_id: row.target_id}) "
                    f"MERGE (a)-[r:{edge_type} "
                    "{repo: row.repo, source_path: row.source_path}]->(b) "
                    "SET r.index_revision = row.index_revision",
                    {"rows": batch},
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

    def find_file_node(
        self, repo: str, revision: str, file_name: str
    ) -> StructuralNode | None:
        """Resolve File node by source_path (basename or relative path). Proposed."""
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        normalized = _normalize_path_key(file_name)
        result = graph.query(
            "MATCH (n:File {repo: $repo, index_revision: $revision}) "
            "WHERE n.source_path = $exact OR n.source_path ENDS WITH $suffix "
            "RETURN n.entity_id, n.repo, n.source_path, n.entity_kind, "
            "n.qualified_name, n.start_line, n.end_line, n.index_revision "
            "ORDER BY size(n.source_path) ASC LIMIT 5",
            {
                "repo": repo,
                "revision": revision,
                "exact": normalized,
                "suffix": "/" + normalized if "/" not in normalized else normalized,
            },
        )
        rows = getattr(result, "result_set", [])
        if not rows:
            return None
        # Prefer exact source_path match, else shortest basename match.
        nodes = [StructuralNode(*row) for row in rows]
        for node in nodes:
            if node.source_path == normalized:
                return node
        for node in nodes:
            if node.source_path.rsplit("/", 1)[-1] == normalized.rsplit("/", 1)[-1]:
                return node
        return nodes[0]

    def reverse_imports_dependents(
        self,
        repo: str,
        revision: str,
        target_entity_id: str,
        *,
        max_hops: int = 3,
    ) -> tuple[list[str], list[str], int]:
        """Return (direct_dependents, transitive, max_depth_seen) via reverse IMPORTS.

        Proposed: files that IMPORT the target (A-IMPORTS->target ⇒ A is dependent).
        Paths/ids only — no source bodies.
        """
        hops = max(1, min(int(max_hops), 5))
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        result = graph.query(
            "MATCH path = (dep:File {repo: $repo, index_revision: $revision})"
            f"-[:IMPORTS*1..{hops}]->"
            "(target:File {repo: $repo, entity_id: $target_id, "
            "index_revision: $revision}) "
            "RETURN DISTINCT dep.source_path AS path, length(path) AS hops "
            "ORDER BY hops ASC, path ASC",
            {"repo": repo, "revision": revision, "target_id": target_entity_id},
        )
        rows = getattr(result, "result_set", [])
        return _split_direct_transitive(rows)

    def list_file_imports_subgraph(
        self,
        repo: str,
        revision: str,
        *,
        depth: int = 5,
        limit: int = _GRAPH_PAYLOAD_CAP,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """File nodes + IMPORTS edges for graph.html (metadata only). Proposed."""
        depth = max(1, min(int(depth), 5))
        cap = max(1, min(int(limit), _GRAPH_PAYLOAD_CAP))
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        node_result = graph.query(
            "MATCH (n:File {repo: $repo, index_revision: $revision}) "
            "RETURN n.entity_id, n.source_path "
            "ORDER BY n.source_path ASC LIMIT $limit",
            {"repo": repo, "revision": revision, "limit": cap},
        )
        edge_result = graph.query(
            "MATCH (a:File {repo: $repo, index_revision: $revision})"
            "-[r:IMPORTS]->"
            "(b:File {repo: $repo, index_revision: $revision}) "
            "RETURN a.entity_id, b.entity_id, a.source_path, b.source_path "
            "ORDER BY a.source_path ASC LIMIT $limit",
            {"repo": repo, "revision": revision, "limit": cap},
        )
        nodes = [
            {"id": str(row[0]), "path": str(row[1])}
            for row in getattr(node_result, "result_set", [])
        ]
        # depth query param is honored by the HTML client (1–5); server returns
        # the capped File/IMPORTS universe for interactive filtering.
        _ = depth
        edges = [
            {
                "from": str(row[0]),
                "to": str(row[1]),
                "from_path": str(row[2]),
                "to_path": str(row[3]),
                "kind": "IMPORTS",
            }
            for row in getattr(edge_result, "result_set", [])
        ]
        return nodes, edges

    def list_structural_subgraph(
        self,
        repo: str,
        revision: str,
        *,
        depth: int = 5,
        limit: int = _GRAPH_PAYLOAD_CAP,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """File/Module/Class/Method/Call + L1 edges for Proposed symbols graph.html."""
        _ = depth
        cap = max(1, min(int(limit), _GRAPH_PAYLOAD_CAP))
        graph = self.for_repo(repo).graph if self._repo != repo else self.graph
        node_result = graph.query(
            "MATCH (n {repo: $repo, index_revision: $revision}) "
            "WHERE n.entity_kind IN $kinds "
            "RETURN n.entity_id, n.source_path, n.entity_kind, n.qualified_name "
            "ORDER BY n.source_path ASC, n.entity_kind ASC LIMIT $limit",
            {
                "repo": repo,
                "revision": revision,
                "kinds": sorted(NODE_LABELS),
                "limit": cap,
            },
        )
        nodes = [
            {
                "id": str(row[0]),
                "path": str(row[1]),
                "kind": str(row[2]),
                "qname": str(row[3]),
            }
            for row in getattr(node_result, "result_set", [])
        ]
        edges: list[dict[str, str]] = []
        for edge_type in sorted(EDGE_TYPES):
            if len(edges) >= cap:
                break
            remaining = cap - len(edges)
            edge_result = graph.query(
                "MATCH (a {repo: $repo, index_revision: $revision})"
                f"-[r:{edge_type}]->"
                "(b {repo: $repo, index_revision: $revision}) "
                "RETURN a.entity_id, b.entity_id, a.source_path, b.source_path "
                "ORDER BY a.source_path ASC LIMIT $limit",
                {"repo": repo, "revision": revision, "limit": remaining},
            )
            for row in getattr(edge_result, "result_set", []):
                edges.append(
                    {
                        "from": str(row[0]),
                        "to": str(row[1]),
                        "from_path": str(row[2]),
                        "to_path": str(row[3]),
                        "kind": edge_type,
                    }
                )
                if len(edges) >= cap:
                    break
        return nodes, edges

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

    def find_file_node(
        self, repo: str, revision: str, file_name: str
    ) -> StructuralNode | None:
        if self.revisions.get(repo) != revision:
            return None
        normalized = _normalize_path_key(file_name)
        files = [
            node
            for node in self.nodes.get(repo, {}).values()
            if node.entity_kind == "File" and node.index_revision == revision
        ]
        for node in files:
            if node.source_path == normalized:
                return node
        basename = normalized.rsplit("/", 1)[-1]
        matches = [
            node for node in files if node.source_path.rsplit("/", 1)[-1] == basename
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda n: len(n.source_path))[0]

    def reverse_imports_dependents(
        self,
        repo: str,
        revision: str,
        target_entity_id: str,
        *,
        max_hops: int = 3,
    ) -> tuple[list[str], list[str], int]:
        if self.revisions.get(repo) != revision:
            return [], [], 0
        hops = max(1, min(int(max_hops), 5))
        id_to_path = {
            node.entity_id: node.source_path
            for node in self.nodes.get(repo, {}).values()
            if node.entity_kind == "File" and node.index_revision == revision
        }
        if target_entity_id not in id_to_path:
            return [], [], 0
        # Reverse adjacency: target <-IMPORTS- source  ⇒ source depends on target
        reverse: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges.get(repo, []):
            if edge.edge_kind != "IMPORTS":
                continue
            if edge.source_id not in id_to_path or edge.target_id not in id_to_path:
                continue
            reverse[edge.target_id].append(edge.source_id)

        depth_map: dict[str, int] = {}
        queue: deque[tuple[str, int]] = deque([(target_entity_id, 0)])
        seen = {target_entity_id}
        while queue:
            current, depth = queue.popleft()
            if depth >= hops:
                continue
            for dependent_id in reverse.get(current, []):
                if dependent_id in seen:
                    continue
                seen.add(dependent_id)
                next_depth = depth + 1
                depth_map[dependent_id] = next_depth
                queue.append((dependent_id, next_depth))

        rows = [
            (id_to_path[entity_id], depth)
            for entity_id, depth in sorted(
                depth_map.items(), key=lambda item: (item[1], id_to_path[item[0]])
            )
        ]
        return _split_direct_transitive(rows)

    def list_file_imports_subgraph(
        self,
        repo: str,
        revision: str,
        *,
        depth: int = 5,
        limit: int = _GRAPH_PAYLOAD_CAP,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        _ = depth
        if self.revisions.get(repo) != revision:
            return [], []
        cap = max(1, min(int(limit), _GRAPH_PAYLOAD_CAP))
        files = sorted(
            (
                node
                for node in self.nodes.get(repo, {}).values()
                if node.entity_kind == "File" and node.index_revision == revision
            ),
            key=lambda node: node.source_path,
        )[:cap]
        allowed = {node.entity_id for node in files}
        nodes = [{"id": node.entity_id, "path": node.source_path} for node in files]
        edges: list[dict[str, str]] = []
        for edge in self.edges.get(repo, []):
            if edge.edge_kind != "IMPORTS":
                continue
            if edge.source_id not in allowed or edge.target_id not in allowed:
                continue
            edges.append(
                {
                    "from": edge.source_id,
                    "to": edge.target_id,
                    "from_path": self.nodes[repo][edge.source_id].source_path,
                    "to_path": self.nodes[repo][edge.target_id].source_path,
                    "kind": "IMPORTS",
                }
            )
            if len(edges) >= cap:
                break
        return nodes, edges

    def list_structural_subgraph(
        self,
        repo: str,
        revision: str,
        *,
        depth: int = 5,
        limit: int = _GRAPH_PAYLOAD_CAP,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        _ = depth
        if self.revisions.get(repo) != revision:
            return [], []
        cap = max(1, min(int(limit), _GRAPH_PAYLOAD_CAP))
        entities = sorted(
            (
                node
                for node in self.nodes.get(repo, {}).values()
                if node.entity_kind in NODE_LABELS and node.index_revision == revision
            ),
            key=lambda node: (node.source_path, node.entity_kind, node.qualified_name),
        )[:cap]
        allowed = {node.entity_id for node in entities}
        nodes = [
            {
                "id": node.entity_id,
                "path": node.source_path,
                "kind": node.entity_kind,
                "qname": node.qualified_name,
            }
            for node in entities
        ]
        edges: list[dict[str, str]] = []
        for edge in self.edges.get(repo, []):
            if edge.edge_kind not in EDGE_TYPES:
                continue
            if edge.source_id not in allowed or edge.target_id not in allowed:
                continue
            edges.append(
                {
                    "from": edge.source_id,
                    "to": edge.target_id,
                    "from_path": self.nodes[repo][edge.source_id].source_path,
                    "to_path": self.nodes[repo][edge.target_id].source_path,
                    "kind": edge.edge_kind,
                }
            )
            if len(edges) >= cap:
                break
        return nodes, edges

    def health(self) -> str:
        return "ok"


_memory_store: InMemoryFalkorStore | None = None


def get_graph_store(settings: Settings):
    """Return FalkorDBStore or process-local InMemoryFalkorStore for memory://."""
    global _memory_store
    if settings.falkordb_url.startswith("memory://"):
        if _memory_store is None:
            _memory_store = InMemoryFalkorStore()
        return _memory_store
    return FalkorDBStore(settings)


def reset_memory_graph_store() -> None:
    """Clear shared memory store between tests."""
    global _memory_store
    _memory_store = None


def _normalize_path_key(file_name: str) -> str:
    normalized = (file_name or "").replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def _split_direct_transitive(
    rows: list[Any],
) -> tuple[list[str], list[str], int]:
    direct: list[str] = []
    transitive: list[str] = []
    max_depth = 0
    seen: set[str] = set()
    for row in rows:
        path = str(row[0])
        hops = int(row[1])
        if path in seen:
            continue
        seen.add(path)
        max_depth = max(max_depth, hops)
        if hops <= 1:
            direct.append(path)
        else:
            transitive.append(path)
    return direct, transitive, max_depth


def _graph_name(settings: Settings, repo: str) -> str:
    prefix = re.sub(r"[^A-Za-z0-9_]", "_", settings.falkordb_graph_prefix)
    digest = hashlib.sha256(repo.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
