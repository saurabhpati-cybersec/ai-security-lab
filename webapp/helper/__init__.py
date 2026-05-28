"""On-screen helper: grounded Q&A over the lab's own docs.

Public surface:
- corpus.load_corpus(repo_root) -> list[Chunk]
- retriever.BM25Retriever
- hardening.check_selection(selection) -> HardeningResult
- answerer.build_prompt(...) / stream_synthesis(...) / has_any_key()
"""
