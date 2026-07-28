"""Phase-aware code2prompt-style packing (US-004).

Five SDLC phases: Requirements / Design / Dev / Test / Deploy.
Concrete code2prompt package pin NEEDS CLARIFICATION — in-house templates (OQ / T040).
Phase wire remains OQ-16 Proposed only. No L4 Headroom gate (ADR-006).
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

from app.services.l5_citations import attach_citations
from app.services.l5_pack import estimate_tokens
from app.services.l5_search import SearchHit

SUPPORTED_PHASES = ("Requirements", "Design", "Dev", "Test", "Deploy")
DEFAULT_PHASE = "Dev"


@dataclass(frozen=True)
class PhasePackResult:
    final_context: str
    tokens_before: int
    tokens_after: int
    saving_percent: float
    phase: str


# Phase scoping: which hit facets / prompt sections to emphasize (composition MUST differ).
_PHASE_TEMPLATES: dict[str, dict[str, str]] = {
    "Requirements": {
        "title": "Requirements-oriented context pack",
        "focus": "user goals, acceptance criteria, constraints, and stakeholder intent",
        "section": "requirements_signals",
        "include_tests": "false",
        "include_impl": "summary",
        "include_interfaces": "true",
    },
    "Design": {
        "title": "Design-oriented context pack",
        "focus": "architecture, interfaces, module boundaries, and data flow",
        "section": "design_artifacts",
        "include_tests": "false",
        "include_impl": "signatures",
        "include_interfaces": "true",
    },
    "Dev": {
        "title": "Development-oriented context pack",
        "focus": "implementation details, call sites, and editable source",
        "section": "dev_sources",
        "include_tests": "adjacent",
        "include_impl": "full",
        "include_interfaces": "true",
    },
    "Test": {
        "title": "Test-oriented context pack",
        "focus": "test targets, fixtures, assertions, and coverage gaps",
        "section": "test_focus",
        "include_tests": "primary",
        "include_impl": "under_test",
        "include_interfaces": "false",
    },
    "Deploy": {
        "title": "Deploy-oriented context pack",
        "focus": "runtime config, entrypoints, ops surface, and release risks",
        "section": "deploy_surface",
        "include_tests": "smoke",
        "include_impl": "entrypoints",
        "include_interfaces": "ops",
    },
}


def normalize_phase(phase: str | None) -> str:
    if phase is None or not str(phase).strip():
        return DEFAULT_PHASE
    if phase not in SUPPORTED_PHASES:
        raise ValueError(
            f"unsupported phase {phase!r}; expected one of {list(SUPPORTED_PHASES)} "
            "(Proposed OQ-16)"
        )
    return phase


def pack_for_phase(
    hits: list[SearchHit],
    *,
    query: str,
    repo: str,
    phase: str | None = None,
    include_citations: bool = True,
) -> PhasePackResult:
    """Assemble phase-scoped final_context. Composition differs by phase for same hits."""
    selected = normalize_phase(phase)
    tmpl = _PHASE_TEMPLATES[selected]

    # tokens_before: raw candidate content estimate (Proposed MVP packing semantics)
    raw = "\n".join(h.content or h.path for h in hits)
    tokens_before = estimate_tokens(raw) if raw.strip() else 0

    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<context_pack phase="{escape(selected)}" repo="{escape(repo)}" '
        f'template="code2prompt-style-inhouse">',
        f'  <meta title="{escape(tmpl["title"])}" focus="{escape(tmpl["focus"])}" '
        f'section="{escape(tmpl["section"])}" '
        f'include_tests="{escape(tmpl["include_tests"])}" '
        f'include_impl="{escape(tmpl["include_impl"])}" '
        f'include_interfaces="{escape(tmpl["include_interfaces"])}" />',
        f'  <query><![CDATA[{_safe_cdata(query)}]]></query>',
        f'  <{tmpl["section"]}>',
    ]

    for i, hit in enumerate(hits):
        excerpt = _phase_excerpt(hit, selected)
        line = hit.start_line if hit.start_line is not None else 1
        parts.append(
            f'    <file path="{escape(hit.path)}" rank="{i + 1}" '
            f'score="{hit.score:.6f}" start_line="{line}" '
            f'phase_role="{escape(_phase_role(hit, selected))}">'
        )
        parts.append(f"      <![CDATA[{_safe_cdata(excerpt)}]]>")
        parts.append("    </file>")

    parts.append(f"  </{tmpl['section']}>")
    parts.append("</context_pack>")
    body = "\n".join(parts)

    if include_citations:
        body = attach_citations(body, hits)

    tokens_after = estimate_tokens(body)
    if tokens_before > 0:
        saving = max(0.0, (tokens_before - tokens_after) / tokens_before * 100.0)
    else:
        saving = 0.0

    return PhasePackResult(
        final_context=body,
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        saving_percent=round(saving, 4),
        phase=selected,
    )


def _phase_role(hit: SearchHit, phase: str) -> str:
    path = hit.path.lower()
    is_test = "test" in path or path.endswith("_test.py") or "/tests/" in path
    if phase == "Test":
        return "primary_test" if is_test else "under_test"
    if phase == "Requirements":
        return "requirement_signal"
    if phase == "Design":
        return "design_surface"
    if phase == "Deploy":
        return "deploy_entrypoint" if any(
            x in path for x in ("main.", "docker", "deploy", "compose", "config")
        ) else "runtime_related"
    return "implementation"


def _phase_excerpt(hit: SearchHit, phase: str) -> str:
    content = hit.content or ""
    lines = content.splitlines()
    if phase == "Requirements":
        # Prefer leading docstring / comments / headings
        head = "\n".join(lines[:12])
        return f"[REQUIREMENTS VIEW]\n{head}"
    if phase == "Design":
        # Prefer signatures / imports
        sigs = [ln for ln in lines if ln.strip().startswith(("def ", "class ", "import ", "from "))]
        body = "\n".join(sigs[:20]) if sigs else "\n".join(lines[:20])
        return f"[DESIGN VIEW]\n{body}"
    if phase == "Test":
        return "[TEST VIEW]\n" + "\n".join(lines[:40])
    if phase == "Deploy":
        return "[DEPLOY VIEW]\n" + "\n".join(lines[:25])
    # Dev — fuller implementation
    return "[DEV VIEW]\n" + "\n".join(lines[:60])


def _safe_cdata(text: str) -> str:
    return (text or "").replace("]]>", "]]]]><![CDATA[>")
