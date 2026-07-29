"""Unit: IgnorePolicy-excluded paths never enter summarize input (EP-008 T011)."""

from __future__ import annotations

from app.adapters.headroom_summarizer import filter_summarize_inputs, summarize_unit
from app.services.l4_compression import CompressionService
from app.services.l5_search import SearchHit


def test_filter_drops_env_and_venv_paths() -> None:
    kept, excluded = filter_summarize_inputs(
        [
            ("src/ok.py", "def ok(): pass"),
            (".env", "SECRET=1"),
            ("venv/lib/x.py", "x=1"),
            ("credentials.json", "{}"),
        ]
    )
    assert [p for p, _ in kept] == ["src/ok.py"]
    assert ".env" in excluded
    assert any("venv" in p for p in excluded)
    assert "credentials.json" in excluded


def test_summarize_unit_excluded_returns_empty() -> None:
    result = summarize_unit(".env", "SECRET=1", aggressive=True)
    assert result.mode == "excluded"
    assert result.content == ""


def test_compression_skips_excluded_paths() -> None:
    ctx = """<?xml version="1.0"?>
<context_pack>
  <file path="src/ok.py" score="0.9"><![CDATA[def ok():\n    return 1]]></file>
  <file path=".env" score="0.1"><![CDATA[SECRET=supersecret]]></file>
</context_pack>
"""
    result = CompressionService().compress(
        final_context=ctx,
        hits=[
            SearchHit("src/ok.py", 0.9, "def ok():\n    return 1"),
            SearchHit(".env", 0.1, "SECRET=supersecret"),
        ],
        phase="Dev",
    )
    assert "SECRET=supersecret" not in result.final_context
    assert ".env" in result.provenance.get("excluded_paths", [])
