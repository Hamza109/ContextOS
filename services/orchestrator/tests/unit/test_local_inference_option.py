"""Local Ollama/config path without external exfil (T072 / FR-020)."""

from __future__ import annotations

from app.config import Settings
from app.security.consent_gate import ConsentContext, ConsentDecision, evaluate_query_time_llm


def test_local_inference_option_avoids_external() -> None:
    ctx = ConsentContext(external_llm_consent=False, local_inference_configured=True)
    assert evaluate_query_time_llm(ctx) == ConsentDecision.USE_LOCAL_INFERENCE

    # Config hook exists (Proposed)
    settings = Settings(local_inference_enabled=True, local_inference_url="http://127.0.0.1:11434")
    assert settings.local_inference_enabled is True
    assert settings.local_inference_url is not None
