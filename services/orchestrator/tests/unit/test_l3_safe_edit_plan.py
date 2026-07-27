"""Unit: safe-edit-plan behavioral discriminator (T057; FR-008; SC-006).

Proposed interim markers only — no invented Confirmed schema keys (OQ-Safe-Edit-Shape).
"""

from __future__ import annotations

from app.services.l3_symbol import (
    SAFE_EDIT_BEGIN,
    SAFE_EDIT_END,
    SafeEditPlan,
    attach_safe_edit_plan,
    format_safe_edit_plan_block,
    is_symbol_scoped_plan,
)


def test_safe_edit_plan_is_symbol_scoped_not_rewrite_entire_file() -> None:
    plan = SafeEditPlan(
        symbol_name="login",
        guidance_text=(
            "Prefer symbol-scoped edits.\n"
            "Do not rewrite entire files; change only call sites."
        ),
        definition_file_line="auth.py:10",
        reference_count=2,
        breaking_change_count=0,
    )
    block = format_safe_edit_plan_block(plan)
    assert SAFE_EDIT_BEGIN in block and SAFE_EDIT_END in block
    assert is_symbol_scoped_plan(block)
    assert "safe_edit_plan_json" not in block  # no invented Confirmed key


def test_affirmative_rewrite_entire_file_fails_discriminator() -> None:
    bad = (
        f"{SAFE_EDIT_BEGIN}\n"
        "symbol: x\n"
        "rewrite entire file\n"
        f"{SAFE_EDIT_END}"
    )
    assert is_symbol_scoped_plan(bad) is False


def test_attach_safe_edit_preserves_host_context() -> None:
    host = "<context_pack>hello</context_pack>"
    plan = SafeEditPlan(symbol_name="x", guidance_text="symbol-scoped tweak")
    out = attach_safe_edit_plan(host, plan)
    assert host in out
    assert is_symbol_scoped_plan(out)
