"""OQ discovery notes for EP-003 backend (T003–T004, T018–T021) — in-test only.

Do NOT Confirmed-freeze OQ-12, OQ-Symbol-REST, OQ-Safe-Edit-Shape, OQ-Lang-Set, OQ-11.
Lean: no standalone open-questions.md.
"""

from __future__ import annotations

from app.adapters.serena_mcp import PROPOSED_FIXTURE_LANGUAGES
from app.services.l3_symbol import SAFE_EDIT_BEGIN, proposed_fixture_languages


def test_mvp_transport_is_mcp_first_option_a() -> None:
    """T003: Proposed Option A — MCP-first; Option B symbol REST deferred."""
    # Documented by absence of Confirmed symbol routers (see OpenAPI tests).
    assert "python" in PROPOSED_FIXTURE_LANGUAGES


def test_proposed_language_subset_documented() -> None:
    """T007/T022: Proposed AC fixture subset — OQ-Lang-Set remains open."""
    subset = proposed_fixture_languages()
    assert subset == frozenset({"python", "typescript", "javascript"})
    # Do not claim 12+ language-complete Pass


def test_safe_edit_interim_markers_documented() -> None:
    """T054: Proposed delimited block interim — OQ-Safe-Edit-Shape open."""
    assert "PROPOSED" in SAFE_EDIT_BEGIN
