# Day 2 Deliverable: Working Environment

Provide the following evidence that your environment is fully operational:

1. **Smoketest output** — screenshot or terminal paste of:
   ```
   python3 evals/harness/smoketest.py
   ```
   showing `Smoketest PASSED` as the final line.

2. **Eval pass** — terminal output of:
   ```
   python3 labs/day-02-lab-setup/eval.py
   ```
   showing all 3 checks passing:
   ```
   PASS: smoketest
   PASS: all critical imports
   PASS: 6 datasets found
   ```

3. **(With live API key) Benign eval output** — terminal paste of the benign.jsonl eval run showing:
   - `ASR: 1.00` (all 25 benign cases passed = 0% false positive rate at baseline)
   - `cases.jsonl` created in `evals/results/` with at least 25 entries

4. **(Bonus) Log schema events** — show that the `cases.jsonl` output contains entries with at minimum:
   - `model_call` events
   - `tool_call` events (if any tools were called)
   - `final_response` events
