"""Unit: L4 savings math on large verbose fixture (EP-008 T012)."""

from __future__ import annotations

from app.config import Settings
from app.services.l4_compression import CompressionService
from app.services.l5_search import SearchHit


def _verbose_unit(n: int = 400) -> str:
    lines = [
        "class VerboseService:",
        "    def run(self) -> None:",
        "        # TODO: shrink this",
        "        pass",
    ]
    lines.extend([f"        print('noise line {i} with lots of padding text here')" for i in range(n)])
    return "\n".join(lines)


def test_savings_band_60_to_95_on_large_fixture() -> None:
    verbose = _verbose_unit(500)
    # Keep substantial high-relevance bodies (not summarized) so savings stay ≤95%.
    core_body = "\n".join(
        ["def core():", "    return 42"]
        + [f"    # retained high-relevance detail {i}" for i in range(180)]
    )
    files = []
    for i in range(5):
        path = f"noise_{i}.py"
        files.append(
            f'<file path="{path}" score="0.05" phase_role="implementation">'
            f"<![CDATA[{verbose}]]></file>"
        )
    files.append(
        f'<file path="core.py" score="0.95" phase_role="implementation">'
        f"<![CDATA[{core_body}]]></file>"
    )
    files.append(
        f'<file path="core_b.py" score="0.92" phase_role="implementation">'
        f"<![CDATA[{core_body}]]></file>"
    )
    ctx = "<?xml version='1.0'?><context_pack>\n" + "\n".join(files) + "\n</context_pack>"
    hits = (
        [SearchHit(f"noise_{i}.py", 0.05, verbose) for i in range(5)]
        + [
            SearchHit("core.py", 0.95, core_body),
            SearchHit("core_b.py", 0.92, core_body),
        ]
    )

    settings = Settings(l4_enabled=True, l4_relevance_summarize_threshold=0.5)
    result = CompressionService(settings).compress(
        final_context=ctx,
        hits=hits,
        phase="Dev",
    )
    assert 60.0 <= result.saving_percent <= 95.0, result.saving_percent
    assert "TODO" in result.final_context or "def run" in result.final_context
    assert "def core" in result.final_context
