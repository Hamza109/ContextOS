"""MVP metrics keys present — packing counts only (T044 / OQ-MVP-metrics)."""

from __future__ import annotations

from app.api.schemas_context import ContextMetrics
from app.services.l5_phase_pack import pack_for_phase
from app.services.l5_search import SearchHit


def test_metrics_confirmed_keys_from_phase_pack() -> None:
    hits = [SearchHit(path="a.py", score=0.5, content="hello world\n" * 20, start_line=1)]
    packed = pack_for_phase(hits, query="hello", repo="r", phase="Dev")
    metrics = ContextMetrics(
        tokens_before=packed.tokens_before,
        tokens_after=packed.tokens_after,
        saving_percent=packed.saving_percent,
        trace="mvp_packing_counts",
    )
    data = metrics.model_dump()
    for key in ("tokens_before", "tokens_after", "saving_percent", "trace"):
        assert key in data
    # No invent pass thresholds — just numeric presence
    assert isinstance(metrics.tokens_before, int)
    assert isinstance(metrics.tokens_after, int)
    assert isinstance(metrics.saving_percent, float)
