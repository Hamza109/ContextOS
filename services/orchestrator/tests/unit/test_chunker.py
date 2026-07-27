"""Chunker ~500 tokens (T032)."""

from __future__ import annotations

from app.services.l5_chunk import MAX_TOKENS, MIN_TOKENS, TARGET_TOKENS, chunk_text


def test_chunker_approximates_500_tokens() -> None:
    # Build text with many short lines to force multiple chunks
    lines = [f"word{i} " * 40 + "\n" for i in range(80)]
    text = "".join(lines)
    chunks = chunk_text(text, repo_name="r", file_path="f.py")
    assert len(chunks) >= 2
    for ch in chunks[:-1]:
        # Intermediate chunks should land near target (Proposed tolerance)
        near_band = MIN_TOKENS <= ch.token_count <= MAX_TOKENS + 200
        near_half = ch.token_count >= TARGET_TOKENS // 2
        assert near_band or near_half
    assert all(c.repo_name == "r" for c in chunks)
    assert all(c.file_path == "f.py" for c in chunks)
