"""Unit: no external LLM summarize without consent (EP-008 T010)."""

from __future__ import annotations

from app.adapters.headroom_summarizer import may_call_external_summarizer, summarize_unit
from app.security.consent_gate import ConsentContext


def test_local_path_allowed_without_consent() -> None:
    result = summarize_unit(
        "a.py",
        "def f():\n    return 1\n" + ("noise\n" * 40),
        aggressive=True,
        prefer_external=False,
    )
    assert result.mode == "local_heuristic"
    assert "def f" in result.content


def test_external_skipped_without_consent() -> None:
    called = {"n": 0}

    def fake_external(path: str, content: str) -> str:
        called["n"] += 1
        return "EXTERNAL"

    result = summarize_unit(
        "a.py",
        "def f():\n    return 1\n",
        prefer_external=True,
        consent=ConsentContext(external_llm_consent=False),
        external_summarizer=fake_external,
    )
    assert called["n"] == 0
    assert result.mode == "external_skipped"
    assert "EXTERNAL" not in result.content


def test_external_allowed_with_consent() -> None:
    def fake_external(path: str, content: str) -> str:
        return "EXTERNAL_OK"

    result = summarize_unit(
        "a.py",
        "def f():\n    return 1\n",
        prefer_external=True,
        consent=ConsentContext(external_llm_consent=True),
        external_summarizer=fake_external,
    )
    assert result.mode == "external"
    assert result.content == "EXTERNAL_OK"
    assert may_call_external_summarizer(ConsentContext(external_llm_consent=True)) is True
    assert may_call_external_summarizer(ConsentContext(external_llm_consent=False)) is False
