"""OQ-12 / SC-002 accuracy evaluation harness — **BLOCKED** placeholder (T029, T078).

Missing Evidence: measurement method for FR-04 99% accuracy is not agreed (OQ-12).
This module MUST NOT invent Pass/Fail results or claim SC-002 Pass.

Proposed verification design candidates (non-normative — T019):
1. Golden fixture set of (language, symbol, expected file:line) scored as exact match rate.
2. Dual-judge: Serena result vs independently curated LSP oracle on fixture repos.
3. Stratified sample across Proposed language subset until OQ-Lang-Set Confirmed.

None of the above are Confirmed. Skip until product/research freezes the method.
"""

from __future__ import annotations

import pytest

# Explicit skip reason for validation-report / CI honesty.
OQ12_SKIP_REASON = (
    "BLOCKED (OQ-12): FR-04/SC-002 99% accuracy measurement method Missing Evidence — "
    "Proposed verification design only; do not invent Pass/Fail"
)


@pytest.mark.skip(reason=OQ12_SKIP_REASON)
def test_l3_definition_accuracy_oq12_blocked() -> None:
    """Placeholder — never execute a fake accuracy Pass."""
    raise AssertionError("OQ-12 harness must remain skipped until measure method Confirmed")
