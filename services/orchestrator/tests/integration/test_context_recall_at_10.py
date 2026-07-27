"""Recall@10 >0.92 harness placeholder (T030 / T061).

BLOCKED until OQ-recall-harness resolves (evaluation dataset Missing Evidence).
MUST NOT claim Pass.
"""

from __future__ import annotations

import pytest


def test_context_recall_at_10_blocked() -> None:
    pytest.skip(
        "SC-003 / FR-008 blocked: OQ-recall-harness — evaluation harness/dataset "
        "Missing Evidence. No invented recall Pass."
    )
