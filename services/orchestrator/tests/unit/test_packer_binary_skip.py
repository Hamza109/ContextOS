"""Binary skip during packing (EP-005 T009 / test_packer_binary_skip)."""

from __future__ import annotations

from pathlib import Path

from app.services.l5_pack import pack_repository
from tests.fixtures.ignore_exclusion_repo import materialize_ignore_exclusion_repo


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


def test_packer_fixture_binary_absent(tmp_path: Path, monkeypatch) -> None:
    root = materialize_ignore_exclusion_repo(tmp_path / "fixture_repo")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))
    result = pack_repository(root, "bin_fix")
    assert "photo.png" not in result.xml_content
