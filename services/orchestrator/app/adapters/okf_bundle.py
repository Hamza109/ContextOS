"""Proposed OKF v0.2 on-disk bundle adapter (EP-013).

Concept ID = path relative to bundle root without ``.md``.
Reserved files ``index.md`` / ``log.md`` are not concepts.
Malformed concepts are skipped with counts only — never fabricated.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_RESERVED = frozenset({"index.md", "log.md"})
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)


@dataclass(frozen=True)
class OkfConcept:
    """Parsed OKF concept (metadata + markdown body)."""

    concept_id: str
    type: str
    title: str
    description: str
    tags: list[str]
    frontmatter: dict[str, Any]
    body: str
    relative_path: str  # path under bundle root including .md

    @property
    def sources(self) -> list[Any]:
        raw = self.frontmatter.get("sources")
        return list(raw) if isinstance(raw, list) else []

    @property
    def generated(self) -> dict[str, Any] | None:
        raw = self.frontmatter.get("generated")
        return dict(raw) if isinstance(raw, dict) else None


@dataclass
class OkfBundleStats:
    concepts_written: int = 0
    concepts_listed: int = 0
    malformed_skipped: int = 0


@dataclass
class OkfBundle:
    """Repository-scoped OKF directory under ``{okf_cache_dir}/{repo_name}/``."""

    root: Path
    stats: OkfBundleStats = field(default_factory=OkfBundleStats)

    def ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def concept_path(self, concept_id: str) -> Path:
        safe = _normalize_concept_id(concept_id)
        return self.root / f"{safe}.md"

    def write_concept(
        self,
        concept_id: str,
        *,
        type: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        sources: list[dict[str, Any]] | None = None,
        generated: dict[str, Any] | None = None,
        repo: str | None = None,
        index_revision: str | None = None,
        body: str = "",
        extra_frontmatter: dict[str, Any] | None = None,
    ) -> Path:
        """Write one concept file with required ``type`` frontmatter."""
        self.ensure_root()
        safe_id = _normalize_concept_id(concept_id)
        if not type or not str(type).strip():
            raise ValueError("OKF concept requires non-empty type")
        fm: dict[str, Any] = {
            "type": str(type).strip(),
            "title": title or safe_id,
            "description": description or "",
            "tags": list(tags or []),
        }
        if sources is not None:
            fm["sources"] = sources
        if generated is not None:
            fm["generated"] = generated
        if repo is not None:
            fm["repo"] = repo
        if index_revision is not None:
            fm["index_revision"] = index_revision
        if extra_frontmatter:
            for key, value in extra_frontmatter.items():
                if key not in fm:
                    fm[key] = value
        path = self.concept_path(safe_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
        content = f"---\n{dumped}\n---\n\n{(body or '').rstrip()}\n"
        path.write_text(content, encoding="utf-8")
        self.stats.concepts_written += 1
        return path

    def read_concept(self, concept_id: str) -> OkfConcept | None:
        path = self.concept_path(concept_id)
        if not path.is_file():
            return None
        parsed = _parse_concept_file(path, self.root)
        if parsed is None:
            self.stats.malformed_skipped += 1
            return None
        return parsed

    def list_concepts(self) -> list[OkfConcept]:
        """List readable concepts; skip reserved and malformed files."""
        self.ensure_root()
        concepts: list[OkfConcept] = []
        for path in sorted(self.root.rglob("*.md")):
            if path.name in _RESERVED:
                continue
            try:
                path.relative_to(self.root)
            except ValueError:
                continue
            parsed = _parse_concept_file(path, self.root)
            if parsed is None:
                self.stats.malformed_skipped += 1
                continue
            concepts.append(parsed)
        self.stats.concepts_listed = len(concepts)
        return concepts

    def write_index(self, concepts: list[OkfConcept] | None = None) -> Path:
        """Generate reserved ``index.md`` listing concept IDs and titles."""
        self.ensure_root()
        items = concepts if concepts is not None else self.list_concepts()
        lines = [
            "---",
            "type: Index",
            "title: OKF Bundle Index",
            "---",
            "",
            "# OKF Bundle Index",
            "",
        ]
        for concept in items:
            lines.append(f"- [{concept.title}]({concept.concept_id}.md) (`{concept.type}`)")
        lines.append("")
        path = self.root / "index.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def clear_concepts(self) -> None:
        """Remove prior concept markdown (keeps root). Used on full regenerate."""
        if not self.root.exists():
            return
        for path in self.root.rglob("*.md"):
            if path.name in _RESERVED:
                continue
            path.unlink(missing_ok=True)


def okf_bundle_root(okf_cache_dir: Path, repo_name: str) -> Path:
    """Proposed OQ-OKF-01: ``{cache}/{repo_name}/``."""
    safe = re.sub(r"[^\w.\-]+", "_", repo_name.strip()) or "repo"
    return Path(okf_cache_dir) / safe


def _normalize_concept_id(concept_id: str) -> str:
    cleaned = concept_id.replace("\\", "/").lstrip("./")
    if cleaned.endswith(".md"):
        cleaned = cleaned[:-3]
    if not cleaned or cleaned in {"index", "log"} or ".." in cleaned.split("/"):
        raise ValueError(f"invalid OKF concept id: {concept_id!r}")
    return cleaned


def _parse_concept_file(path: Path, root: Path) -> OkfConcept | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(fm, dict):
        return None
    concept_type = fm.get("type")
    if not concept_type or not str(concept_type).strip():
        # Required OKF field missing → malformed skip
        return None
    rel = path.relative_to(root).as_posix()
    concept_id = rel[:-3] if rel.endswith(".md") else rel
    tags_raw = fm.get("tags") or []
    tags = [str(t) for t in tags_raw] if isinstance(tags_raw, list) else []
    return OkfConcept(
        concept_id=concept_id,
        type=str(concept_type).strip(),
        title=str(fm.get("title") or concept_id),
        description=str(fm.get("description") or ""),
        tags=tags,
        frontmatter=fm,
        body=match.group(2).strip(),
        relative_path=rel,
    )


def extract_markdown_links(body: str) -> list[str]:
    """Return linked concept IDs from standard markdown links (paths without .md)."""
    ids: list[str] = []
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", body):
        target = match.group(2).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0].replace("\\", "/")
        if ".." in target.split("/"):
            continue
        while target.startswith("./"):
            target = target[2:]
        if target.endswith(".md"):
            target = target[:-3]
        if target:
            ids.append(target)
    return ids
