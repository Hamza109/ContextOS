"""~500-token chunker for Qdrant embeddings (FR-023; Appendix C)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.services.l5_pack import estimate_tokens

# Proposed tolerance around ~500 tokens (exact bound Not evidenced).
TARGET_TOKENS = 500
MIN_TOKENS = 350
MAX_TOKENS = 650


@dataclass(frozen=True)
class Chunk:
    repo_name: str
    file_path: str
    content: str
    token_count: int
    chunk_index: int


def chunk_text(
    text: str,
    *,
    repo_name: str,
    file_path: str,
    target_tokens: int = TARGET_TOKENS,
) -> list[Chunk]:
    """Split text into approximate ~500-token chunks."""
    if not text.strip():
        return []

    lines = text.splitlines(keepends=True)
    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_tokens = 0
    index = 0

    def flush() -> None:
        nonlocal buf, buf_tokens, index
        if not buf:
            return
        content = "".join(buf)
        tc = estimate_tokens(content)
        chunks.append(
            Chunk(
                repo_name=repo_name,
                file_path=file_path,
                content=content,
                token_count=tc,
                chunk_index=index,
            )
        )
        index += 1
        buf = []
        buf_tokens = 0

    for line in lines:
        line_tokens = estimate_tokens(line) or 1
        if buf and buf_tokens + line_tokens > target_tokens:
            flush()
        buf.append(line)
        buf_tokens += line_tokens
        if buf_tokens >= target_tokens:
            flush()

    flush()
    return chunks


def chunk_file(path: Path, *, repo_name: str, root: Path) -> list[Chunk]:
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if "\x00" in text:
        return []
    return chunk_text(text, repo_name=repo_name, file_path=rel)
