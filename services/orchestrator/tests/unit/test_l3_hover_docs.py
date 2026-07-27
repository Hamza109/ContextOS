"""Unit: hover/doc presentation mapping (T026) — no invented undocumented fields."""

from __future__ import annotations

from app.adapters.serena_mcp import SerenaHoverPayload
from app.services.l3_symbol import HoverDocs, map_hover


def test_map_hover_passthrough_contents() -> None:
    payload = SerenaHoverPayload(
        contents="```python\ndef foo(): ...\n```\nDoc for foo.",
        path="m.py",
        line=10,
    )
    docs = map_hover(payload)
    assert isinstance(docs, HoverDocs)
    assert docs.contents == payload.contents
    assert docs.path == "m.py"
    assert docs.line == 10


def test_map_hover_empty_contents_ok() -> None:
    docs = map_hover(SerenaHoverPayload(contents=""))
    assert docs.contents == ""
    assert docs.path is None
