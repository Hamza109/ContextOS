"""Proposed OKF bundle generator (EP-013 / US-046).

Consumes only IgnorePolicy-allowed FR-002 source paths plus optional L1 metadata
summaries. Concept bodies are metadata/summary oriented — never full source code.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from app.adapters.l1_parser import StructuralNode
from app.adapters.okf_bundle import OkfBundle, OkfConcept, okf_bundle_root
from app.config import Settings, get_settings
from app.security.ignore_policy import IgnorePolicy

logger = logging.getLogger(__name__)

_GENERATOR_ID = "process:contextos-okf-generator"
_SPEC_BASENAMES = frozenset(
    {"spec.md", "plan.md", "tasks.md", "validation-report.md", "review-report.md"}
)
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_MAX_SUMMARY_CHARS = 480
_MAX_L1_CONCEPTS = 40


@dataclass(frozen=True)
class OkfGenerateResult:
    status: str  # ok | disabled | error
    concepts_written: int
    sources_used: int
    duration_ms: int
    index_revision: str
    bundle_root: str | None
    error: str | None = None


def generate_okf_bundle(
    repo_path: Path,
    repo_name: str,
    *,
    settings: Settings | None = None,
    policy: IgnorePolicy | None = None,
    allowed_paths: list[Path] | None = None,
    index_revision: str,
    l1_entities: list[StructuralNode] | None = None,
) -> OkfGenerateResult:
    """Generate or refresh a repository-scoped OKF bundle after eligibility."""
    cfg = settings or get_settings()
    started = time.perf_counter()
    if not cfg.okf_enabled:
        return OkfGenerateResult(
            status="disabled",
            concepts_written=0,
            sources_used=0,
            duration_ms=0,
            index_revision=index_revision,
            bundle_root=None,
        )

    root = Path(repo_path).expanduser().resolve()
    try:
        ignore = policy or IgnorePolicy.from_repo(root)
        allowed = _allowed_set(root, allowed_paths, ignore)
        sources = _select_fr002_sources(root, allowed)
        bundle = OkfBundle(okf_bundle_root(cfg.okf_cache_dir, repo_name))
        bundle.clear_concepts()
        bundle.ensure_root()

        written: list[OkfConcept] = []
        generated_at = datetime.now(UTC).isoformat()
        generated_meta = {"by": _GENERATOR_ID, "at": generated_at}

        for source in sources:
            concept = _emit_doc_concept(
                bundle,
                root=root,
                source=source,
                repo_name=repo_name,
                index_revision=index_revision,
                generated=generated_meta,
            )
            if concept is not None:
                written.append(concept)

        for entity in (l1_entities or [])[:_MAX_L1_CONCEPTS]:
            concept = _emit_structural_concept(
                bundle,
                entity=entity,
                repo_name=repo_name,
                index_revision=index_revision,
                generated=generated_meta,
            )
            if concept is not None:
                written.append(concept)

        _rewrite_related_links(bundle, written)
        bundle.write_index(written)
        duration_ms = int((time.perf_counter() - started) * 1000)
        return OkfGenerateResult(
            status="ok",
            concepts_written=len(written),
            sources_used=len(sources),
            duration_ms=duration_ms,
            index_revision=index_revision,
            bundle_root=str(bundle.root),
        )
    except Exception as exc:  # noqa: BLE001 — OKF must not break Confirmed index
        logger.warning("OKF generation failed for repo=%s: %s", repo_name, exc, exc_info=True)
        return OkfGenerateResult(
            status="error",
            concepts_written=0,
            sources_used=0,
            duration_ms=int((time.perf_counter() - started) * 1000),
            index_revision=index_revision,
            bundle_root=None,
            error=type(exc).__name__,
        )


def _allowed_set(
    root: Path,
    allowed_paths: list[Path] | None,
    policy: IgnorePolicy,
) -> set[str]:
    if allowed_paths is not None:
        out: set[str] = set()
        for path in allowed_paths:
            resolved = path.resolve()
            if policy.is_excluded(resolved):
                continue
            try:
                out.add(resolved.relative_to(root).as_posix())
            except ValueError:
                continue
        return out
    # Fallback: caller should supply allowed_paths; empty means no sources.
    return set()


def _select_fr002_sources(root: Path, allowed: set[str]) -> list[Path]:
    selected: list[Path] = []
    for rel in sorted(allowed):
        if not rel.endswith(".md"):
            continue
        if rel.startswith("docs/architecture/"):
            selected.append(root / rel)
            continue
        if rel == "docs/backlog/user-stories.md":
            selected.append(root / rel)
            continue
        parts = Path(rel).parts
        if (
            len(parts) >= 3
            and parts[0] == "specs"
            and parts[-1] in _SPEC_BASENAMES
        ):
            selected.append(root / rel)
    return selected


def _emit_doc_concept(
    bundle: OkfBundle,
    *,
    root: Path,
    source: Path,
    repo_name: str,
    index_revision: str,
    generated: dict[str, Any],
) -> OkfConcept | None:
    rel = source.relative_to(root).as_posix()
    try:
        text = source.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    concept_type = _type_for_source(rel)
    title = _title_from_markdown(text) or Path(rel).stem.replace("-", " ").title()
    description = _summary_from_markdown(text)
    tags = _tags_for_source(rel, concept_type)
    concept_id = rel[:-3] if rel.endswith(".md") else rel
    body = _metadata_body(title=title, description=description, source_rel=rel, tags=tags)
    path = bundle.write_concept(
        concept_id,
        type=concept_type,
        title=title,
        description=description,
        tags=tags,
        sources=[{"uri": rel}],
        generated=generated,
        repo=repo_name,
        index_revision=index_revision,
        body=body,
    )
    return bundle.read_concept(concept_id) or OkfConcept(
        concept_id=concept_id,
        type=concept_type,
        title=title,
        description=description,
        tags=tags,
        frontmatter={},
        body=body,
        relative_path=path.relative_to(bundle.root).as_posix(),
    )


def _emit_structural_concept(
    bundle: OkfBundle,
    *,
    entity: StructuralNode,
    repo_name: str,
    index_revision: str,
    generated: dict[str, Any],
) -> OkfConcept | None:
    # Metadata-only: qualified name, kind, path, lines — never source body.
    safe_entity = re.sub(r"[^\w.\-]+", "_", entity.entity_id) or "entity"
    concept_id = f"structural/{safe_entity}"
    title = entity.qualified_name or entity.entity_id
    description = (
        f"{entity.entity_kind} at {entity.source_path}:"
        f"{entity.start_line}-{entity.end_line}"
    )
    tags = ["structural", entity.entity_kind.lower(), "l1"]
    body = "\n".join(
        [
            f"# {title}",
            "",
            f"- Kind: `{entity.entity_kind}`",
            f"- Path: `{entity.source_path}`",
            f"- Lines: {entity.start_line}-{entity.end_line}",
            f"- Entity ID: `{entity.entity_id}`",
            "",
            "_Metadata summary only — source code is not duplicated._",
            "",
        ]
    )
    bundle.write_concept(
        concept_id,
        type="Structural Entity",
        title=title,
        description=description,
        tags=tags,
        sources=[{"uri": entity.source_path, "entity_id": entity.entity_id}],
        generated=generated,
        repo=repo_name,
        index_revision=index_revision or entity.index_revision,
        body=body,
    )
    return bundle.read_concept(concept_id)


def _rewrite_related_links(bundle: OkfBundle, concepts: list[OkfConcept]) -> None:
    """Add bounded markdown links between architecture/spec concepts."""
    by_type: dict[str, list[OkfConcept]] = {}
    for concept in concepts:
        by_type.setdefault(concept.type, []).append(concept)

    architecture = by_type.get("Architecture Doc", [])
    specs = [
        c
        for t in ("Spec", "Plan", "Tasks", "Validation Report", "Review Report")
        for c in by_type.get(t, [])
    ]
    backlog = by_type.get("User Story", [])

    for concept in concepts:
        related: list[OkfConcept] = []
        if concept.type == "Architecture Doc":
            related.extend(specs[:3])
            related.extend(backlog[:1])
        elif concept.type in {"Spec", "Plan", "Tasks", "Validation Report", "Review Report"}:
            related.extend(architecture[:2])
            related.extend(backlog[:1])
        elif concept.type == "User Story":
            related.extend(architecture[:2])
            related.extend(specs[:2])
        elif concept.type == "Structural Entity":
            related.extend(architecture[:1])
        related = [r for r in related if r.concept_id != concept.concept_id][:5]
        if not related:
            continue
        link_lines = ["", "## Related", ""]
        for rel in related:
            link_lines.append(f"- [{rel.title}]({rel.concept_id}.md)")
        link_lines.append("")
        # Re-write preserving frontmatter fields
        fm = dict(concept.frontmatter)
        bundle.write_concept(
            concept.concept_id,
            type=concept.type,
            title=concept.title,
            description=concept.description,
            tags=concept.tags,
            sources=fm.get("sources") if isinstance(fm.get("sources"), list) else None,
            generated=fm.get("generated") if isinstance(fm.get("generated"), dict) else None,
            repo=str(fm["repo"]) if fm.get("repo") is not None else None,
            index_revision=(
                str(fm["index_revision"]) if fm.get("index_revision") is not None else None
            ),
            body=concept.body.rstrip() + "\n" + "\n".join(link_lines),
        )


def _type_for_source(rel: str) -> str:
    name = Path(rel).name
    if rel.startswith("docs/architecture/"):
        return "Architecture Doc"
    if rel == "docs/backlog/user-stories.md":
        return "User Story"
    mapping = {
        "spec.md": "Spec",
        "plan.md": "Plan",
        "tasks.md": "Tasks",
        "validation-report.md": "Validation Report",
        "review-report.md": "Review Report",
    }
    return mapping.get(name, "Spec")


def _tags_for_source(rel: str, concept_type: str) -> list[str]:
    tags = [concept_type.casefold().replace(" ", "-")]
    if "architecture" in rel:
        tags.append("architecture")
    if rel.startswith("specs/"):
        tags.append("spec-kit")
        parts = Path(rel).parts
        if len(parts) >= 2:
            tags.append(parts[1])
    if "backlog" in rel:
        tags.append("backlog")
    return tags


def _title_from_markdown(text: str) -> str | None:
    match = _HEADING_RE.search(text)
    if match:
        return match.group(1).strip()[:200]
    return None


def _summary_from_markdown(text: str) -> str:
    # Strip simple frontmatter if present, then take first prose paragraph.
    body = text
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4 :]
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            if lines:
                break
            continue
        if stripped.startswith("```"):
            if lines:
                break
            continue
        lines.append(stripped)
        if sum(len(x) for x in lines) >= _MAX_SUMMARY_CHARS:
            break
    summary = " ".join(lines).strip()
    if len(summary) > _MAX_SUMMARY_CHARS:
        summary = summary[: _MAX_SUMMARY_CHARS - 1].rstrip() + "…"
    return summary


def _metadata_body(*, title: str, description: str, source_rel: str, tags: Iterable[str]) -> str:
    tag_list = ", ".join(f"`{t}`" for t in tags) or "_none_"
    return "\n".join(
        [
            f"# {title}",
            "",
            description or "_No summary extracted._",
            "",
            f"- Source: `{source_rel}`",
            f"- Tags: {tag_list}",
            "",
            "_Metadata/summary only — full source text is not duplicated into OKF._",
            "",
        ]
    )
