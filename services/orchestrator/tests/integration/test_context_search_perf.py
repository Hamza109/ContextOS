"""Performance harness for semantic search p95 @ 500k LOC (T029 / T060).

BLOCKED/SKIPPED: 500k LOC fixture unavailable (T020 discovery).
Do NOT invent Pass/Fail execution results.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.perf


def test_context_search_p95_500k_blocked() -> None:
    pytest.skip(
        "SC-002 / NFR-001 blocked: 500k LOC indexed fixture unavailable in workspace "
        "(OQ / T020). No invented p95 Pass."
    )
