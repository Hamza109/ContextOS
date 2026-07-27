"""Unit tests for score fusion + MMR ordering/diversity (T023)."""

from __future__ import annotations

from app.services.l5_search import SearchHit, fuse_scores, mmr_rerank


def test_fuse_scores_combines_channels() -> None:
    fused = fuse_scores(
        {"a.py": 1.0, "b.py": 0.2},
        {"a.py": 0.1, "b.py": 1.0},
        vector_weight=0.5,
        bm25_weight=0.5,
    )
    assert set(fused) == {"a.py", "b.py"}
    # After min-max, both channels contribute; b should not be zero
    assert fused["b.py"] > 0
    assert fused["a.py"] > 0


def test_mmr_prefers_diversity() -> None:
    # Two near-duplicate high scores + one diverse lower score
    candidates = [
        SearchHit(path="a.py", score=1.0, content="alpha beta gamma shared"),
        SearchHit(path="a2.py", score=0.99, content="alpha beta gamma shared"),
        SearchHit(path="c.py", score=0.5, content="unique zebra widget"),
    ]
    selected = mmr_rerank(candidates, lambda_mult=0.5, top_k=2)
    paths = [h.path for h in selected]
    assert paths[0] == "a.py"
    # With diversity penalty, c.py should beat near-duplicate a2.py
    assert "c.py" in paths
    assert "a2.py" not in paths


def test_mmr_respects_top_k() -> None:
    candidates = [
        SearchHit(path=f"f{i}.py", score=1.0 - i * 0.1, content=f"token{i} unique{i}")
        for i in range(5)
    ]
    selected = mmr_rerank(candidates, lambda_mult=0.7, top_k=3)
    assert len(selected) == 3
