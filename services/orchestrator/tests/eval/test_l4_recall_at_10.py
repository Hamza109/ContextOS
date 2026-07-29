"""Opt-in eval scaffold: L4 recall@10 vs >0.92 (EP-008 T013).

Record/opt-in only — no pass claim without executed run (Constitution IV).
Set CONTEXTOS_L4_RECALL_EVAL=1 to run the measurement.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from app.adapters.headroom_summarizer import summarize_local
from app.services.l4_relevance import RelevanceUnit, score_units

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "l4_naive_pack"
GOLDEN = FIXTURE_DIR / "golden_relevant.json"
PACK = FIXTURE_DIR / "naive_pack.json"


def _recall_at_k(ranked_paths: list[str], relevant: set[str], k: int = 10) -> float:
    if not relevant:
        return 0.0
    top = set(ranked_paths[:k])
    return len(top & relevant) / len(relevant)


@pytest.mark.skipif(
    os.environ.get("CONTEXTOS_L4_RECALL_EVAL", "").lower() not in {"1", "true", "yes"},
    reason="Opt-in recall@10 eval — set CONTEXTOS_L4_RECALL_EVAL=1 (no pass claim by default)",
)
def test_l4_recall_at_10_scaffold() -> None:
    assert PACK.is_file() and GOLDEN.is_file()
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    golden = set(json.loads(GOLDEN.read_text(encoding="utf-8"))["relevant_paths"])

    units = [
        RelevanceUnit(
            path=u["path"],
            content=u["content"],
            hit_score=float(u.get("score", 0.0)),
            phase_role=u.get("phase_role", "implementation"),
        )
        for u in pack["units"]
    ]
    # Simulate L4: summarize low-score units then re-rank by score (relevance preserved).
    scored = score_units(units)
    ranked = [s.path for s in scored]
    recall = _recall_at_k(ranked, golden, k=10)
    # Record measurement — assert only when opt-in run is intentional.
    # Target: >0.92 (BRD §10). Do not claim pass in CI without this env.
    assert recall > 0.92, f"recall@10={recall:.4f} (recorded)"


def test_fixture_present_for_scaffold() -> None:
    """Always-on sanity: fixture exists so harness is runnable."""
    assert FIXTURE_DIR.is_dir()
    assert PACK.is_file()
    assert GOLDEN.is_file()
    # Smoke: summarizer does not drop golden symbol lines from a sample unit
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    sample = next(u for u in pack["units"] if "def relevant_api" in u["content"])
    summary, _, _ = summarize_local(sample["content"], aggressive=True)
    assert "def relevant_api" in summary
