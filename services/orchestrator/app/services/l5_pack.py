"""Repomix-style in-house packer (OQ-PACKER — package not Confirmed-pinned).

Behavioral FR-001/002/003/004 only; pack field inventory not frozen (OQ-PACK).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from app.adapters.fs_walker import walk_with_stats
from app.config import Settings, get_settings
from app.security.ignore_policy import IgnorePolicy

# Approximate token estimate: whitespace/punctuation split (FR-002 behavioral).
# Exact tokenizer not Confirmed for pack pre-calc.
_TOKEN_SPLIT = re.compile(r"\s+|(?=[^\w\s])|(?<=[^\w\s])")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    parts = [p for p in _TOKEN_SPLIT.split(text) if p and not p.isspace()]
    return max(1, len(parts)) if text.strip() else 0


@dataclass(frozen=True)
class PackResult:
    """Minimal pack artifact — do not invent Confirmed schema fields (FR-022)."""

    repo_name: str
    xml_content: str
    token_count: int
    files_packed: int
    files_excluded: int
    artifact_path: Path | None


def pack_repository(
    repo_path: str | Path,
    repo_name: str,
    *,
    settings: Settings | None = None,
    paths_filter: list[str] | None = None,
) -> PackResult:
    """Produce XML-oriented LLM-optimized flatten with token pre-calc; skip binaries."""
    root = Path(repo_path).resolve()
    policy = IgnorePolicy.from_repo(root)
    files, stats = walk_with_stats(root, policy)

    if paths_filter:
        wanted = {_normalize_rel(root, p) for p in paths_filter}
        files = [f for f in files if f.relative_to(root).as_posix() in wanted]

    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<repository name="{escape(repo_name)}" path="{escape(str(root))}">',
    ]
    packed = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Defense-in-depth binary skip
        if "\x00" in content:
            continue
        parts.append(f'  <file path="{escape(rel)}">')
        parts.append(f"    <![CDATA[{_safe_cdata(content)}]]>")
        parts.append("  </file>")
        packed += 1
    parts.append("</repository>")
    xml_content = "\n".join(parts)
    token_count = estimate_tokens(xml_content)

    cfg = settings or get_settings()
    artifact_path = _persist_pack(cfg, repo_name, xml_content)

    return PackResult(
        repo_name=repo_name,
        xml_content=xml_content,
        token_count=token_count,
        files_packed=packed,
        files_excluded=stats.files_excluded,
        artifact_path=artifact_path,
    )


def _safe_cdata(text: str) -> str:
    # Avoid breaking CDATA if content contains ]]>
    return text.replace("]]>", "]]]]><![CDATA[>")


def _normalize_rel(root: Path, p: str) -> str:
    path = Path(p)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def _persist_pack(settings: Settings, repo_name: str, xml_content: str) -> Path | None:
    """Proposed provisional cache keyed by repo_name (T018 / OQ-PACK)."""
    try:
        cache_dir = Path(settings.pack_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w.\-]+", "_", repo_name) or "repo"
        digest = hashlib.sha256(xml_content.encode("utf-8")).hexdigest()[:12]
        out = cache_dir / f"{safe}.pack.xml"
        out.write_text(xml_content, encoding="utf-8")
        meta = cache_dir / f"{safe}.pack.meta"
        meta.write_text(f"token_estimate_sha256_prefix={digest}\n", encoding="utf-8")
        return out
    except OSError:
        return None
