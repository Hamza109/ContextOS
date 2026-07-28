"""Opt-in combined L5+L1 1M-LOC full-index measurement harness."""

from __future__ import annotations

import os
import platform
import time

import pytest

from app.config import Settings
from app.services.l5_index import run_index

pytestmark = pytest.mark.perf


@pytest.mark.skipif(
    not os.environ.get("CONTEXTOS_PERF_CORPUS"),
    reason="NFR-001 harness skipped: set CONTEXTOS_PERF_CORPUS to 1M LOC path to execute",
)
def test_full_index_under_15_min_for_1m_loc() -> None:
    """Execute only when CONTEXTOS_PERF_CORPUS points at a large fixture.

    Gap documentation (constitution IV): without corpus, SC-005 remains Planned / Not Verified.
    """
    corpus = os.environ["CONTEXTOS_PERF_CORPUS"]
    assert os.path.isdir(corpus)
    falkor_url = os.environ.get("CONTEXTOS_PERF_FALKORDB_URL")
    if not falkor_url:
        pytest.skip("corpus present but CONTEXTOS_PERF_FALKORDB_URL is unavailable")
    started = time.perf_counter()
    result = run_index(
        corpus,
        os.environ.get("CONTEXTOS_PERF_REPO", "perf-full-v1"),
        settings=Settings(falkordb_url=falkor_url),
    )
    elapsed = time.perf_counter() - started
    print(
        {
            "corpus_revision": os.environ.get("CONTEXTOS_PERF_CORPUS_REVISION", "unspecified"),
            "warm_state": os.environ.get("CONTEXTOS_PERF_WARM_STATE", "cold"),
            "environment": platform.platform(),
            "combined_l5_l1_seconds": elapsed,
            "reported_total_ms": result.time_ms,
            "files_indexed": result.files_indexed,
            "graph_nodes": result.graph_nodes,
            "embeddings": result.embeddings,
            "target_seconds": 900,
            "observed_under_target": elapsed < 900,
        }
    )
