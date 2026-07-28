"""Unit tests for Proposed OKF bundle adapter (EP-013 T011)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.okf_bundle import OkfBundle, extract_markdown_links


def test_write_read_list_and_concept_id_stability(tmp_path: Path) -> None:
    bundle = OkfBundle(tmp_path / "repo")
    bundle.write_concept(
        "docs/architecture/overview",
        type="Architecture Doc",
        title="Overview",
        description="System overview",
        tags=["architecture"],
        sources=[{"uri": "docs/architecture/overview.md"}],
        generated={"by": "process:contextos-okf-generator", "at": "2026-07-28T00:00:00Z"},
        repo="demo",
        index_revision="rev-1",
        body="# Overview\n\nSee [Spec](specs/ep-demo/spec.md).\n",
    )
    concept = bundle.read_concept("docs/architecture/overview")
    assert concept is not None
    assert concept.concept_id == "docs/architecture/overview"
    assert concept.type == "Architecture Doc"
    assert concept.frontmatter["repo"] == "demo"
    assert concept.frontmatter["index_revision"] == "rev-1"
    assert concept.sources[0]["uri"] == "docs/architecture/overview.md"
    listed = bundle.list_concepts()
    assert [c.concept_id for c in listed] == ["docs/architecture/overview"]
    index = bundle.write_index(listed)
    assert index.name == "index.md"
    assert "docs/architecture/overview" in index.read_text(encoding="utf-8")


def test_malformed_concepts_skipped_with_count(tmp_path: Path) -> None:
    bundle = OkfBundle(tmp_path / "repo")
    bundle.ensure_root()
    (bundle.root / "good.md").write_text(
        "---\ntype: Spec\ntitle: Good\n---\n\nBody\n",
        encoding="utf-8",
    )
    (bundle.root / "bad.md").write_text("no frontmatter here\n", encoding="utf-8")
    (bundle.root / "missing-type.md").write_text(
        "---\ntitle: No Type\n---\n\nBody\n",
        encoding="utf-8",
    )
    concepts = bundle.list_concepts()
    assert [c.concept_id for c in concepts] == ["good"]
    assert bundle.stats.malformed_skipped == 2


def test_extract_markdown_links() -> None:
    body = "See [A](docs/a.md) and [B](../skip.md) and [C](specs/x/spec)."
    assert extract_markdown_links(body) == ["docs/a", "specs/x/spec"]
