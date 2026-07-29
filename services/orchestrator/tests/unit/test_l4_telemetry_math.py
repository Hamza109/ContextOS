"""Unit: compression telemetry math (EP-008 T025)."""

from __future__ import annotations

from app.services.l4_compression import compression_ratio, saving_percent
from app.telemetry.compression import compute_cost_saved


def test_saving_and_ratio_math() -> None:
    assert saving_percent(1000, 200) == 80.0
    assert compression_ratio(1000, 200) == 0.2
    assert saving_percent(0, 0) == 0.0


def test_cost_saved_token_delta_primary() -> None:
    assert compute_cost_saved(1000, 200) == 800.0


def test_cost_saved_optional_rate() -> None:
    # 800 tokens saved / 1000 * 0.5 = 0.4
    assert compute_cost_saved(1000, 200, rate_per_1k_tokens=0.5) == 0.4
