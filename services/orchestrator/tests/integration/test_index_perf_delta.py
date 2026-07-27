"""Delta performance harness skeleton (T061 / NFR-002 / SC-006).

Planned until a 100-file delta fixture is executed with evidence.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.perf


@pytest.mark.skipif(
    not os.environ.get("CONTEXTOS_PERF_DELTA"),
    reason="NFR-002 harness skipped: set CONTEXTOS_PERF_DELTA=1 to execute 100-file delta timing",
)
def test_delta_100_files_under_60s() -> None:
    """Gap (constitution IV): SC-006 remains Planned / Not Verified without harness execution."""
    assert os.environ.get("CONTEXTOS_PERF_DELTA")
    pytest.skip("Harness skeleton only — wire timed incremental run_index for 100-file delta")
