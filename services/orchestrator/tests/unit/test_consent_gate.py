"""Consent gate unit tests (T070)."""

from __future__ import annotations

import pytest

from app.security.consent_gate import (
    ConsentContext,
    ConsentDecision,
    assert_external_llm_allowed,
    evaluate_query_time_llm,
    index_path_may_call_external_llm,
)


def test_deny_when_consent_absent() -> None:
    ctx = ConsentContext(external_llm_consent=False, local_inference_configured=False)
    assert evaluate_query_time_llm(ctx) == ConsentDecision.DENY_EXTERNAL
    with pytest.raises(PermissionError):
        assert_external_llm_allowed(ctx)


def test_allow_when_consent_present() -> None:
    ctx = ConsentContext(external_llm_consent=True)
    assert evaluate_query_time_llm(ctx) == ConsentDecision.ALLOW_EXTERNAL_PACKED_CONTEXT_ONLY
    assert_external_llm_allowed(ctx)  # does not raise


def test_index_path_never_allows_external_llm() -> None:
    assert index_path_may_call_external_llm() is False
