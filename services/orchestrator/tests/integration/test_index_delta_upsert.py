"""Delta upsert replaces Qdrant chunks for changed file_path (T062)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.embeddings import HashEmbedder
from app.adapters.falkordb_store import InMemoryFalkorStore
from app.config import Settings
from app.services.l1_entity_cache import L1EntityCache
from app.services.l1_graph import L1GraphService
from app.services.l5_index import run_index


class DeltaStore:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def upsert_file_chunks(self, chunks, vectors, *, content_hashes=None):
        self.calls.append([c.file_path for c in chunks])
        return len(chunks)


def test_delta_reindex_scopes_to_file(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    (root / "a.py").write_text("a=1\n", encoding="utf-8")
    (root / "b.py").write_text("b=1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    store = DeltaStore()
    result = run_index(
        str(root),
        "delta",
        files=["a.py"],
        embedder=HashEmbedder(),
        store=store,  # type: ignore[arg-type]
    )
    assert result.mode == "incremental"
    assert result.files_indexed == 1
    assert store.calls
    assert set(store.calls[0]) == {"a.py"}


def test_delta_reconciles_only_affected_graph_paths(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "a.py").write_text("class A:\n pass\n", encoding="utf-8")
    (root / "b.py").write_text("class B:\n pass\n", encoding="utf-8")
    settings = Settings(
        falkordb_url="memory://delta",
        pack_cache_dir=tmp_path / "packs",
    )
    graph_store = InMemoryFalkorStore()
    service = L1GraphService(
        settings,
        store=graph_store,
        cache=L1EntityCache(),
    )
    run_index(str(root), "delta-graph", settings=settings, graph_service=service, skip_embed=True)
    original_b_ids = {
        node.entity_id
        for node in graph_store.nodes["delta-graph"].values()
        if node.source_path == "b.py"
    }
    (root / "a.py").write_text("class A2:\n pass\n", encoding="utf-8")
    result = run_index(
        str(root),
        "delta-graph",
        files=["a.py"],
        settings=settings,
        graph_service=service,
        skip_embed=True,
    )
    nodes = graph_store.nodes["delta-graph"].values()
    assert original_b_ids <= {node.entity_id for node in nodes}
    assert any(node.qualified_name.endswith("A2") for node in nodes)
    assert result.graph_nodes > 0


def test_delta_reindex_resolves_imports_to_unchanged_files(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    package = root / "pkg"
    package.mkdir(parents=True)
    (package / "auth.py").write_text("from .tokens import check\n", encoding="utf-8")
    (package / "tokens.py").write_text("def check():\n return True\n", encoding="utf-8")
    settings = Settings(
        falkordb_url="memory://delta",
        pack_cache_dir=tmp_path / "packs",
    )
    graph_store = InMemoryFalkorStore()
    service = L1GraphService(
        settings,
        store=graph_store,
        cache=L1EntityCache(),
    )
    run_index(str(root), "delta-imports", settings=settings, graph_service=service, skip_embed=True)

    (package / "auth.py").write_text("from .tokens import check\n\ncheck()\n", encoding="utf-8")
    run_index(
        str(root),
        "delta-imports",
        files=["pkg/auth.py"],
        settings=settings,
        graph_service=service,
        skip_embed=True,
    )

    nodes = graph_store.nodes["delta-imports"]
    file_imports = [
        edge
        for edge in graph_store.edges["delta-imports"]
        if edge.edge_kind == "IMPORTS"
        and nodes[edge.source_id].entity_kind == "File"
        and nodes[edge.target_id].entity_kind == "File"
    ]
    assert len(file_imports) == 1
    assert nodes[file_imports[0].source_id].source_path == "pkg/auth.py"
    assert nodes[file_imports[0].target_id].source_path == "pkg/tokens.py"
