"""Full-index performance harness skeleton (T047 / NFR-001 / SC-005).

Planned until a 1M LOC corpus is available. Does not invent search metrics.
"""

from __future__ import annotations

import os

import pytest

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
    # Skeleton: real timing assertion deferred to when corpus + Qdrant + model available.
    assert os.path.isdir(corpus)
    # Placeholder — implement timed run_index when corpus exists.
    pytest.skip("Harness skeleton only — wire timed run_index when corpus ready")
