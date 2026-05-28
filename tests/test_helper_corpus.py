"""Tests for the helper corpus loader and chunker."""

from __future__ import annotations

from pathlib import Path

from webapp.helper.corpus import Chunk, load_corpus, slugify


def test_slugify_lowercases_and_hyphenates():
    assert slugify("What is ASR?") == "what-is-asr"
    assert slugify("  Hello,  World!  ") == "hello-world"
    assert slugify("Tool/Use & Abuse") == "tooluse-abuse"
    assert slugify("") == ""


def test_chunk_markdown_splits_on_h1_and_h2(tmp_path: Path):
    md = tmp_path / "sample.md"
    md.write_text(
        "# Top\nintro text\n\n"
        "## First section\nbody of first\n\n"
        "## Second section\nbody of second\n"
    )
    chunks = load_corpus(tmp_path)
    assert len(chunks) == 3
    headings = [c.heading for c in chunks]
    assert headings == ["Top", "First section", "Second section"]
    assert chunks[0].path == "sample.md"
    assert chunks[1].anchor == "first-section"
    assert "body of first" in chunks[1].content


def test_chunk_includes_heading_in_content(tmp_path: Path):
    md = tmp_path / "x.md"
    md.write_text("## Hello\nworld\n")
    chunks = load_corpus(tmp_path)
    # The chunk content should include the heading text so BM25 can match on it.
    assert "Hello" in chunks[0].content
    assert "world" in chunks[0].content


def test_load_corpus_includes_repo_docs():
    repo_root = Path(__file__).resolve().parent.parent
    chunks = load_corpus(repo_root)
    paths = {c.path for c in chunks}
    assert "docs/threat-model.md" in paths
    assert "GETTING_STARTED.md" in paths
    # At least one labs/day-* file present
    assert any(p.startswith("labs/day-") for p in paths)


def test_load_corpus_skips_poisoned_rag_corpus():
    repo_root = Path(__file__).resolve().parent.parent
    chunks = load_corpus(repo_root)
    for c in chunks:
        assert not c.path.startswith("agents/reference/corpus/"), (
            f"poisoned RAG corpus must not be indexed: {c.path}"
        )
