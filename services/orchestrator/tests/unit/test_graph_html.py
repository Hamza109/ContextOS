"""Unit tests for graph.html builder (T022)."""

from __future__ import annotations

from app.api.graph import _select_seed_id, render_graph_html


def test_graph_html_confirmed_visual_defaults_and_depth_clamp() -> None:
    html = render_graph_html(
        repo="demo",
        revision="rev-1",
        depth=9,  # clamp to 5
        nodes=[{"id": "1", "path": "a.py"}, {"id": "2", "path": "b.py"}],
        edges=[
            {
                "from": "2",
                "to": "1",
                "from_path": "b.py",
                "to_path": "a.py",
                "kind": "IMPORTS",
            }
        ],
        seed_id="2",
        mode="files",
    )
    assert "vis-network" in html
    assert "enabled: false" in html  # Confirmed end-state: physics off after stabilize
    assert "forceAtlas2Based" in html
    assert "shape: 'dot'" in html
    assert 'id="sidebar"' in html
    assert 'id="search"' in html
    assert 'id="info-panel"' in html
    assert 'id="legend"' in html
    assert "legend-cb" in html
    assert "hiddenCommunities" in html
    assert "#4E79A7" in html  # Graphify / Tableau community palette
    assert "#F28E2B" in html
    assert "#0f172a" in html
    assert 'max="5"' in html
    assert 'min="1"' in html
    assert 'data-index-revision="rev-1"' in html
    assert 'data-mode="files"' in html
    assert "mode-btn" in html
    assert '"content"' not in html
    assert "SECRET" not in html
    assert "seed_id" in html
    assert "stats.textContent" in html
    assert "allEdges.length" in html
    assert "payload.seed_id" in html
    # Basename labels (not full path pills) — Graphify-style
    assert '"label":"a.py"' in html or '"label": "a.py"' in html
    assert '"community"' in html or '"community":' in html


def test_graph_html_symbols_mode_uses_kind_legend() -> None:
    html = render_graph_html(
        repo="demo",
        revision="rev-1",
        depth=2,
        nodes=[
            {"id": "f", "path": "a.py", "kind": "File", "qname": "a.py"},
            {"id": "c", "path": "a.py", "kind": "Class", "qname": "a.Auth"},
            {"id": "m", "path": "a.py", "kind": "Method", "qname": "a.Auth.validate"},
        ],
        edges=[
            {
                "from": "f",
                "to": "c",
                "from_path": "a.py",
                "to_path": "a.py",
                "kind": "CONTAINS",
            },
            {
                "from": "c",
                "to": "m",
                "from_path": "a.py",
                "to_path": "a.py",
                "kind": "DECLARES",
            },
        ],
        seed_id="f",
        mode="symbols",
    )
    assert 'data-mode="symbols"' in html
    assert "Kinds" in html
    assert '"_kind":"Class"' in html or '"_kind": "Class"' in html
    assert "Auth" in html
    assert "switchMode('symbols')" in html or "mode', 'symbols'" in html


def test_community_key_groups_by_path_prefix() -> None:
    from app.api.graph import _community_key

    assert _community_key("apps/api/src/app.module.ts") == "apps/api"
    assert _community_key("README.md") == "README.md"


def test_graph_html_depth_one_still_valid() -> None:
    html = render_graph_html(
        repo="demo",
        revision="r",
        depth=0,
        nodes=[{"id": "1", "path": "a.py"}],
        edges=[],
    )
    assert 'value="1"' in html
    assert "No File→File IMPORTS" in html


def test_select_seed_prefers_file_kind_when_path_shared() -> None:
    nodes = [
        {"id": "file", "path": "a.py", "kind": "File"},
        {"id": "cls", "path": "a.py", "kind": "Class"},
        {"id": "b", "path": "b.py", "kind": "File"},
    ]
    edges = [{"from": "file", "to": "cls", "kind": "CONTAINS"}]
    assert _select_seed_id(nodes, edges, "a.py") == "file"


def test_select_seed_prefers_file_query_then_highest_degree() -> None:
    nodes = [
        {"id": "a", "path": "apps/api/jest.config.js"},
        {"id": "b", "path": "apps/api/src/app.module.ts"},
        {"id": "c", "path": "apps/api/src/modules/auth/auth.module.ts"},
    ]
    edges = [
        {"from": "b", "to": "c", "kind": "IMPORTS"},
        {"from": "c", "to": "b", "kind": "IMPORTS"},
    ]
    assert _select_seed_id(nodes, edges, "apps/api/src/app.module.ts") == "b"
    assert _select_seed_id(nodes, edges, None) in {"b", "c"}
    assert _select_seed_id(nodes, [], None) == "a"
