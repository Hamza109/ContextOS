"""FR-019 allowed packed/compressed context path hook (T071) — no POST /context delivery."""

from __future__ import annotations

from app.security.consent_gate import ConsentContext, allowed_transmission_for_external


def test_consented_path_restricted_to_packed_compressed_only() -> None:
    denied = allowed_transmission_for_external(ConsentContext(external_llm_consent=False))
    assert denied.may_send_external is False
    assert denied.content_kind == "none"

    allowed = allowed_transmission_for_external(ConsentContext(external_llm_consent=True))
    assert allowed.may_send_external is True
    assert allowed.content_kind == "packed_or_compressed_context_only"
