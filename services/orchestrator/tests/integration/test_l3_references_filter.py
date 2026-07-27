"""Integration: file-type filter on references (T040; SC-004)."""

from __future__ import annotations

from app.adapters.serena_mcp import (
    InMemorySerenaDouble,
    SerenaMCPAdapter,
    SerenaMCPConfig,
    SerenaReferencePayload,
)
from app.services.l3_symbol import SymbolService


def test_references_file_type_filter() -> None:
    session = InMemorySerenaDouble(
        references={
            "foo": [
                SerenaReferencePayload(path="a.py", line=1),
                SerenaReferencePayload(path="b.ts", line=2),
                SerenaReferencePayload(path="c.py", line=3),
            ]
        }
    )
    svc = SymbolService(
        adapter=SerenaMCPAdapter(SerenaMCPConfig(use_test_double=True), session=session)
    )
    all_hits = svc.find_references(path="a.py", line=1, symbol="foo")
    assert len(all_hits) == 3
    py_only = svc.find_references(
        path="a.py", line=1, symbol="foo", file_types=[".py"]
    )
    assert [h.path for h in py_only] == ["a.py", "c.py"]
    empty = svc.find_references(
        path="a.py", line=1, symbol="foo", file_types=[".rs"]
    )
    assert empty == []
