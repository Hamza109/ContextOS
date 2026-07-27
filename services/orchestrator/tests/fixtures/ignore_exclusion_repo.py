"""Shared ignore-exclusion fixture repo for EP-005 SC-001 (T004).

Contains .gitignore-matched paths, .env, secret-like files, node_modules/,
dist/, a .git-shaped path, and a binary sample — for packs and embeddings e2e.

No real secrets; placeholder contents only.
"""

from __future__ import annotations

from pathlib import Path

# Paths that MUST remain excluded from packs/embeddings after policy walk.
EXCLUDED_REL_PATHS: frozenset[str] = frozenset(
    {
        ".env",
        "secrets.yaml",
        "credentials.json",
        "node_modules/pkg/index.js",
        "dist/bundle.js",
        ".git/config",
        "debug.log",  # .gitignore *.log
        "photo.png",
        "ignored_by_gi.txt",  # explicit gitignore entry
    }
)

ALLOWED_REL_PATHS: frozenset[str] = frozenset(
    {
        "src/main.py",
        "README.md",
    }
)


def materialize_ignore_exclusion_repo(root: Path) -> Path:
    """Create a mini-repo under ``root`` with allowed + excluded artifacts.

    Returns the repo root path.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    (root / ".gitignore").write_text("*.log\nignored_by_gi.txt\n", encoding="utf-8")
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "main.py").write_text(
        "def main():\n    return 'safe'\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# fixture\n", encoding="utf-8")

    (root / ".env").write_text("API_KEY=fixture-not-real\n", encoding="utf-8")
    (root / "secrets.yaml").write_text("password: fixture\n", encoding="utf-8")
    (root / "credentials.json").write_text('{"token":"fixture"}\n', encoding="utf-8")

    nm = root / "node_modules" / "pkg"
    nm.mkdir(parents=True, exist_ok=True)
    (nm / "index.js").write_text("module.exports=1\n", encoding="utf-8")

    dist = root / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "bundle.js").write_text("var a=1\n", encoding="utf-8")

    # .git-shaped tree for policy assertions (may be incomplete on some FS).
    git_dir = root / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    (root / "debug.log").write_text("noise\n", encoding="utf-8")
    (root / "ignored_by_gi.txt").write_text("nope\n", encoding="utf-8")
    (root / "photo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")

    return root
