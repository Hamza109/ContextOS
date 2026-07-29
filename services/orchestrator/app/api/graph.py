"""GET /graph.html — Confirmed vis-network dependency graph (EP-007 / US-019).

T003 contract sketch vs api-contract §2.5 / ADR-010:
- HTML + vis-network (CDN ok for local trusted draft)
- Default mode=files: File nodes; IMPORTS edges; depth 1–5 (Confirmed)
- Proposed mode=symbols: File/Module/Class/Method/Call + L1 edges
- Physics: ForceAtlas2 stabilize then disabled (Confirmed end-state: physics off)
- Graphify-inspired UX: Tableau colors, legend checkboxes, sidebar search/info
- Auth NEEDS CLARIFICATION — local trusted-client draft only (no Confirmed auth)
- Proposed 404 unknown repo; payload metadata/paths only (no source bodies)
"""

from __future__ import annotations

import json
import time
from html import escape

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.adapters.falkordb_store import EDGE_TYPES, get_graph_store
from app.config import get_settings
from app.security.ignore_policy import path_is_hard_excluded
from app.telemetry.blast import graph_span, record_graph_attributes

router = APIRouter(tags=["graph"])

_BG_COLOR = "#0f172a"
_PAYLOAD_CAP = 2000
_MODE_FILES = "files"
_MODE_SYMBOLS = "symbols"
_ALLOWED_MODES = {_MODE_FILES, _MODE_SYMBOLS}
_FILE_EDGE_KINDS = {"IMPORTS"}
_SYMBOL_EDGE_KINDS = set(EDGE_TYPES)

# Graphify / Tableau 10 palette (Proposed multi-color UX).
_COMMUNITY_PALETTE = (
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
    "#9C755F",
    "#BAB0AC",
)

# Fixed kind colors for symbols mode (Graphify-like type discrimination).
_KIND_COLORS = {
    "File": "#4E79A7",
    "Module": "#76B7B2",
    "Class": "#F28E2B",
    "Method": "#59A14F",
    "Call": "#E15759",
}
_KIND_ORDER = ("File", "Module", "Class", "Method", "Call")

_EDGE_COLORS = {
    "IMPORTS": "#475569",
    "CONTAINS": "#64748b",
    "DECLARES": "#94a3b8",
    "MAKES_CALL": "#F28E2B",
}


