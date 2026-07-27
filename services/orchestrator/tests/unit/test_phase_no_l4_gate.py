"""Assert no L4 / Headroom gate required for packing success (T043)."""

from __future__ import annotations

from app.services.l5_phase_pack import pack_for_phase
from app.services.l5_search import SearchHit


def test_phase_pack_succeeds_without_l4_gate() -> None:
    hits = [SearchHit(path="a.py", score=0.8, content="print(1)\n", start_line=1)]
    packed = pack_for_phase(hits, query="x", repo="r", phase="Dev", include_citations=False)
    assert packed.final_context
    # No Headroom budget exception path — success without L4
    assert "context_pack" in packed.final_context
