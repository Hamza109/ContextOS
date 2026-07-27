"""Security: no rename-execution / sandbox APIs in orchestrator (T050; FR-007)."""

from __future__ import annotations

import ast
from pathlib import Path

ORCH_ROOT = Path(__file__).resolve().parents[2] / "app"

# Forbidden product claims for ContextOS rename execution sandbox (BRD §6).
FORBIDDEN_SYMBOLS = {
    "execute_rename",
    "apply_rename",
    "rename_sandbox",
    "run_rename_in_sandbox",
}


def test_no_rename_execution_symbols_in_orchestrator() -> None:
    hits: list[str] = []
    for path in ORCH_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        # Allow comments mentioning out-of-scope; forbid definitions/assignments of APIs
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in FORBIDDEN_SYMBOLS:
                    hits.append(f"{path}:{node.name}")
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in FORBIDDEN_SYMBOLS:
                        hits.append(f"{path}:{t.id}")
    assert hits == [], f"Forbidden rename-execution symbols found: {hits}"


def test_rename_scope_analysis_flags_no_execution() -> None:
    from app.adapters.serena_mcp import InMemorySerenaDouble, SerenaMCPAdapter, SerenaMCPConfig
    from app.services.l3_symbol import SymbolService

    svc = SymbolService(
        adapter=SerenaMCPAdapter(
            SerenaMCPConfig(use_test_double=True), session=InMemorySerenaDouble()
        )
    )
    result = svc.analyze_rename_scope(path="a.py", line=1, symbol="x")
    assert result.execution_supported is False
