"""Unit tests for filesystem walker (EP-005 T010 / FR-001, FR-002).

walk_allowed_files must never yield fixture excluded paths.
"""

from __future__ import annotations

from pathlib import Path

from app.adapters.fs_walker import walk_allowed_files, walk_with_stats
from tests.fixtures.ignore_exclusion_repo import (
    ALLOWED_REL_PATHS,
    EXCLUDED_REL_PATHS,
    materialize_ignore_exclusion_repo,
)


def _touch(path: Path, data: str | bytes = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def test_walker_skips_excluded_and_binaries(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / "src" / "a.py", "a=1")
    _touch(root / ".env", "K=V")
    _touch(root / "node_modules" / "x" / "y.js", "1")
    _touch(root / "logo.png", b"\x00\x01\x02\x03")
    _touch(root / ".gitignore", "*.tmp\n")
    _touch(root / "skip.tmp", "tmp")

    allowed = walk_allowed_files(root)
    rels = [p.relative_to(root).as_posix() for p in allowed]
    assert "src/a.py" in rels
    assert ".env" not in rels
    assert "skip.tmp" not in rels
    assert not any("node_modules" in r for r in rels)
    assert "logo.png" not in rels

    _, stats = walk_with_stats(root)
    assert stats.files_allowed >= 1
    assert stats.files_excluded >= 3


def test_walker_shared_fixture_never_yields_excluded(tmp_path: Path) -> None:
    root = materialize_ignore_exclusion_repo(tmp_path / "fixture_repo")
    allowed = walk_allowed_files(root)
    rels = {p.relative_to(root).as_posix() for p in allowed}
    for excl in EXCLUDED_REL_PATHS:
        assert excl not in rels, f"walker leaked excluded path: {excl}"
    for ok in ALLOWED_REL_PATHS:
        assert ok in rels, f"walker missing allowed path: {ok}"
