"""Unit tests for Proposed OKF retrieve (EP-013 T018)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.okf_bundle import OkfBundle
from app.config import Settings
from app.services.okf_retrieve import attach_okf_evidence, retrieve_okf


def _seed_bundle(root: Path) -> OkfBundle:
    bundle = OkfBundle(root)
    bundle.write_concept(
        "docs/architecture/system-overview",
        type="Architecture Doc",
        title="Architecture Overview",
        description="API contract and hybrid search layers",
        tags=["architecture", "api-contract"],
        sources=[{"uri": "docs/architecture/system-overview.md"}],
        generated={"by": "process:contextos-okf-generator", "at": "2026-07-28T00:00:00Z"},
        repo="demo",
        index_revision="rev-1",
        body=(
            "# Architecture Overview\n\n"
            "See [Demo Spec](specs/ep-demo-okf/spec.md).\n"
        ),
    )
    bundle.write_concept(
        "specs/ep-demo-okf/spec",
        type="Spec",
        title="Feature Specification: EP-Demo OKF",
        description="Demo epic for OKF retrieval",
        tags=["spec-kit", "ep-demo-okf"],
        sources=[{"uri": "specs/ep-demo-okf/spec.md"}],
        generated={"by": "process:contextos-okf-generator", "at": "2026-07-28T00:00:00Z"},
        repo="demo",
        index_revision="rev-1",
        body="# Spec\n",
    )
    return bundle


def test_exact_and_token_match_hit(tmp_path: Path) -> None:
    bundle = _seed_bundle(tmp_path / "demo")
    settings = Settings(okf_cache_dir=tmp_path, okf_enabled=True, okf_link_expand_limit=5)
    exact = retrieve_okf("demo", "Architecture Overview", settings=settings, bundle=bundle)
    assert exact.status == "hit"
    assert "docs/architecture/system-overview" in exact.matched_ids
    assert "<okf_evidence" in exact.evidence_block
    token = retrieve_okf(
        "demo",
        "what is the api contract architecture?",
        settings=settings,
        bundle=bundle,
    )
    assert token.status == "hit"
    assert any("architecture" in i for i in token.matched_ids)


def test_miss_does_not_fabricate(tmp_path: Path) -> None:
    bundle = _seed_bundle(tmp_path / "demo")
    settings = Settings(okf_cache_dir=tmp_path, okf_enabled=True)
    result = retrieve_okf(
        "demo",
        "zzzz-no-such-concept-qqq",
        settings=settings,
        bundle=bundle,
    )
    assert result.status == "miss"
    assert result.concepts == []
    assert result.evidence_block == ""
    assert attach_okf_evidence("<base/>", result) == "<base/>"


def test_bounded_link_expansion(tmp_path: Path) -> None:
    bundle = _seed_bundle(tmp_path / "demo")
    settings = Settings(okf_cache_dir=tmp_path, okf_enabled=True, okf_link_expand_limit=1)
    result = retrieve_okf(
        "demo",
        "Architecture Overview",
        settings=settings,
        bundle=bundle,
    )
    assert result.status == "hit"
    assert "docs/architecture/system-overview" in result.matched_ids
    assert "specs/ep-demo-okf/spec" in result.matched_ids
    assert len(result.concepts) <= 2  # seed + one expanded


def test_absent_bundle_is_miss_like(tmp_path: Path) -> None:
    settings = Settings(okf_cache_dir=tmp_path / "empty", okf_enabled=True)
    result = retrieve_okf("missing", "architecture", settings=settings)
    assert result.status == "absent"
    assert result.concepts == []
