"""Provenance citations — file:line + confidence (US-015 / BRD §14).

OQ-11 OPEN: Proposed interim XML attributes inside packed string.
Do NOT invent Confirmed citation JSON field names.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

from app.services.l5_search import SearchHit


@dataclass(frozen=True)
class Citation:
    path: str
    line: int
    confidence: float


def citation_for_hit(hit: SearchHit) -> Citation:
    """Derive Proposed citation attributes from a search hit."""
    line = hit.start_line if hit.start_line is not None else 1
    # Confidence from fused score clamped to [0, 1] — Proposed heuristic
    conf = max(0.0, min(1.0, float(hit.score)))
    return Citation(path=hit.path, line=int(line), confidence=round(conf, 4))


def format_citation_xml(citation: Citation) -> str:
    """Proposed interim representation (OQ-11): XML attributes, not Confirmed JSON keys."""
    return (
        f'<citation path="{escape(citation.path)}" '
        f'line="{citation.line}" '
        f'confidence="{citation.confidence}" '
        f'file_line="{escape(citation.path)}:{citation.line}" />'
    )


def attach_citations(body: str, hits: list[SearchHit]) -> str:
    """Append a citations block to packed context ensuring file:line + confidence presence."""
    if not hits:
        return body
    lines = [
        body.rstrip(),
        "",
        "<!-- Proposed citations (OQ-11 open — not Confirmed JSON schema) -->",
        "<citations>",
    ]
    for hit in hits:
        cit = citation_for_hit(hit)
        lines.append(f"  {format_citation_xml(cit)}")
    lines.append("</citations>")
    return "\n".join(lines)


def citations_present(packed: str) -> bool:
    """Behavioral check: file:line + confidence attributes appear (no invented JSON keys)."""
    if not packed:
        return False
    has_line = ('line="' in packed) or ("file_line=" in packed) or (":" in packed and "confidence" in packed)
    has_conf = "confidence=" in packed or "confidence:" in packed
    return bool(has_line and has_conf)
