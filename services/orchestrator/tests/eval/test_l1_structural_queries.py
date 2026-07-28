from __future__ import annotations

import os
import statistics
import time

import pytest

from app.adapters.l1_parser import StructuralNode
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_structural_query import StructuralQueryService

pytestmark = pytest.mark.eval
DATASET_REVISION = "l1-structural-queries-v1"


@pytest.mark.skipif(
    os.environ.get("CONTEXTOS_L1_QUERY_EVAL") != "1",
    reason="query grounding/cache/latency eval skipped: set CONTEXTOS_L1_QUERY_EVAL=1",
)
def test_structural_query_grounding_cache_and_latency() -> None:
    cache = L1EntityCache()
    entity = StructuralNode(
        "auth-validate",
        "repo",
        "src/auth.py",
        "Method",
        "auth.Auth.validate",
        12,
        14,
        "revision-1",
    )
    cache.refresh("repo", "revision-1", [entity])
    service = StructuralQueryService(
        Settings(falkordb_url="memory://eval"),
        cache=cache,
    )
    expected = {"src/auth.py:12"}
    observed: set[str] = set()
    durations: list[float] = []
    hits = 0
    for _ in range(20):
        started = time.perf_counter()
        result = service.enrich("<base/>", repo="repo", query="where is auth validated?")
        durations.append((time.perf_counter() - started) * 1000)
        hits += int(result.cache_hit)
        if 'citation="src/auth.py:12"' in result.final_context:
            observed.add("src/auth.py:12")
    tp = len(expected & observed)
    fp = len(observed - expected)
    fn = len(expected - observed)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    ordered = sorted(durations)
    print(
        {
            "dataset_revision": DATASET_REVISION,
            "grounding": {"precision": precision, "recall": recall, "f1": f1},
            "post_warm_cache_hit_rate": hits / len(durations),
            "latency_ms": {
                "p50": statistics.median(ordered),
                "p95": ordered[max(0, int(len(ordered) * 0.95) - 1)],
            },
        }
    )
    assert observed == expected
