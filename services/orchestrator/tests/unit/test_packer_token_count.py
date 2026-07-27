"""Token pre-calculation on pack output (T022)."""

from __future__ import annotations

from pathlib import Path

from app.services.l5_pack import pack_repository


def test_packer_token_count_present(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    (root / "a.py").parent.mkdir(parents=True, exist_ok=True)
    (root / "a.py").write_text("def hello():\n    return 1\n", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_PACK_CACHE_DIR", str(tmp_path / "packs"))

    result = pack_repository(root, "tok")
    assert result.token_count > 0
    assert "<repository" in result.xml_content
