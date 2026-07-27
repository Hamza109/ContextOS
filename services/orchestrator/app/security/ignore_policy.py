"""Ignore / hard-exclusion policy for repository walks (FR-010..FR-012; EP-005 FR-001..FR-003).

No override path until OQ-OVERRIDE is clarified — defaults stay enforced (SC-002).
Secret-glob inventory may extend without inventing Confirmed override UX (T020).
US-016 query-time LLM consent is out of scope (cite only).
"""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path

# Hard exclusions — always enforced (constitution III; FR-011). No override (FR-012).
HARD_EXCLUDE_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
        "__pycache__",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "target",
        "vendor",
        ".next",
        "coverage",
        ".idea",
        ".vscode",
    }
)

HARD_EXCLUDE_FILE_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.development",
        ".env.production",
        ".env.staging",
    }
)

SECRET_FILE_GLOBS: tuple[str, ...] = (
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*id_rsa*",
    "*id_ed25519*",
    "*.keystore",
    "credentials.json",
    "secrets.yaml",
    "secrets.yml",
    ".npmrc",
    ".pypirc",
)

BINARY_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".class",
        ".o",
        ".a",
        ".wasm",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp3",
        ".mp4",
        ".mov",
        ".avi",
        ".sqlite",
        ".db",
        ".pyc",
        ".pyo",
        ".whl",
        ".egg",
    }
)


@dataclass
class IgnorePolicy:
    """Single enforcement point for walk/pack/index exclusions."""

    root: Path
    gitignore_patterns: list[str] = field(default_factory=list)

    @classmethod
    def from_repo(cls, repo_path: str | Path) -> IgnorePolicy:
        root = Path(repo_path).resolve()
        patterns: list[str] = []
        gitignore = root / ".gitignore"
        if gitignore.is_file():
            patterns.extend(_parse_gitignore(gitignore))
        return cls(root=root, gitignore_patterns=patterns)

    def is_hard_excluded_dir(self, name: str) -> bool:
        return name in HARD_EXCLUDE_DIR_NAMES

    def is_excluded(self, path: Path) -> bool:
        """Return True if path must not be packed or embedded."""
        try:
            rel = path.resolve().relative_to(self.root)
        except ValueError:
            return True

        parts = rel.parts
        if any(p in HARD_EXCLUDE_DIR_NAMES for p in parts[:-1] if p):
            return True
        if parts and parts[0] in HARD_EXCLUDE_DIR_NAMES:
            return True

        name = path.name
        if name in HARD_EXCLUDE_FILE_NAMES or name.startswith(".env"):
            return True

        rel_posix = rel.as_posix()
        for glob in SECRET_FILE_GLOBS:
            if fnmatch.fnmatch(name, glob) or fnmatch.fnmatch(rel_posix, glob):
                return True

        if path.suffix.lower() in BINARY_EXTENSIONS:
            return True

        if self._matches_gitignore(rel_posix, path.is_dir()):
            return True

        return False

    def is_binary_file(self, path: Path) -> bool:
        if path.suffix.lower() in BINARY_EXTENSIONS:
            return True
        return _looks_binary(path)

    def _matches_gitignore(self, rel_posix: str, is_dir: bool) -> bool:
        for raw in self.gitignore_patterns:
            pattern = raw.strip()
            if not pattern or pattern.startswith("#"):
                continue
            negate = pattern.startswith("!")
            if negate:
                pattern = pattern[1:]
            matched = _gitignore_match(pattern, rel_posix, is_dir)
            if matched and not negate:
                return True
            # Negation patterns are rare; simple MVP: if negated match, do not exclude here.
            # Full gitignore precedence is complex; defaults remain exclude-all for secrets.
        return False


def _parse_gitignore(path: Path) -> list[str]:
    lines: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return lines
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


def _gitignore_match(pattern: str, rel_posix: str, is_dir: bool) -> bool:
    if pattern.endswith("/"):
        if not is_dir and "/" not in rel_posix:
            # directory-only pattern against file name
            pass
        pattern = pattern.rstrip("/")
        candidates = [rel_posix, rel_posix.rstrip("/")]
        for c in candidates:
            if fnmatch.fnmatch(c, pattern) or fnmatch.fnmatch(c.split("/")[0], pattern):
                return True
            # match any path segment
            if any(fnmatch.fnmatch(part, pattern) for part in c.split("/")):
                return True
        return False

    if pattern.startswith("/"):
        pattern = pattern[1:]
        return fnmatch.fnmatch(rel_posix, pattern)

    if "/" in pattern:
        return fnmatch.fnmatch(rel_posix, pattern) or fnmatch.fnmatch(
            os.path.basename(rel_posix), pattern
        )

    # Match basename or any path segment
    if fnmatch.fnmatch(os.path.basename(rel_posix), pattern):
        return True
    return any(fnmatch.fnmatch(part, pattern) for part in rel_posix.split("/"))


def _looks_binary(path: Path, sample_size: int = 8192) -> bool:
    if not path.is_file():
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(sample_size)
    except OSError:
        return True
    if b"\x00" in chunk:
        return True
    # High proportion of non-text bytes
    if not chunk:
        return False
    text_chars = sum(1 for b in chunk if b in b"\t\n\r" or 32 <= b <= 126)
    return (text_chars / len(chunk)) < 0.75
