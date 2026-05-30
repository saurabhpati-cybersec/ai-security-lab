"""Markdown corpus loader and chunker for the on-screen helper.

Sources (relative to repo root):
- docs/*.md (recursive)
- labs/day-*/**/*.md
- GETTING_STARTED.md
- README.md
- DECISIONS.md (if present)

Explicitly skipped: agents/reference/corpus/ — those are deliberately
poisoned RAG documents used by the lab's attacks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

# ----- public types ---------------------------------------------------------


@dataclass(frozen=True)
class Chunk:
    path: str       # repo-relative, forward-slashed (e.g. "docs/threat-model.md")
    heading: str    # nearest H1/H2/H3 heading text; "" if file has no heading
    anchor: str     # GitHub-style slug of the heading
    content: str    # the chunk text (heading line + body)


# ----- public API -----------------------------------------------------------


_SLUG_NONWORD = re.compile(r"[^\w\s-]")
_SLUG_WS = re.compile(r"[\s_]+")


def slugify(heading: str) -> str:
    """GitHub-style heading slug: lower, drop punctuation, spaces → hyphens."""
    s = heading.strip().lower()
    s = _SLUG_NONWORD.sub("", s)
    s = _SLUG_WS.sub("-", s)
    s = s.strip("-")
    return s


def load_corpus(repo_root: Path) -> list[Chunk]:
    """Walk corpus sources under repo_root and return all chunks.

    Returns an empty list if no markdown is found. Safe to call on a tmp_path
    containing arbitrary .md files (used by tests).
    """
    chunks: list[Chunk] = []
    for md_path in _iter_corpus_files(repo_root):
        chunks.extend(_chunk_markdown(md_path, repo_root))
    return chunks


# ----- internals ------------------------------------------------------------


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
_MAX_CHUNK_CHARS = 1500


def _iter_corpus_files(repo_root: Path) -> Iterator[Path]:
    """Yield every markdown file we want to index.

    For test ergonomics: if the directory looks like a repo root (has docs/ or
    labs/), use the curated source list; otherwise treat it as a flat tree and
    yield every .md inside it.
    """
    looks_like_repo = (repo_root / "docs").is_dir() or (repo_root / "labs").is_dir()
    if not looks_like_repo:
        for p in sorted(repo_root.rglob("*.md")):
            yield p
        return

    # Curated sources for the real repo.
    sources: list[Path] = []
    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        for p in sorted(docs_dir.rglob("*.md")):
            # Skip our own specs/plans (they describe the helper itself; meta noise).
            if "superpowers" in p.parts:
                continue
            sources.append(p)
    labs_dir = repo_root / "labs"
    if labs_dir.is_dir():
        for p in sorted(labs_dir.rglob("*.md")):
            sources.append(p)
    for top in ("GETTING_STARTED.md", "README.md", "DECISIONS.md"):
        f = repo_root / top
        if f.is_file():
            sources.append(f)
    for p in sources:
        # Defensive: never index the poisoned RAG corpus.
        rel = p.relative_to(repo_root).as_posix()
        if rel.startswith("agents/reference/corpus/"):
            continue
        yield p


def _chunk_markdown(path: Path, repo_root: Path) -> Iterator[Chunk]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(repo_root).as_posix()

    headings = list(_HEADING_RE.finditer(text))
    if not headings:
        # No headings — emit the whole file as one chunk.
        body = text.strip()
        if body:
            yield from _split_long(
                Chunk(path=rel, heading="", anchor="", content=body)
            )
        return

    # If there's any preamble before the first heading, drop it (rare in our corpus).
    for i, m in enumerate(headings):
        start = m.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        heading_text = m.group(2).strip()
        body = text[start:end].strip()
        if not body:
            continue
        chunk = Chunk(
            path=rel,
            heading=heading_text,
            anchor=slugify(heading_text),
            content=body,
        )
        yield from _split_long(chunk)


def _split_long(chunk: Chunk) -> Iterator[Chunk]:
    """If content exceeds _MAX_CHUNK_CHARS, split on paragraph boundaries."""
    if len(chunk.content) <= _MAX_CHUNK_CHARS:
        yield chunk
        return
    paragraphs = chunk.content.split("\n\n")
    buf: list[str] = []
    size = 0
    for para in paragraphs:
        if size + len(para) > _MAX_CHUNK_CHARS and buf:
            yield Chunk(
                path=chunk.path,
                heading=chunk.heading,
                anchor=chunk.anchor,
                content="\n\n".join(buf),
            )
            buf, size = [], 0
        buf.append(para)
        size += len(para) + 2
    if buf:
        yield Chunk(
            path=chunk.path,
            heading=chunk.heading,
            anchor=chunk.anchor,
            content="\n\n".join(buf),
        )
