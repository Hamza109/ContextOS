"""Unit: summarizer preserves symbols/types/TODOs (EP-008 T009)."""

from __future__ import annotations

from app.adapters.headroom_summarizer import summarize_local


def test_summarizer_preserves_def_class_todo() -> None:
    src = "\n".join(
        [
            "import os",
            "class Foo:",
            "    def bar(self) -> int:",
            "        # TODO: wire budget",
            "        x = 1",
            "        y = 2",
            "        z = 3",
            "        return x + y + z",
            "type Alias = dict[str, int]",
        ]
        + [f"    filler_line_{i} = {i}" for i in range(80)]
    )
    summary, preserved, dropped = summarize_local(src, aggressive=True)
    assert "class Foo" in summary
    assert "def bar" in summary
    assert "TODO" in summary
    assert "type Alias" in summary or "import os" in summary
    assert preserved >= 3
    assert dropped > 0
    assert len(summary) < len(src)
