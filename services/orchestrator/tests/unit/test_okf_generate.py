"""Unit tests for Proposed OKF generator (EP-013 T011 / T014)."""

from __future__ import annotations

from pathlib import Path

from app.adapters.l1_parser import StructuralNode
from app.adapters.okf_bundle import OkfBundle, okf_bundle_root
from app.config import Settings
from app.security.ignore_policy import IgnorePolicy
from app.services.okf_generate import generate_okf_bundle
from tests.fixtures.okf_knowledge_repo_fixture import (
    EXPECTED_DOC_CONCEPT_IDS,
    materialize_okf_knowledge_repo,
)


def test_generate_emits_frontmatter_provenance_and_links(tmp_path: Path) -> None:
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    settings = Settings(okf_cache_dir=tmp_path / "okf", okf_enabled=True)
    policy = IgnorePolicy.from_repo(repo)
    allowed = [
        p
        for p in repo.rglob("*")
        if p.is_file() and not policy.is_excluded(p)
    ]
    entity = StructuralNode(
        "auth-authenticate",
        "okf-demo",
        "src/auth.py",
        "Method",
        "auth.authenticate",
        4,
        6,
        "rev-fixture",
    )
    result = generate_okf_bundle(
        repo,
        "okf-demo",
        settings=settings,
        policy=policy,
        allowed_paths=allowed,
        index_revision="rev-fixture",
        l1_entities=[entity],
    )
    assert result.status == "ok"
    assert result.concepts_written >= len(EXPECTED_DOC_CONCEPT_IDS)
    bundle = OkfBundle(okf_bundle_root(settings.okf_cache_dir, "okf-demo"))
    ids = {c.concept_id for c in bundle.list_concepts()}
    assert EXPECTED_DOC_CONCEPT_IDS.issubset(ids)
    assert any(i.startswith("structural/") for i in ids)
    arch = bundle.read_concept("docs/architecture/system-overview")
    assert arch is not None
    assert arch.type == "Architecture Doc"
    assert arch.frontmatter.get("sources")
    assert arch.frontmatter.get("generated", {}).get("by")
    assert arch.frontmatter.get("repo") == "okf-demo"
    assert arch.frontmatter.get("index_revision") == "rev-fixture"
    assert "Related" in arch.body
    assert ".md)" in arch.body
    # Metadata-only: must not dump full fixture secret content
    for concept in bundle.list_concepts():
        assert "must-not-become-okf-source" not in concept.body
        assert "SECRET_TOKEN" not in concept.body


def test_excluded_paths_never_become_sources(tmp_path: Path) -> None:
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    settings = Settings(okf_cache_dir=tmp_path / "okf", okf_enabled=True)
    policy = IgnorePolicy.from_repo(repo)
    allowed = [
        p
        for p in repo.rglob("*")
        if p.is_file() and not policy.is_excluded(p)
    ]
    result = generate_okf_bundle(
        repo,
        "okf-demo",
        settings=settings,
        policy=policy,
        allowed_paths=allowed,
        index_revision="rev-1",
    )
    assert result.status == "ok"
    bundle = OkfBundle(okf_bundle_root(settings.okf_cache_dir, "okf-demo"))
    forbidden_markers = (
        "must-not-become-okf-source",
        "SECRET_TOKEN",
        "node_modules/leak",
        "build/out",
        "ignored/secret",
        "secret.pem",
    )
    for concept in bundle.list_concepts():
        blob = concept.body + str(concept.frontmatter)
        for marker in forbidden_markers:
            assert marker not in blob
        for source in concept.sources:
            uri = source.get("uri") if isinstance(source, dict) else str(source)
            assert "node_modules" not in uri
            assert not uri.startswith("build/")
            assert not uri.startswith("ignored/")
            assert ".env" not in uri
            assert not uri.endswith(".pem")


def test_okf_disabled_is_noop(tmp_path: Path) -> None:
    repo = materialize_okf_knowledge_repo(tmp_path / "repo")
    settings = Settings(okf_cache_dir=tmp_path / "okf", okf_enabled=False)
    result = generate_okf_bundle(
        repo,
        "okf-demo",
        settings=settings,
        allowed_paths=[],
        index_revision="rev-1",
    )
    assert result.status == "disabled"
    assert result.concepts_written == 0
    assert not (tmp_path / "okf" / "okf-demo").exists()
