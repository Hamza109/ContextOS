"""Unit: L4 relevance ordering (EP-008 T008)."""

from __future__ import annotations

from app.services.l4_relevance import RelevanceUnit, score_unit, score_units


def test_higher_hit_score_ranks_first() -> None:
    units = [
        RelevanceUnit("low.py", "x", hit_score=0.1, phase_role="implementation"),
        RelevanceUnit("high.py", "y", hit_score=0.9, phase_role="implementation"),
    ]
    ranked = score_units(units)
    assert ranked[0].path == "high.py"
    assert ranked[0].score > ranked[1].score


def test_phase_role_boost_applied() -> None:
    plain = score_unit(RelevanceUnit("a.py", "x", hit_score=0.5, phase_role="implementation"))
    entry = score_unit(RelevanceUnit("main.py", "x", hit_score=0.5, phase_role="deploy_entrypoint"))
    assert entry.score > plain.score
    assert any("phase_role=" in r for r in entry.reasons)


def test_recency_only_when_present() -> None:
    without = score_unit(RelevanceUnit("a.py", "x", hit_score=0.4, phase_role="implementation"))
    with_rec = score_unit(
        RelevanceUnit("a.py", "x", hit_score=0.4, phase_role="implementation", recency=1.0)
    )
    assert with_rec.score > without.score
    assert not any(r.startswith("recency") for r in without.reasons)
    assert any(r.startswith("recency") for r in with_rec.reasons)