@router.get(
    "/graph.html",
    response_class=HTMLResponse,
    summary="Interactive L1 dependency / structural graph",
    description=(
        "Confirmed default: mode=files, File nodes, IMPORTS edges, depth 1–5, "
        "background #0f172a. Proposed: mode=symbols expands L1 Class/Method/Call. "
        "Auth NEEDS CLARIFICATION — local trusted draft only. No source bodies."
    ),
    responses={
        200: {"description": "Proposed: text/html success"},
        404: {"description": "Proposed: unknown/unindexed repo"},
        503: {"description": "Proposed: graph store unavailable"},
    },
)
def get_graph_html(
    repo: str = Query(..., min_length=1, description="Confirmed query param"),
    depth: int = Query(
        3,
        ge=1,
        le=5,
        description="Confirmed interactive depth 1–5 (clamped)",
    ),
    file: str | None = Query(
        None,
        description="Proposed seed file path; default prefers a connected node",
    ),
    mode: str = Query(
        _MODE_FILES,
        description="Confirmed files (IMPORTS) or Proposed symbols (L1 entities)",
    ),
) -> HTMLResponse:
    settings = get_settings()
    depth = max(1, min(int(depth), 5))
    mode_norm = (mode or _MODE_FILES).strip().lower()
    if mode_norm not in _ALLOWED_MODES:
        mode_norm = _MODE_FILES
    with graph_span(
        "graph.html",
        repo=repo,
        attributes={"graph.depth": depth, "graph.mode": mode_norm},
    ) as span:
        started = time.perf_counter()
        store = get_graph_store(settings)
        try:
            revision = store.latest_revision(repo)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=503, detail="graph store unavailable"
            ) from exc
        if not revision:
            raise HTTPException(
                status_code=404,
                detail=f"unknown or unindexed repo: {repo}",
            )
        try:
            if mode_norm == _MODE_SYMBOLS:
                raw_nodes, raw_edges = store.list_structural_subgraph(
                    repo, revision, depth=depth, limit=_PAYLOAD_CAP
                )
            else:
                raw_nodes, raw_edges = store.list_file_imports_subgraph(
                    repo, revision, depth=depth, limit=_PAYLOAD_CAP
                )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=503, detail="graph store unavailable"
            ) from exc

        nodes, edges = _filter_graph_payload(raw_nodes, raw_edges, mode=mode_norm)
        seed_id = _select_seed_id(nodes, edges, file)
        html = render_graph_html(
            repo=repo,
            revision=revision,
            depth=depth,
            nodes=nodes,
            edges=edges,
            seed_id=seed_id,
            mode=mode_norm,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        record_graph_attributes(
            span,
            duration_ms=duration_ms,
            node_count=len(nodes),
            edge_count=len(edges),
            depth=depth,
        )
        return HTMLResponse(content=html, status_code=200)


def _filter_graph_payload(
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
    *,
    mode: str = _MODE_FILES,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    allowed_kinds = (
        _SYMBOL_EDGE_KINDS if mode == _MODE_SYMBOLS else _FILE_EDGE_KINDS
    )
    kept_nodes = [
        node for node in nodes if not path_is_hard_excluded(node.get("path", ""))
    ]
    # files mode: ensure kind default
    if mode == _MODE_FILES:
        for node in kept_nodes:
            node.setdefault("kind", "File")
            node.setdefault("qname", node.get("path", ""))
    allowed = {node["id"] for node in kept_nodes}
    kept_edges = [
        edge
        for edge in edges
        if edge.get("kind") in allowed_kinds
        and edge.get("from") in allowed
        and edge.get("to") in allowed
        and not path_is_hard_excluded(edge.get("from_path", ""))
        and not path_is_hard_excluded(edge.get("to_path", ""))
    ]
    return kept_nodes, kept_edges


def _select_seed_id(
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
    file: str | None,
) -> str | None:
    """Prefer File matching ?file=, else highest-degree node, else first."""
    if not nodes:
        return None
    if file:
        wanted = file.strip().replace("\\", "/").lstrip("./")
        path_matches = [
            node
            for node in nodes
            if node.get("path") == wanted
            or node.get("path", "").endswith("/" + wanted)
            or node.get("path", "").endswith(wanted)
        ]
        file_matches = [
            node for node in path_matches if node.get("kind", "File") == "File"
        ]
        if file_matches:
            return file_matches[0]["id"]
        if path_matches:
            return path_matches[0]["id"]
    degree: dict[str, int] = {node["id"]: 0 for node in nodes}
    for edge in edges:
        degree[edge["from"]] = degree.get(edge["from"], 0) + 1
        degree[edge["to"]] = degree.get(edge["to"], 0) + 1
    best = max(
        nodes,
        key=lambda node: (degree.get(node["id"], 0), -len(node.get("path", ""))),
    )
    if degree.get(best["id"], 0) > 0:
        return best["id"]
    return nodes[0]["id"]


def _community_key(path: str) -> str:
    """Group files by top path segments (Graphify-like community buckets)."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    if not parts:
        return "(root)"
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def _display_label(node: dict[str, str], *, mode: str) -> str:
    if mode == _MODE_SYMBOLS:
        kind = node.get("kind", "File")
        qname = node.get("qname") or node.get("path", "")
        if kind == "File":
            return (node.get("path") or qname).rsplit("/", 1)[-1]
        # Prefer short leaf of qualified name
        leaf = qname.rsplit(".", 1)[-1] if qname else kind
        return leaf
    return node.get("path", "").rsplit("/", 1)[-1]


def render_graph_html(
    *,
    repo: str,
    revision: str,
    depth: int,
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
    seed_id: str | None = None,
    mode: str = _MODE_FILES,
) -> str:
    """Build Graphify-inspired vis-network HTML (community/kind colors + filters)."""
    depth = max(1, min(int(depth), 5))
    mode = mode if mode in _ALLOWED_MODES else _MODE_FILES
    if seed_id is None and nodes:
        seed_id = nodes[0]["id"]
    seed_label = next(
        (node.get("path", "") for node in nodes if node["id"] == seed_id),
        "",
    )
    degree: dict[str, int] = {node["id"]: 0 for node in nodes}
    for edge in edges:
        degree[edge["from"]] = degree.get(edge["from"], 0) + 1
        degree[edge["to"]] = degree.get(edge["to"], 0) + 1

    if mode == _MODE_SYMBOLS:
        key_counts: dict[str, int] = {}
        node_keys: dict[str, str] = {}
        for node in nodes:
            key = node.get("kind") or "File"
            node_keys[node["id"]] = key
            key_counts[key] = key_counts.get(key, 0) + 1
        ordered_keys = [k for k in _KIND_ORDER if k in key_counts] + sorted(
            k for k in key_counts if k not in _KIND_ORDER
        )
        key_to_cid = {key: idx for idx, key in enumerate(ordered_keys)}
        legend = [
            {
                "cid": key_to_cid[key],
                "color": _KIND_COLORS.get(
                    key, _COMMUNITY_PALETTE[key_to_cid[key] % len(_COMMUNITY_PALETTE)]
                ),
                "label": key,
                "count": key_counts[key],
            }
            for key in ordered_keys
        ]
        legend_title = "Kinds"
    else:
        key_counts = {}
        node_keys = {}
        for node in nodes:
            key = _community_key(node["path"])
            node_keys[node["id"]] = key
            key_counts[key] = key_counts.get(key, 0) + 1
        ordered_keys = sorted(key_counts.keys(), key=lambda k: (-key_counts[k], k))
        key_to_cid = {key: idx for idx, key in enumerate(ordered_keys)}
        legend = [
            {
                "cid": key_to_cid[key],
                "color": _COMMUNITY_PALETTE[key_to_cid[key] % len(_COMMUNITY_PALETTE)],
                "label": key,
                "count": key_counts[key],
            }
            for key in ordered_keys
        ]
        legend_title = "Communities"

    vis_nodes = []
    for node in nodes:
        path = node["path"]
        kind = node.get("kind") or "File"
        qname = node.get("qname") or path
        label = _display_label(node, mode=mode)
        deg = degree.get(node["id"], 0)
        size = 8 + min(22, deg * 1.5)
        if mode == _MODE_SYMBOLS and kind == "File":
            size = max(size, 14)
        font_size = 12 if node["id"] == seed_id or deg >= 3 else 0
        cid = key_to_cid[node_keys[node["id"]]]
        if mode == _MODE_SYMBOLS:
            color = _KIND_COLORS.get(
                kind, _COMMUNITY_PALETTE[cid % len(_COMMUNITY_PALETTE)]
            )
        else:
            color = _COMMUNITY_PALETTE[cid % len(_COMMUNITY_PALETTE)]
        title = f"{kind}: {qname}" if mode == _MODE_SYMBOLS else path
        vis_nodes.append(
            {
                "id": node["id"],
                "label": label,
                "title": title,
                "size": size,
                "font": {"size": font_size, "color": "#e2e8f0", "face": "ui-sans-serif"},
                "color": {
                    "background": color,
                    "border": color,
                    "highlight": {"background": "#ffffff", "border": color},
                },
                "community": cid,
                "_path": path,
                "_degree": deg,
                "_community_name": node_keys[node["id"]],
                "_kind": kind,
                "_qname": qname,
            }
        )
    vis_edges = [
        {
            "from": edge["from"],
            "to": edge["to"],
            "arrows": "to",
            "label": edge.get("kind", "") if mode == _MODE_SYMBOLS else "",
            "font": {"size": 0 if mode == _MODE_FILES else 8, "color": "#64748b"},
            "color": {
                "color": _EDGE_COLORS.get(edge.get("kind", ""), "#475569"),
                "opacity": 0.55,
            },
            "_kind": edge.get("kind", ""),
        }
        for edge in edges
    ]
    payload = {
        "nodes": vis_nodes,
        "edges": vis_edges,
        "legend": legend,
        "legend_title": legend_title,
        "depth": depth,
        "repo": repo,
        "index_revision": revision,
        "seed_id": seed_id,
        "seed_label": seed_label,
        "mode": mode,
    }
    for item in payload["nodes"]:
        assert "content" not in item and "source" not in item
    for item in payload["edges"]:
        assert "content" not in item and "source" not in item

    data_json = json.dumps(payload, separators=(",", ":"))
    safe_repo = escape(repo, quote=True)
    safe_rev = escape(revision, quote=True)
    safe_mode = escape(mode, quote=True)
    files_active = "active" if mode == _MODE_FILES else ""
    symbols_active = "active" if mode == _MODE_SYMBOLS else ""
    empty_hint = ""
    if not edges:
        if mode == _MODE_SYMBOLS:
            empty_hint = (
                '<div class="banner">No L1 structural edges in this revision. '
                "Re-index the repo to populate Class/Method/Call relationships.</div>"
            )
        else:
            empty_hint = (
                '<div class="banner">No File→File IMPORTS in this revision. '
                "Re-index after relative-import fixes; package imports "
                "(@nestjs/…) stay unresolved by design.</div>"
            )
    search_ph = "Search symbols..." if mode == _MODE_SYMBOLS else "Search files..."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>ContextOS graph — {safe_repo}</title>
  <!-- Proposed freshness: index_revision={safe_rev} stale=false mode={safe_mode} -->
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {_BG_COLOR}; color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      display: flex; height: 100vh; overflow: hidden;
    }}
    #graph {{ flex: 1; position: relative; background: {_BG_COLOR}; }}
    #sidebar {{
      width: 300px; background: #1e293b; border-left: 1px solid #334155;
      display: flex; flex-direction: column; overflow: hidden;
    }}
    #toolbar {{
      padding: 12px; border-bottom: 1px solid #334155; display: flex;
      flex-direction: column; gap: 8px;
    }}
    #toolbar strong {{ font-size: 14px; }}
    .meta {{ font-size: 12px; color: #94a3b8; }}
    label {{ font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 8px; }}
    .mode-toggle {{ display: flex; gap: 6px; }}
    .mode-btn {{
      flex: 1; text-align: center; padding: 6px 8px; border-radius: 6px;
      border: 1px solid #475569; background: {_BG_COLOR}; color: #94a3b8;
      font-size: 12px; cursor: pointer; text-decoration: none;
    }}
    .mode-btn:hover {{ color: #e2e8f0; border-color: #64748b; }}
    .mode-btn.active {{ background: #4E79A7; border-color: #4E79A7; color: #fff; }}
    #search-wrap {{ padding: 12px; border-bottom: 1px solid #334155; }}
    #search {{
      width: 100%; background: {_BG_COLOR}; border: 1px solid #475569; color: #e2e8f0;
      padding: 7px 10px; border-radius: 6px; font-size: 13px; outline: none;
    }}
    #search:focus {{ border-color: #4E79A7; }}
    #search-results {{
      max-height: 120px; overflow-y: auto; margin-top: 6px; display: none;
    }}
    .search-item {{
      padding: 4px 6px; cursor: pointer; border-radius: 4px; font-size: 12px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .search-item:hover {{ background: #334155; }}
    #info-panel {{ padding: 14px; border-bottom: 1px solid #334155; min-height: 140px; }}
    #info-panel h3, #legend-wrap h3 {{
      font-size: 12px; color: #94a3b8; margin-bottom: 8px;
      text-transform: uppercase; letter-spacing: 0.05em;
    }}
    #info-content {{ font-size: 13px; color: #cbd5e1; line-height: 1.55; }}
    #info-content .field {{ margin-bottom: 5px; word-break: break-all; }}
    #info-content .field b {{ color: #f8fafc; }}
    #info-content .empty {{ color: #64748b; font-style: italic; }}
    .neighbor-link {{
      display: block; padding: 2px 6px; margin: 2px 0; border-radius: 3px;
      cursor: pointer; font-size: 12px; white-space: nowrap; overflow: hidden;
      text-overflow: ellipsis; border-left: 3px solid #4E79A7;
    }}
    .neighbor-link:hover {{ background: #334155; }}
    #neighbors-list {{ max-height: 140px; overflow-y: auto; margin-top: 4px; }}
    #legend-wrap {{ flex: 1; overflow-y: auto; padding: 12px; min-height: 0; }}
    #legend-controls {{
      display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 4px 0;
    }}
    #legend-controls label {{
      display: flex; align-items: center; gap: 6px; cursor: pointer;
      font-size: 12px; color: #94a3b8; user-select: none;
    }}
    #legend-controls label:hover {{ color: #e2e8f0; }}
    .legend-item {{
      display: flex; align-items: center; gap: 8px; padding: 4px 0;
      cursor: pointer; border-radius: 4px; font-size: 12px;
    }}
    .legend-item:hover {{ background: #334155; padding-left: 4px; }}
    .legend-item.dimmed {{ opacity: 0.35; }}
    .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
    .legend-label {{ flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .legend-count {{ color: #64748b; font-size: 11px; }}
    .legend-cb, #select-all-cb {{
      appearance: none; -webkit-appearance: none; width: 14px; height: 14px;
      border: 1.5px solid #475569; border-radius: 3px; background: {_BG_COLOR};
      cursor: pointer; position: relative; flex-shrink: 0;
    }}
    .legend-cb:checked, #select-all-cb:checked {{
      background: #4E79A7; border-color: #4E79A7;
    }}
    .legend-cb:checked::after, #select-all-cb:checked::after {{
      content: ''; position: absolute; left: 3.5px; top: 1px; width: 4px; height: 7px;
      border: solid #fff; border-width: 0 2px 2px 0; transform: rotate(45deg);
    }}
    #select-all-cb:indeterminate {{ background: #4E79A7; border-color: #4E79A7; }}
    #select-all-cb:indeterminate::after {{
      content: ''; position: absolute; left: 2px; top: 5px; width: 8px; height: 2px;
      background: #fff; border: none; transform: none;
    }}
    #stats {{
      padding: 10px 14px; border-top: 1px solid #334155;
      font-size: 11px; color: #64748b;
    }}
    .banner {{
      position: absolute; left: 12px; top: 12px; right: 12px; z-index: 2;
      background: #1e293b; border: 1px solid #334155; color: #94a3b8;
      padding: 8px 10px; border-radius: 6px; font-size: 12px;
    }}
  </style>
</head>
<body data-index-revision="{safe_rev}" data-stale="false" data-repo="{safe_repo}" data-mode="{safe_mode}">
  <div id="graph">{empty_hint}</div>
  <aside id="sidebar">
    <div id="toolbar">
      <strong>ContextOS L1 graph</strong>
      <span class="meta">repo={safe_repo}</span>
      <div class="mode-toggle">
        <a class="mode-btn {files_active}" id="mode-files" href="#">Files</a>
        <a class="mode-btn {symbols_active}" id="mode-symbols" href="#">Symbols</a>
      </div>
      <label>Depth
        <input id="depth" type="range" min="1" max="5" value="{depth}" style="flex:1"/>
        <span id="depthVal">{depth}</span>
      </label>
    </div>
    <div id="search-wrap">
      <input id="search" type="text" placeholder="{search_ph}" autocomplete="off"/>
      <div id="search-results"></div>
    </div>
    <div id="info-panel">
      <h3>Node Info</h3>
      <div id="info-content"><span class="empty">Click a node to inspect it</span></div>
    </div>
    <div id="legend-wrap">
      <h3 id="legend-title">{legend_title}</h3>
      <div id="legend-controls">
        <label><input type="checkbox" id="select-all-cb" checked> Select All</label>
      </div>
      <div id="legend"></div>
    </div>
    <div id="stats"></div>
  </aside>
  <script id="graph-data" type="application/json">{data_json}</script>
  <script>
    const payload = JSON.parse(document.getElementById('graph-data').textContent);
    const container = document.getElementById('graph');
    const allNodes = payload.nodes || [];
    const allEdges = payload.edges || [];
    const LEGEND = payload.legend || [];
    const depthInput = document.getElementById('depth');
    const depthVal = document.getElementById('depthVal');
    const stats = document.getElementById('stats');
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');
    const infoContent = document.getElementById('info-content');
    const selectAllCb = document.getElementById('select-all-cb');
    const hiddenCommunities = new Set();

    function esc(s) {{
      return String(s).replace(/[&<>"']/g, c => ({{
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
      }})[c]);
    }}

    function switchMode(nextMode) {{
      const url = new URL(window.location.href);
      url.searchParams.set('mode', nextMode);
      url.searchParams.set('depth', String(depthInput.value));
      window.location.href = url.toString();
    }}
    document.getElementById('mode-files').addEventListener('click', (e) => {{
      e.preventDefault(); switchMode('files');
    }});
    document.getElementById('mode-symbols').addEventListener('click', (e) => {{
      e.preventDefault(); switchMode('symbols');
    }});

    function neighborhood(maxDepth) {{
      if (!allNodes.length) return {{nodes: [], edges: []}};
      const seed = payload.seed_id || allNodes[0].id;
      if (!allEdges.length) {{
        const seedNode = allNodes.find(n => n.id === seed) || allNodes[0];
        return {{nodes: [seedNode], edges: []}};
      }}
      const adj = new Map();
      for (const e of allEdges) {{
        if (!adj.has(e.from)) adj.set(e.from, []);
        if (!adj.has(e.to)) adj.set(e.to, []);
        adj.get(e.from).push(e.to);
        adj.get(e.to).push(e.from);
      }}
      const keep = new Set([seed]);
      let frontier = [seed];
      for (let d = 0; d < maxDepth; d++) {{
        const next = [];
        for (const id of frontier) {{
          for (const n of (adj.get(id) || [])) {{
            if (!keep.has(n)) {{ keep.add(n); next.push(n); }}
          }}
        }}
        frontier = next;
      }}
      return {{
        nodes: allNodes.filter(n => keep.has(n.id)),
        edges: allEdges.filter(e => keep.has(e.from) && keep.has(e.to)),
      }};
    }}

    let network = null;
    let nodesDS = null;
    let edgesDS = null;

    function applyCommunityVisibility() {{
      if (!nodesDS) return;
      const updates = nodesDS.getIds().map(id => {{
        const n = nodesDS.get(id);
        return {{ id, hidden: hiddenCommunities.has(n.community) }};
      }});
      if (updates.length) nodesDS.update(updates);
    }}

    function updateSelectAllState() {{
      const total = LEGEND.length;
      const hidden = hiddenCommunities.size;
      selectAllCb.checked = hidden === 0;
      selectAllCb.indeterminate = hidden > 0 && hidden < total;
    }}

    function showInfo(nodeId) {{
      const n = nodesDS.get(nodeId);
      if (!n || n.hidden) return;
      const neighborIds = network.getConnectedNodes(nodeId);
      const neighborItems = neighborIds.map(nid => {{
        const nb = nodesDS.get(nid);
        const color = nb && nb.color ? nb.color.background : '#4E79A7';
        const label = nb ? (nb.label || nb._qname || nb._path || nid) : nid;
        return `<span class="neighbor-link" style="border-left-color:${{esc(color)}}" onclick="window.focusNode(${{JSON.stringify(nid)}})">${{esc(label)}}</span>`;
      }}).join('');
      infoContent.innerHTML = `
        <div class="field"><b>${{esc(n.label)}}</b></div>
        <div class="field">Kind: ${{esc(n._kind || 'File')}}</div>
        <div class="field">Path: ${{esc(n._path || n.title || '')}}</div>
        <div class="field">Name: ${{esc(n._qname || '')}}</div>
        <div class="field">${{esc(payload.legend_title || 'Community')}}: ${{esc(n._community_name || '')}}</div>
        <div class="field">Degree: ${{n._degree || 0}}</div>
        ${{neighborIds.length
          ? `<div class="field" style="margin-top:8px;color:#94a3b8;font-size:11px">Neighbors (${{neighborIds.length}})</div><div id="neighbors-list">${{neighborItems}}</div>`
          : ''}}
      `;
    }}

    window.focusNode = function(nodeId) {{
      if (!network || !nodesDS) return;
      const n = nodesDS.get(nodeId);
      if (!n || n.hidden) return;
      network.focus(nodeId, {{ scale: 1.35, animation: true }});
      network.selectNodes([nodeId]);
      showInfo(nodeId);
    }};

    function render(maxDepth) {{
      const sub = neighborhood(maxDepth);
      nodesDS = new vis.DataSet(sub.nodes.map(n => ({{
        ...n,
        hidden: hiddenCommunities.has(n.community),
      }})));
      edgesDS = new vis.DataSet(sub.edges);
      const options = {{
        physics: {{
          enabled: true,
          solver: 'forceAtlas2Based',
          forceAtlas2Based: {{
            gravitationalConstant: -55,
            centralGravity: 0.008,
            springLength: 110,
            springConstant: 0.08,
            damping: 0.45,
            avoidOverlap: 0.9,
          }},
          stabilization: {{ iterations: 160, fit: true }},
        }},
        interaction: {{
          hover: true,
          tooltipDelay: 80,
          hideEdgesOnDrag: true,
          navigationButtons: false,
          keyboard: false,
        }},
        nodes: {{ shape: 'dot', borderWidth: 1.5 }},
        edges: {{
          arrows: {{ to: {{ enabled: true, scaleFactor: 0.55 }} }},
          smooth: {{ type: 'continuous', roundness: 0.25 }},
          selectionWidth: 2,
        }},
      }};
      if (network) network.destroy();
      network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, options);
      network.once('stabilizationIterationsDone', () => {{
        network.setOptions({{ physics: {{ enabled: false }} }});
        const seed = payload.seed_id;
        if (seed && nodesDS.get(seed) && !nodesDS.get(seed).hidden) {{
          network.focus(seed, {{ scale: 1.2, animation: false }});
          network.selectNodes([seed]);
          showInfo(seed);
        }}
      }});
      network.on('click', params => {{
        if (params.nodes.length > 0) showInfo(params.nodes[0]);
      }});
      const visible = sub.nodes.filter(n => !hiddenCommunities.has(n.community)).length;
      stats.textContent =
        visible + ' shown · ' + sub.edges.length + ' edges · depth ' + maxDepth +
        ' · mode ' + (payload.mode || 'files') +
        ' · ' + LEGEND.length + ' ' + (payload.legend_title || 'groups').toLowerCase() +
        ' · universe ' + allNodes.length;
    }}

    const legendEl = document.getElementById('legend');
    LEGEND.forEach(c => {{
      const item = document.createElement('div');
      item.className = 'legend-item';
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.className = 'legend-cb';
      cb.checked = true;
      cb.addEventListener('change', (e) => {{
        e.stopPropagation();
        if (cb.checked) {{
          hiddenCommunities.delete(c.cid);
          item.classList.remove('dimmed');
        }} else {{
          hiddenCommunities.add(c.cid);
          item.classList.add('dimmed');
        }}
        applyCommunityVisibility();
        updateSelectAllState();
        const visible = (nodesDS ? nodesDS.get().filter(n => !n.hidden).length : 0);
        stats.textContent =
          visible + ' shown · depth ' + depthInput.value +
          ' · mode ' + (payload.mode || 'files') +
          ' · universe ' + allNodes.length;
      }});
      item.innerHTML =
        `<div class="legend-dot" style="background:${{esc(c.color)}}"></div>` +
        `<span class="legend-label" title="${{esc(c.label)}}">${{esc(c.label)}}</span>` +
        `<span class="legend-count">${{c.count}}</span>`;
      item.prepend(cb);
      item.onclick = (e) => {{
        if (e.target === cb) return;
        cb.checked = !cb.checked;
        cb.dispatchEvent(new Event('change'));
      }};
      legendEl.appendChild(item);
    }});

    selectAllCb.addEventListener('change', () => {{
      const hide = !selectAllCb.checked;
      document.querySelectorAll('.legend-item').forEach(item => {{
        hide ? item.classList.add('dimmed') : item.classList.remove('dimmed');
      }});
      document.querySelectorAll('.legend-cb').forEach(cb => {{ cb.checked = !hide; }});
      LEGEND.forEach(c => {{
        if (hide) hiddenCommunities.add(c.cid); else hiddenCommunities.delete(c.cid);
      }});
      applyCommunityVisibility();
      updateSelectAllState();
    }});

    searchInput.addEventListener('input', () => {{
      const q = searchInput.value.trim().toLowerCase();
      if (!q) {{ searchResults.style.display = 'none'; searchResults.innerHTML = ''; return; }}
      const hits = allNodes
        .filter(n =>
          (n._path || '').toLowerCase().includes(q) ||
          (n._qname || '').toLowerCase().includes(q) ||
          (n.label || '').toLowerCase().includes(q) ||
          (n._kind || '').toLowerCase().includes(q)
        )
        .slice(0, 20);
      searchResults.style.display = 'block';
      searchResults.innerHTML = hits.map(n =>
        `<div class="search-item" data-id="${{esc(n.id)}}" style="border-left:3px solid ${{esc(n.color.background)}}">${{esc((n._kind ? n._kind + ': ' : '') + (n._qname || n._path || n.label))}}</div>`
      ).join('');
    }});
    searchResults.addEventListener('click', ev => {{
      const item = ev.target.closest('.search-item');
      if (!item) return;
      const id = item.getAttribute('data-id');
      const node = allNodes.find(n => n.id === id);
      if (node && hiddenCommunities.has(node.community)) {{
        hiddenCommunities.delete(node.community);
        document.querySelectorAll('.legend-cb').forEach((cb, i) => {{
          if (LEGEND[i] && LEGEND[i].cid === node.community) {{
            cb.checked = true;
            cb.closest('.legend-item').classList.remove('dimmed');
          }}
        }});
        applyCommunityVisibility();
        updateSelectAllState();
      }}
      if (nodesDS && nodesDS.get(id)) {{
        window.focusNode(id);
      }} else {{
        payload.seed_id = id;
        render(Number(depthInput.value));
      }}
      searchResults.style.display = 'none';
    }});

    depthInput.addEventListener('input', () => {{
      const d = Number(depthInput.value);
      depthVal.textContent = String(d);
      render(d);
    }});
    render(Number(depthInput.value));
  </script>
</body>
</html>
"""
