"""Citation attribute presence — file:line + confidence (T051); no invented JSON keys."""

from __future__ import annotations

from app.services.l5_citations import attach_citations, citations_present, format_citation_xml
from app.services.l5_citations import citation_for_hit
from app.services.l5_search import SearchHit


def test_citation_xml_has_file_line_and_confidence() -> None:
    hit = SearchHit(path="src/a.py", score=0.82, content="x=1\n", start_line=3)
    cit = citation_for_hit(hit)
    xml = format_citation_xml(cit)
    assert 'path="src/a.py"' in xml
    assert 'line="3"' in xml
    assert "confidence=" in xml
    assert "file_line=" in xml


def test_attach_citations_present_in_packed_string() -> None:
    body = "<context_pack></context_pack>"
    hits = [SearchHit(path="b.py", score=0.5, content="y", start_line=10)]
    packed = attach_citations(body, hits)
    assert citations_present(packed)
    # Must NOT require invented Confirmed JSON keys like citation_id / sources[]
    assert "citation_id" not in packed
