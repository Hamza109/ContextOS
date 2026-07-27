"""Unit tests for phase templates — distinct composition (T041)."""

from __future__ import annotations

from app.services.l5_phase_pack import SUPPORTED_PHASES, pack_for_phase
from app.services.l5_search import SearchHit

HITS = [
    SearchHit(
        path="src/auth.py",
        score=0.9,
        content="def login():\n    return True\n\nclass AuthService:\n    pass\n",
        start_line=1,
    ),
    SearchHit(
        path="tests/test_auth.py",
        score=0.7,
        content="def test_login():\n    assert login()\n",
        start_line=1,
    ),
]


def test_five_phases_produce_distinct_composition() -> None:
    packs = {
        phase: pack_for_phase(HITS, query="auth", repo="demo", phase=phase, include_citations=False)
        for phase in SUPPORTED_PHASES
    }
    bodies = {p: packs[p].final_context for p in SUPPORTED_PHASES}
    # Each phase embeds its section name / view marker differently
    assert len(set(bodies.values())) == 5
    for phase in SUPPORTED_PHASES:
        assert f'phase="{phase}"' in bodies[phase]


def test_default_phase_is_dev() -> None:
    packed = pack_for_phase(HITS, query="auth", repo="demo", phase=None, include_citations=False)
    assert packed.phase == "Dev"
    assert 'phase="Dev"' in packed.final_context
