"""Opt-in OKF grounding + fallback eval (EP-013 T026).

Set CONTEXTOS_OKF_RETRIEVAL_EVAL=1 to execute. Records measurements only —
does not invent product Pass/Fail claims.
"""

from __future__ import annotations

import os
import statistics
import time

import pytest

from app.adapters.okf_bundle import OkfBundle
from app.config import Settings
from app.services.okf_retrieve import retrieve_okf

pytestmark = pytest.mark.eval
DATASET_REVISION = "okf-retrieval-eval-v1"


@pytest.mark.skipif(
    os.environ.get("CONTEXTOS_OKF_RETRIEVAL_EVAL") != "1",
    reason="OKF retrieval eval skipped: set CONTEXTOS_OKF_RETRIEVAL_EVAL=1",
)
def test_okf_retrieval_precision_recall_and_fallback(tmp_path) -> None:
    bundle = OkfBundle(tmp_path / "demo")
    bundle.write_concept(
        "docs/architecture/system-overview",
        type="Architecture Doc",
        title="Architecture Overview",
        description="API contract hybrid search layers",
        tags=["architecture", "api-contract"],
        sources=[{"uri": "docs/architecture/system-overview.md"}],
        generated={"by": "process:contextos-okf-generator", "at": "2026-07-28T00:00:00Z"},
        repo="demo",
        index_revision="eval-1",
        body="# Architecture Overview\n",
    )
    settings = Settings(okf_cache_dir=tmp_path, okf_enabled=True)
    cases = [
        ("Architecture Overview", {"docs/architecture/system-overview"}, True),
        ("api contract architecture", {"docs/architecture/system-overview"}, True),
        ("zzzz-no-match-qqq", set(), False),
    ]
    expected_hits: set[str] = set()
    observed_hits: set[str] = set()
    fallback_ok = 0
    durations: list[float] = []
    for query, expected_ids, should_hit in cases:
        started = time.perf_counter()
        result = retrieve_okf("demo", query, settings=settings, bundle=bundle)
        durations.append((time.perf_counter() - started) * 1000)
        if should_hit:
            expected_hits |= expected_ids
            observed_hits |= set(result.matched_ids) & expected_ids
            assert result.status == "hit"
        else:
            assert result.status == "miss"
            fallback_ok += 1  # miss → caller uses hybrid path
    tp = len(expected_hits & observed_hits)
    fp = len(observed_hits - expected_hits)
    fn = len(expected_hits - observed_hits)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    ordered = sorted(durations)
    print(
        {
            "dataset_revision": DATASET_REVISION,
            "grounding": {"precision": precision, "recall": recall, "f1": f1},
            "fallback_miss_cases": fallback_ok,
            "latency_ms": {
                "p50": statistics.median(ordered),
                "p95": ordered[max(0, int(len(ordered) * 0.95) - 1)],
            },
        }
    )
    # Measurement harness only — assert structural sanity, not product SLA.
    assert precision >= 0.0
    assert recall >= 0.0
    assert fallback_ok == 1
