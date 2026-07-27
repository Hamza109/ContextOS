"""Exclusions absent from pack (T023 / SC-004 pack side)."""

from __future__ import annotations

from pathlib import Path

from app.services.l5_pack import pack_repository


def test_packer_excludes_gitignore_and_hard_paths(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    (root / "ok.py").write_text("x=1\n", encoding="utf-8")
    (root / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (root / "node_modules" / "p" / "i.js").parent.mkdir(parents=True)
    (root / "node_modules" / "p" / "i.js").write_text("1\n", encoding="utf-8")
    (root / "dist" / "b.js").parent.mkdir(parents=True)
    (root / "dist" / "b.js").write_text("1\n", encoding="utf-8")
    (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (root / "ignored.txt").write_text("nope\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    result = pack_repository(root, "ex")
    assert 'path="ok.py"' in result.xml_content
    assert 'path=".env"' not in result.xml_content
    assert "node_modules" not in result.xml_content
    assert 'path="dist' not in result.xml_content
    assert 'path="ignored.txt"' not in result.xml_content
