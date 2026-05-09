# Day 5 Deliverable: Tool Abuse

Complete the following steps and record findings in `docs/learning-tracker.md`.

## Steps

1. **Run the eval against the vulnerable agent.**

   ```
   python3 labs/day-05-tool-abuse/eval.py --agent vulnerable
   ```

   Record ASR overall and per attack type (ssrf, path_traversal, confused_deputy,
   budget_exhaustion, mcp_poisoning).

2. **Run the SSRF attack manually.**

   ```
   python3 labs/day-05-tool-abuse/attack/abuse_tools.py ssrf
   ```

   Check the response and the cases JSONL for whether `web_fetch` was called with the
   metadata endpoint URL. Note: in a non-cloud environment, the HTTP request will fail,
   but the tool call itself being made is the vulnerability.

3. **Run the confused deputy attack.**

   ```
   python3 labs/day-05-tool-abuse/attack/abuse_tools.py confused_deputy
   ```

   Note whether the agent validates the claimed "administrator" authority or acts on it.

4. **Check the tools.py implementation.**

   ```
   cat agents/reference/tools.py
   ```

   Identify what validation (if any) exists for the `web_fetch` URL parameter and the
   `read_doc` filename parameter. Note which vulnerabilities are in the tool implementation
   vs. which are in the agent's decision-making.

5. **Explain the confused deputy problem.**

   In one paragraph, explain why the confused deputy attack succeeds structurally — not
   "the model was tricked" but "the capability model is wrong." Identify what change to
   the architecture would prevent it.

6. **Document in `docs/learning-tracker.md`.**

   Update the Day 5 row with:
   - ASR overall and per category
   - Whether SSRF tool call was made (regardless of HTTP result)
   - Whether path traversal returned out-of-corpus content
   - One-sentence architectural fix for confused deputy

## Completion Criteria

- [ ] `eval.py --agent vulnerable` ran to completion
- [ ] SSRF attack run; tool_calls_made checked in cases JSONL
- [ ] Confused deputy attack run; result documented
- [ ] tools.py reviewed for validation gaps
- [ ] Confused deputy problem explained in own words
- [ ] Day 5 row in learning-tracker.md updated
