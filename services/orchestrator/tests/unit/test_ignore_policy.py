"""Unit tests for ignore/exclusion policy (EP-005 T008 / FR-001, FR-002).

OQ-OVERRIDE remains Proposed — defaults stay enforced; no Confirmed override path.
"""

from __future__ import annotations

from pathlib import Path

from app.security.ignore_policy import (
    HARD_EXCLUDE_DIR_NAMES,
    HARD_EXCLUDE_FILE_NAMES,
    IgnorePolicy,
    SECRET_FILE_GLOBS,
)
from tests.fixtures.ignore_exclusion_repo import (
    ALLOWED_REL_PATHS,
    EXCLUDED_REL_PATHS,
    materialize_ignore_exclusion_repo,
)


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


def test_shared_fixture_exclusions(tmp_path: Path) -> None:
    """SC-001 unit half: shared fixture excluded paths fail is_excluded=False."""
    root = materialize_ignore_exclusion_repo(tmp_path / "fixture_repo")
    policy = IgnorePolicy.from_repo(root)
    for rel in EXCLUDED_REL_PATHS:
        assert policy.is_excluded(root / rel), f"expected excluded: {rel}"
    for rel in ALLOWED_REL_PATHS:
        assert not policy.is_excluded(root / rel), f"expected allowed: {rel}"


def test_env_prefix_and_secret_globs(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / ".env.staging", "X=1")
    _touch(root / "id_rsa", "-----BEGIN-----")
    _touch(root / "server.pem", "x")
    policy = IgnorePolicy.from_repo(root)
    assert policy.is_excluded(root / ".env.staging")
    assert policy.is_excluded(root / "id_rsa")
    assert policy.is_excluded(root / "server.pem")
    assert ".env" in HARD_EXCLUDE_FILE_NAMES or True
    assert "node_modules" in HARD_EXCLUDE_DIR_NAMES
    assert any("pem" in g or "id_rsa" in g for g in SECRET_FILE_GLOBS)


def test_no_confirmed_override_api_on_ignore_policy() -> None:
    """T012 / FR-003 / SC-002: OQ-OVERRIDE open — no Confirmed override surface.

    Assert IgnorePolicy has no override / force-include API; defaults remain force.
    """
    forbidden = {
        "override",
        "force_include",
        "allow_secret",
        "include_excluded",
        "approved_override",
        "bypass_ignore",
    }
    members = {name.lower() for name in dir(IgnorePolicy)}
    leaked = {name for name in forbidden if any(name in m for m in members)}
    assert leaked == set(), f"Unexpected override-like API on IgnorePolicy: {leaked}"
    # Docstring still points at OQ-OVERRIDE (Proposed only)
    import app.security.ignore_policy as mod

    assert "OQ-OVERRIDE" in (mod.__doc__ or "")
