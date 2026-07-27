"""Unit tests for ignore/exclusion policy (T016)."""

from __future__ import annotations

from pathlib import Path

from app.security.ignore_policy import IgnorePolicy


def _touch(path: Path, data: bytes | str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def test_hard_excludes_env_node_modules_dist_git(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / "src" / "main.py", "print(1)")
    _touch(root / ".env", "SECRET=1")
    _touch(root / "node_modules" / "pkg" / "index.js", "module.exports=1")
    _touch(root / "dist" / "bundle.js", "var a=1")
    # Avoid writing under a real .git/ tree (sandbox / OS may block); still assert policy.
    git_config = root / ".git" / "config"
    policy = IgnorePolicy.from_repo(root)
    assert policy.is_hard_excluded_dir(".git")
    assert policy.is_excluded(git_config)
    assert policy.is_excluded(root / ".env")
    assert policy.is_excluded(root / "node_modules" / "pkg" / "index.js")
    assert policy.is_excluded(root / "dist" / "bundle.js")
    _touch(root / "secrets.yaml", "password: x")
    assert policy.is_excluded(root / "secrets.yaml")
    assert not policy.is_excluded(root / "src" / "main.py")


def test_gitignore_patterns_respected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / ".gitignore", "*.log\nbuild/\n")
    _touch(root / "app.py", "x")
    _touch(root / "debug.log", "noise")
    _touch(root / "build" / "out.txt", "y")

    policy = IgnorePolicy.from_repo(root)
    assert policy.is_excluded(root / "debug.log")
    assert policy.is_excluded(root / "build" / "out.txt")
    assert not policy.is_excluded(root / "app.py")


def test_binary_extension_excluded(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / "photo.png", b"\x89PNG\r\n\x1a\n")
    policy = IgnorePolicy.from_repo(root)
    assert policy.is_excluded(root / "photo.png")
    assert policy.is_binary_file(root / "photo.png")
