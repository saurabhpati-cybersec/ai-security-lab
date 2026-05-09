# Day 6 Deliverable: RAG Corpus Poisoning

Complete the following steps and record findings in `docs/learning-tracker.md`.

## Steps

1. **Inspect the corpus before poisoning.**

   ```
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py list
   ```

   Note the legitimate documents present.

2. **Write the hidden-instruction poison document.**

   ```
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py poison hidden
   ```

3. **Query the agent on a topic covered by the poison document.**

   ```
   python3 agents/vulnerable/agent.py "What is the company password policy?"
   ```

   Note:
   - Does the agent retrieve the poison document?
   - Does the agent follow the embedded instructions?
   - Does the agent call `send_message`?

4. **Clean and try the high-cosine variant.**

   ```
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py clean
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py poison high_cosine
   python3 agents/vulnerable/agent.py "What are the credential management procedures?"
   ```

5. **Run the eval dataset.**

   ```
   python3 labs/day-06-rag-poisoning/eval.py --agent vulnerable
   ```

   Record ASR and per-category breakdown.

6. **Clean up the corpus.**

   ```
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py clean
   python3 labs/day-06-rag-poisoning/attack/poison_corpus.py list
   ```

   Verify no poison_*.md files remain.

7. **Explain citation laundering.**

   In one paragraph, explain how a poison document can make the agent attribute
   attacker-supplied instructions to a legitimate-sounding internal document name
   (e.g., "SOC-2025-Q2"), and why this increases the chance the user will comply.

8. **Document in `docs/learning-tracker.md`.**

   Update the Day 6 row with:
   - ASR from eval
   - Whether hidden or high_cosine triggered stronger response
   - Whether citation laundering occurred (agent cited a fake source)
   - What write-access control would prevent corpus poisoning

## Completion Criteria

- [ ] Corpus listed before poisoning
- [ ] hidden poison document written and agent queried
- [ ] high_cosine poison document written and agent queried
- [ ] `eval.py --agent vulnerable` ran to completion
- [ ] Corpus cleaned after lab
- [ ] Citation laundering explained in own words
- [ ] Day 6 row in learning-tracker.md updated
