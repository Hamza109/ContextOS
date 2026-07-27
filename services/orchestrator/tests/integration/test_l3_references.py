"""Integration: monorepo references + 2-line context (T039; SC-003)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.serena_mcp import (
    InMemorySerenaDouble,
    SerenaMCPAdapter,
    SerenaMCPConfig,
    SerenaReferencePayload,
)
from app.services.l3_symbol import REFERENCE_CONTEXT_LINES, SymbolService


def test_references_with_two_line_context(tmp_path: Path) -> None:
    src = tmp_path / "mod.py"
    src.write_text(
        "\n".join(
            [
                "def helper():",
                "    pass",
                "",
                "def caller():",
                "    helper()  # call site",
                "    return 1",
                "    # after",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    session = InMemorySerenaDouble(
        references={
            "helper": [
                SerenaReferencePayload(path=str(src), line=5, column=4),
            ]
        }
    )
    svc = SymbolService(
        adapter=SerenaMCPAdapter(SerenaMCPConfig(use_test_double=True), session=session),
        workspace_root=tmp_path,
    )
    hits = svc.find_references(path=str(src), line=1, symbol="helper")
    assert len(hits) == 1
    hit = hits[0]
    assert hit.file_line.endswith(":5")
    assert len(hit.context_before) == REFERENCE_CONTEXT_LINES
    assert len(hit.context_after) <= REFERENCE_CONTEXT_LINES
    assert "helper()" in (hit.line_text or "")
