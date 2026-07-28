from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters import l1_parser as l1_parser_mod
from app.adapters.l1_parser import TreeSitterL1Parser


def _parser() -> TreeSitterL1Parser:
    # Unit tests exercise grammar logic in-process; crash isolation has its own test.
    return TreeSitterL1Parser(isolate_crashes=False)


CASES = {
    "auth.py": "import os\nclass Auth:\n def validate(self):\n  return check()\n",
    "auth.js": "import x from './x'; class Auth { validate() { return check(); } }\n",
    "auth.ts": "import {x} from './x'; class Auth { validate(): boolean { return check(); } }\n",
    "auth.tsx": "import React from 'react'; function Auth(){ return render(); }\n",
    "auth.go": (
        'package auth\nimport "fmt"\ntype Auth struct{}\n'
        'func Validate(){ fmt.Println("x") }\n'
    ),
    "Auth.java": "import java.util.List; class Auth { void validate(){ check(); } }\n",
}


@pytest.mark.parametrize(("name", "source"), CASES.items())
def test_parser_extracts_typed_nodes_and_imports(
    tmp_path: Path, name: str, source: str
) -> None:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    result = _parser().parse_paths("fixture", tmp_path, [path], "rev-1")
    kinds = {node.entity_kind for node in result.nodes}
    assert {"File", "Module"}.issubset(kinds)
    assert any(edge.edge_kind == "IMPORTS" for edge in result.edges)
    assert all(node.index_revision == "rev-1" for node in result.nodes)
    assert all(
        not hasattr(node, "source") and not hasattr(node, "content")
        for node in result.nodes
    )


def test_malformed_supported_source_uses_import_only_fallback(tmp_path: Path) -> None:
    path = tmp_path / "bad.py"
    path.write_text("import os\nclass Broken(\n secret_call()\n", encoding="utf-8")
    result = _parser().parse_paths("fixture", tmp_path, [path], "rev")
    assert result.malformed_files == 1
    assert {node.entity_kind for node in result.nodes} <= {"File", "Module"}
    assert any(edge.edge_kind == "IMPORTS" for edge in result.edges)


def test_unsupported_file_is_counted_without_nodes(tmp_path: Path) -> None:
    path = tmp_path / "notes.rb"
    path.write_text("class Secret; end", encoding="utf-8")
    result = _parser().parse_paths("fixture", tmp_path, [path], "rev")
    assert result.unsupported_files == 1
    assert result.nodes == []


def test_parser_resolves_local_imports_as_file_to_file_edges(tmp_path: Path) -> None:
    source = tmp_path / "auth.py"
    target = tmp_path / "tokens.py"
    source.write_text("import tokens\n", encoding="utf-8")
    target.write_text("def check():\n return True\n", encoding="utf-8")

    result = _parser().parse_paths(
        "fixture", tmp_path, [target, source], "rev"
    )
    nodes = {node.entity_id: node for node in result.nodes}
    file_imports = [
        edge
        for edge in result.edges
        if edge.edge_kind == "IMPORTS"
        and nodes[edge.source_id].entity_kind == "File"
        and nodes[edge.target_id].entity_kind == "File"
    ]

    assert len(file_imports) == 1
    assert nodes[file_imports[0].source_id].source_path == "auth.py"
    assert nodes[file_imports[0].target_id].source_path == "tokens.py"


def test_parser_resolves_python_relative_import_to_sibling_file(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    source = package / "auth.py"
    target = package / "tokens.py"
    source.write_text("from .tokens import check\n", encoding="utf-8")
    target.write_text("def check():\n return True\n", encoding="utf-8")

    result = _parser().parse_paths(
        "fixture", tmp_path, [target, source], "rev"
    )
    nodes = {node.entity_id: node for node in result.nodes}
    file_imports = [
        edge
        for edge in result.edges
        if edge.edge_kind == "IMPORTS"
        and nodes[edge.source_id].entity_kind == "File"
        and nodes[edge.target_id].entity_kind == "File"
    ]

    assert len(file_imports) == 1
    assert nodes[file_imports[0].source_id].source_path == "pkg/auth.py"
    assert nodes[file_imports[0].target_id].source_path == "pkg/tokens.py"


def test_crash_isolation_falls_back_for_poison_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    good = tmp_path / "good.py"
    bad = tmp_path / "poison.py"
    good.write_text("import os\ndef ok():\n return 1\n", encoding="utf-8")
    bad.write_text("import sys\ndef boom():\n return 2\n", encoding="utf-8")

    def fake_try(repo, root, paths, revision):
        if any(p.name == "poison.py" for p in paths):
            return None
        return TreeSitterL1Parser(isolate_crashes=False)._parse_paths_inprocess(
            repo, root, paths, revision
        )

    monkeypatch.setattr(l1_parser_mod, "_try_parse_in_subprocess", fake_try)
    result = TreeSitterL1Parser(isolate_crashes=True).parse_paths(
        "fixture", tmp_path, [good, bad], "rev"
    )
    assert result.malformed_files == 1
    assert result.parsed_files >= 2
    paths = {n.source_path for n in result.nodes if n.entity_kind == "File"}
    assert paths == {"good.py", "poison.py"}
    assert any(n.entity_kind == "Method" and "ok" in n.qualified_name for n in result.nodes)
