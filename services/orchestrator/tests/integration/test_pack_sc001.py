"""SC-001 pack integration (T024)."""

from __future__ import annotations

from pathlib import Path

from app.services.l5_pack import pack_repository


def test_sc001_xml_oriented_pack(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    (root / "lib").mkdir(parents=True)
    (root / "lib" / "util.py").write_text("def f():\n    return 42\n", encoding="utf-8")
    (root / "bin.dat").write_bytes(b"\x00\x01\x02\xff")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    result = pack_repository(root, "sc001")
    assert result.xml_content.startswith("<?xml")
    assert "<repository" in result.xml_content
    assert "<file path=" in result.xml_content
    assert result.token_count > 0
    assert "bin.dat" not in result.xml_content
    assert result.artifact_path is not None
    assert result.artifact_path.exists()
