"""Local tree-sitter structural extraction for EP-006.

The adapter receives policy-approved files only. Source bytes are used transiently
for parsing and are never included in returned graph records.
"""

from __future__ import annotations

import hashlib
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from tree_sitter_language_pack import get_parser

SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".java": "java",
}

_CLASS_TYPES = {"class_definition", "class_declaration", "type_spec"}
_FUNCTION_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "method_declaration",
    "constructor_declaration",
}
_CALL_TYPES = {"call", "call_expression", "method_invocation"}
_IMPORT_TYPES = {
    "import_statement",
    "import_from_statement",
    "import_declaration",
    "package_clause",
}
_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+([.\w/@-]+)\s+import|import\s+(?:[\w*{},\s]+\s+from\s+)?[\"']?([\w./@-]+))",
    re.MULTILINE,
)


@dataclass(frozen=True)
class StructuralNode:
    entity_id: str
    repo: str
    source_path: str
    entity_kind: str
    qualified_name: str
    start_line: int
    end_line: int
    index_revision: str

    def as_properties(self) -> dict[str, str | int]:
        return {
            "entity_id": self.entity_id,
            "repo": self.repo,
            "source_path": self.source_path,
            "entity_kind": self.entity_kind,
            "qualified_name": self.qualified_name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "index_revision": self.index_revision,
        }


@dataclass(frozen=True)
class StructuralEdge:
    source_id: str
    target_id: str
    edge_kind: str
    repo: str
    source_path: str
    index_revision: str

    def as_properties(self) -> dict[str, str]:
        return {
            "repo": self.repo,
            "source_path": self.source_path,
            "index_revision": self.index_revision,
        }


@dataclass
class ParseResult:
    nodes: list[StructuralNode] = field(default_factory=list)
    edges: list[StructuralEdge] = field(default_factory=list)
    parsed_files: int = 0
    unsupported_files: int = 0
    malformed_files: int = 0


class L1Parser(Protocol):
    def parse_paths(
        self, repo: str, root: Path, paths: list[Path], index_revision: str
    ) -> ParseResult: ...


