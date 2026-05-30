"""BM25 retrieval over Chunks.

Pure-Python via rank_bm25 — no compiled dependencies and no embedding API.
The corpus is small (< 500 chunks) and the domain vocabulary is narrow, so
keyword recall is enough; upgrade to embeddings only if recall is poor.
"""

from __future__ import annotations

import re
from typing import Iterable

from rank_bm25 import BM25Okapi

from webapp.helper.corpus import Chunk

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase + split on non-alphanumeric. No stemming — corpus is small."""
    return _TOKEN_RE.findall(text.lower())


class BM25Retriever:
    """Wraps rank_bm25 with a typed top_k API and a score floor."""

    def __init__(self, chunks: Iterable[Chunk]) -> None:
        self.chunks: list[Chunk] = list(chunks)
        if self.chunks:
            self._bm25 = BM25Okapi([tokenize(c.content) for c in self.chunks])
        else:
            self._bm25 = None

    def top_k(
        self, query: str, k: int = 5, floor: float = 0.5
    ) -> list[tuple[Chunk, float]]:
        """Return up to k (chunk, score) pairs ranked by BM25 score, descending.

        Chunks with score < floor are dropped — keeps the prompt clean when
        the user asks something off-corpus.
        """
        if self._bm25 is None or not self.chunks:
            return []
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            zip(self.chunks, scores, strict=True),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [(c, float(s)) for c, s in ranked[:k] if s >= floor]
