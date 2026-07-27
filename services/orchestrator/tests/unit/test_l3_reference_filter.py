"""Unit: file-type filter on references including empty set (T038; FR-005)."""

from __future__ import annotations

from app.services.l3_symbol import ReferenceHit, filter_references_by_file_type


def _hit(path: str, line: int = 1) -> ReferenceHit:
    return ReferenceHit(path=path, line=line, file_line=f"{path}:{line}")


def test_filter_by_py_extension() -> None:
    refs = [_hit("a.py"), _hit("b.ts"), _hit("c.py")]
    filtered = filter_references_by_file_type(refs, [".py", "py"])
    assert [r.path for r in filtered] == ["a.py", "c.py"]


def test_empty_filtered_set_valid() -> None:
    """Empty filtered set conceptually valid — no invented Confirmed empty schema (T036)."""
    refs = [_hit("a.py"), _hit("b.py")]
    filtered = filter_references_by_file_type(refs, [".ts"])
    assert filtered == []


def test_no_filter_returns_all() -> None:
    refs = [_hit("a.py"), _hit("b.ts")]
    assert filter_references_by_file_type(refs, None) == refs
    assert filter_references_by_file_type(refs, []) == refs
