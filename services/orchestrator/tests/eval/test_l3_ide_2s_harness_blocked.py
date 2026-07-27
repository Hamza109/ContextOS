"""OQ-IDE-2s-Harness blocked placeholder (T020/T079).

Composed <2s symbol-accurate IDE context SLA Pass is blocked until harness agreed
with EP-004 US-008. EP-003 contributes L3 precision only — do not invent Pass.
"""

from __future__ import annotations

import pytest

SKIP_REASON = (
    "BLOCKED (OQ-IDE-2s-Harness): composed <2s Pass requires shared harness with EP-004 — "
    "no invented EP-003-only SLA Pass"
)


@pytest.mark.skip(reason=SKIP_REASON)
def test_composed_ide_context_under_2s_blocked() -> None:
    raise AssertionError("OQ-IDE-2s harness must remain skipped")
