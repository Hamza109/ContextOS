"""Binary skip during packing (T021)."""

from __future__ import annotations

from pathlib import Path

from app.services.l5_pack import pack_repository


def test_packer_skips_binaries(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "img.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    result = pack_repository(root, "demo")
    assert "main.py" in result.xml_content
    assert "img.png" not in result.xml_content
    assert result.files_packed == 1
