"""Tests for the BM25 retriever."""

from __future__ import annotations

from pathlib import Path

from webapp.helper.corpus import Chunk, load_corpus
from webapp.helper.retriever import BM25Retriever, tokenize


def test_tokenize_lowercases_and_drops_punctuation():
    assert tokenize("What is ASR?") == ["what", "is", "asr"]
    assert tokenize("rank_bm25 v0.2.2") == ["rank", "bm25", "v0", "2", "2"]
    assert tokenize("") == []


def _make_chunks() -> list[Chunk]:
    return [
        Chunk("a.md", "Apples", "apples", "Apples are red and grow on trees."),
        Chunk("b.md", "Bananas", "bananas", "Bananas are yellow and curved."),
        Chunk("c.md", "Cherries", "cherries", "Cherries are small and red."),
    ]


def test_top_k_returns_most_relevant_chunk_first():
    r = BM25Retriever(_make_chunks())
    hits = r.top_k("yellow curved fruit", k=3)
    assert hits, "expected at least one hit"
    top_chunk, top_score = hits[0]
    assert top_chunk.path == "b.md"
    assert top_score > 0


def test_top_k_respects_floor():
    r = BM25Retriever(_make_chunks())
    # Query unrelated to any chunk → all scores low, floor filters them out.
    hits = r.top_k("quantum gravity universe", k=3, floor=2.0)
    assert hits == []


def test_top_k_empty_corpus_returns_empty():
    r = BM25Retriever([])
    assert r.top_k("anything", k=3) == []


def test_top_k_respects_k():
    chunks = _make_chunks()
    r = BM25Retriever(chunks)
    hits = r.top_k("red", k=2, floor=0.0)
    assert len(hits) <= 2


def test_top_k_over_real_corpus_finds_threat_model():
    repo_root = Path(__file__).resolve().parent.parent
    chunks = load_corpus(repo_root)
    r = BM25Retriever(chunks)
    hits = r.top_k("STRIDE threat model trifecta", k=5, floor=0.5)
    assert hits, "expected real corpus to return some hits for a domain query"
    top_paths = [c.path for c, _ in hits]
    # At least one of the top hits should be the threat model doc.
    assert any("threat-model" in p for p in top_paths), (
        f"expected threat-model.md in top-5, got {top_paths}"
    )


def test_retriever_finds_asr_glossary_entry():
    """Regression: a short acronym query like 'What is ASR?' must surface the
    glossary entry. Previously the whole glossary was one chunk and the term
    score was diluted below the BM25 floor (0.5).

    We use k=20 (matching the API) because many lab README files also mention
    ASR in passing and rank above the focused glossary chunk with k=5.
    """
    repo_root = Path(__file__).resolve().parent.parent
    corpus = load_corpus(repo_root)
    ret = BM25Retriever(corpus)
    hits = ret.top_k("What is ASR?", k=20, floor=0.5)
    # At least one hit must come from the glossary and mention ASR.
    glossary_hits = [c for c, _ in hits if "glossary" in c.path.lower()]
    assert glossary_hits, f"No glossary hits; got {[(c.path, c.heading) for c, _ in hits]}"
    asr_hit = [c for c in glossary_hits if "asr" in c.heading.lower() or "attack success" in c.heading.lower()]
    assert asr_hit, f"Glossary hits did not include the ASR entry; headings: {[c.heading for c in glossary_hits]}"
