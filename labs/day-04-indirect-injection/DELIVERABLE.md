# Day 4 Deliverable: Indirect Prompt Injection

Complete the following steps and record findings in `docs/learning-tracker.md`.

## Steps

1. **Run the eval against the vulnerable agent.**

   ```
   python3 labs/day-04-indirect-injection/eval.py --agent vulnerable
   ```

   Record aggregate ASR and per-category (web_fetch_injection, rag_doc_injection, multi_stage).

2. **Compare with Day 3 direct injection ASR.**

   Note whether IPI ASR is higher or lower than direct injection ASR and write one sentence
   on why the difference exists (or why they are similar).

3. **Run at least two payload variants.**

   ```
   python3 labs/day-04-indirect-injection/attack/inject_indirect.py direct_sim
   python3 labs/day-04-indirect-injection/attack/inject_indirect.py html_comment
   ```

   Note whether the html_comment variant triggers the same behavior as direct_sim.
   If it does not, explain why the model may be treating the content differently.

4. **Describe the multi-stage attack chain.**

   Without running code, write out the five steps of the GitHub README attack scenario
   in your own words. Identify which step requires which trifecta leg.

5. **Document in `docs/learning-tracker.md`.**

   Update the Day 4 row with:
   - ASR overall and per category
   - Comparison with Day 3 ASR
   - Which payload type appeared most effective
   - Which trifecta leg, if removed, would break the attack

## Completion Criteria

- [ ] `eval.py --agent vulnerable` ran to completion
- [ ] ASR recorded and compared with Day 3 baseline
- [ ] At least two payload types tested manually
- [ ] Multi-stage attack chain described in own words
- [ ] Day 4 row in learning-tracker.md updated