def deterministic_entity_id(
    repo: str,
    source_path: str,
    entity_kind: str,
    qualified_name: str,
    start_line: int,
    end_line: int,
) -> str:
    raw = "\0".join(
        (repo, source_path, entity_kind, qualified_name, str(start_line), str(end_line))
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class TreeSitterL1Parser:
    """Extract normalized File/Module/Class/Method/Call nodes and typed edges."""

    def parse_paths(
        self, repo: str, root: Path, paths: list[Path], index_revision: str
    ) -> ParseResult:
        result = ParseResult()
        for path in paths:
            language = SUPPORTED_LANGUAGES.get(path.suffix.lower())
            if language is None:
                result.unsupported_files += 1
                continue
            parsed = self._parse_file(repo, root, path, language, index_revision)
            result.nodes.extend(parsed.nodes)
            result.edges.extend(parsed.edges)
            result.parsed_files += parsed.parsed_files
            result.malformed_files += parsed.malformed_files
        result.nodes = list({node.entity_id: node for node in result.nodes}.values())
        result.edges = list(
            {
                (edge.source_id, edge.target_id, edge.edge_kind): edge
                for edge in result.edges
            }.values()
        )
        _add_resolved_file_imports(result)
        return result

    def _parse_file(
        self,
        repo: str,
        root: Path,
        path: Path,
        language: str,
        revision: str,
    ) -> ParseResult:
        source = path.read_bytes()
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        lines = max(1, source.count(b"\n") + 1)
        file_node = _node(repo, rel, "File", rel, 1, lines, revision)
        module_name = _module_name(rel)
        module_node = _node(repo, rel, "Module", module_name, 1, lines, revision)
        result = ParseResult(
            nodes=[file_node, module_node],
            edges=[_edge(file_node, module_node, "CONTAINS")],
            parsed_files=1,
        )

        try:
            tree = get_parser(language).parse(source)
        except Exception:  # grammar loading/parsing failure: imports only
            result.malformed_files = 1
            self._fallback_imports(source, result, module_node)
            return result

        if tree.root_node.has_error:
            result.malformed_files = 1
            self._fallback_imports(source, result, module_node)
            return result

        self._walk(
            tree.root_node,
            source,
            result,
            module_node,
            owner=module_node,
            scope=[module_name],
        )
        return result

    def _walk(
        self,
        ast_node,
        source: bytes,
        result: ParseResult,
        module_node: StructuralNode,
        *,
        owner: StructuralNode,
        scope: list[str],
    ) -> None:
        current_owner = owner
        current_scope = scope
        kind: str | None = None
        edge_kind: str | None = None
        if ast_node.type in _CLASS_TYPES:
            kind, edge_kind = "Class", "DECLARES"
        elif ast_node.type in _FUNCTION_TYPES:
            kind, edge_kind = "Method", "DECLARES"

        if kind:
            name = _node_name(ast_node, source)
            if name:
                qname = ".".join([*scope, name])
                structural = _node(
                    module_node.repo,
                    module_node.source_path,
                    kind,
                    qname,
                    ast_node.start_point.row + 1,
                    ast_node.end_point.row + 1,
                    module_node.index_revision,
                )
                result.nodes.append(structural)
                result.edges.append(_edge(owner, structural, edge_kind or "DECLARES"))
                current_owner = structural
                current_scope = [*scope, name]

        if ast_node.type in _CALL_TYPES:
            callee = _callee_name(ast_node, source)
            if callee:
                line = ast_node.start_point.row + 1
                qname = f"{'.'.join(scope)}::{callee}@{line}"
                call = _node(
                    module_node.repo,
                    module_node.source_path,
                    "Call",
                    qname,
                    line,
                    ast_node.end_point.row + 1,
                    module_node.index_revision,
                )
                result.nodes.append(call)
                result.edges.append(_edge(owner, call, "MAKES_CALL"))

        if ast_node.type in _IMPORT_TYPES:
            for imported in _import_names(ast_node, source):
                target = _node(
                    module_node.repo,
                    module_node.source_path,
                    "Module",
                    imported,
                    ast_node.start_point.row + 1,
                    ast_node.end_point.row + 1,
                    module_node.index_revision,
                )
                result.nodes.append(target)
                result.edges.append(_edge(module_node, target, "IMPORTS"))

        for child in ast_node.named_children:
            self._walk(
                child,
                source,
                result,
                module_node,
                owner=current_owner,
                scope=current_scope,
            )

    def _fallback_imports(
        self, source: bytes, result: ParseResult, module_node: StructuralNode
    ) -> None:
        text = source.decode("utf-8", errors="replace")
        for match in _IMPORT_RE.finditer(text):
            imported = match.group(1) or match.group(2)
            if not imported:
                continue
            line = text.count("\n", 0, match.start()) + 1
            target = _node(
                module_node.repo,
                module_node.source_path,
                "Module",
                imported,
                line,
                line,
                module_node.index_revision,
            )
            result.nodes.append(target)
            result.edges.append(_edge(module_node, target, "IMPORTS"))


def _node(
    repo: str,
    path: str,
    kind: str,
    qname: str,
    start: int,
    end: int,
    revision: str,
) -> StructuralNode:
    return StructuralNode(
        entity_id=deterministic_entity_id(repo, path, kind, qname, start, end),
        repo=repo,
        source_path=path,
        entity_kind=kind,
        qualified_name=qname,
        start_line=start,
        end_line=end,
        index_revision=revision,
    )


def _edge(source: StructuralNode, target: StructuralNode, kind: str) -> StructuralEdge:
    return StructuralEdge(
        source_id=source.entity_id,
        target_id=target.entity_id,
        edge_kind=kind,
        repo=source.repo,
        source_path=source.source_path,
        index_revision=source.index_revision,
    )


def _slice(node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _node_name(node, source: bytes) -> str | None:
    named = node.child_by_field_name("name")
    if named is not None:
        return _slice(named, source).strip()
    for child in node.named_children:
        if child.type in {"identifier", "type_identifier", "property_identifier"}:
            return _slice(child, source).strip()
    return None


def _callee_name(node, source: bytes) -> str | None:
    function = node.child_by_field_name("function") or node.child_by_field_name("name")
    if function is not None:
        return _slice(function, source).strip()[:256]
    return _slice(node, source).split("(", 1)[0].strip()[:256] or None


def _import_names(node, source: bytes) -> list[str]:
    text = _slice(node, source)
    names = [a or b for a, b in _IMPORT_RE.findall(text) if a or b]
    if names:
        return names
    quoted = re.findall(r"[\"']([^\"']+)[\"']", text)
    return quoted[:1]


def _module_name(path: str) -> str:
    no_suffix = str(Path(path).with_suffix("")).replace("\\", "/")
    return no_suffix.replace("/", ".")


def _add_resolved_file_imports(result: ParseResult) -> None:
    """Add Confirmed File→File IMPORTS edges when a local target can be resolved."""
    nodes_by_id = {node.entity_id: node for node in result.nodes}
    files_by_path = {
        node.source_path: node for node in result.nodes if node.entity_kind == "File"
    }
    files_by_module = {
        node.qualified_name: files_by_path[node.source_path]
        for node in result.nodes
        if node.entity_kind == "Module"
        and node.source_path in files_by_path
        and node.qualified_name == _module_name(node.source_path)
    }
    resolved: list[StructuralEdge] = []
    for edge in result.edges:
        if edge.edge_kind != "IMPORTS":
            continue
        source = nodes_by_id.get(edge.source_id)
        target = nodes_by_id.get(edge.target_id)
        if source is None or target is None:
            continue
        source_file = files_by_path.get(source.source_path)
        target_file = next(
            (
                files_by_module[candidate]
                for candidate in _import_module_candidates(
                    source.source_path, target.qualified_name
                )
                if candidate in files_by_module
            ),
            None,
        )
        if source_file is not None and target_file is not None:
            resolved.append(_edge(source_file, target_file, "IMPORTS"))
    result.edges.extend(resolved)
    result.edges = list(
        {
            (edge.source_id, edge.target_id, edge.edge_kind): edge
            for edge in result.edges
        }.values()
    )


def _import_module_candidates(source_path: str, imported: str) -> list[str]:
    raw = imported.strip().replace("\\", "/")
    candidates = [raw.replace("/", ".").strip(".")]
    if raw.startswith("."):
        candidates.insert(0, _python_relative_import_candidate(source_path, raw))
    return [candidate for candidate in candidates if candidate]


def _python_relative_import_candidate(source_path: str, imported: str) -> str:
    leading_dots = len(imported) - len(imported.lstrip("."))
    suffix = imported[leading_dots:].strip(".")
    package_parts = [part for part in posixpath.dirname(source_path).split("/") if part]
    keep = max(0, len(package_parts) - max(0, leading_dots - 1))
    target_parts = package_parts[:keep]
    if suffix:
        target_parts.extend(part for part in suffix.split(".") if part)
    return ".".join(target_parts)
