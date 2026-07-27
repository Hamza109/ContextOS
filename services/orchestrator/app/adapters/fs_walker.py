"""Filesystem walker that applies ignore_policy before yielding files."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from app.security.ignore_policy import IgnorePolicy


@dataclass(frozen=True)
class WalkStats:
    files_seen: int
    files_allowed: int
    files_excluded: int


def walk_allowed_files(repo_path: str | Path, policy: IgnorePolicy | None = None) -> list[Path]:
    """Return sorted list of allowed file paths under repo_path."""
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"repo_path is not a readable directory: {root}")

    pol = policy or IgnorePolicy.from_repo(root)
    allowed: list[Path] = []
    for path in _iter_files(root, pol):
        if pol.is_excluded(path):
            continue
        if pol.is_binary_file(path):
            continue
        allowed.append(path)
    return sorted(allowed)


def walk_with_stats(
    repo_path: str | Path, policy: IgnorePolicy | None = None
) -> tuple[list[Path], WalkStats]:
    root = Path(repo_path).resolve()
    pol = policy or IgnorePolicy.from_repo(root)
    allowed: list[Path] = []
    seen = 0
    excluded = 0
    for path in _iter_files(root, pol):
        seen += 1
        if pol.is_excluded(path) or pol.is_binary_file(path):
            excluded += 1
            continue
        allowed.append(path)
    stats = WalkStats(files_seen=seen, files_allowed=len(allowed), files_excluded=excluded)
    return sorted(allowed), stats


def _iter_files(root: Path, policy: IgnorePolicy) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os_walk(root):
        # Prune hard-excluded directories in-place
        dirnames[:] = [d for d in dirnames if not policy.is_hard_excluded_dir(d)]
        current = Path(dirpath)
        for name in filenames:
            yield current / name


def os_walk(root: Path):
    import os

    return os.walk(root)
