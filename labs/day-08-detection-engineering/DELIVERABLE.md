# Day 8 Deliverable: Detection Engineering

Run `python3 labs/day-08-detection-engineering/eval.py` — record TPR and FPR. Note which injection categories are hardest to detect. Commit results to evals/results/. Document in learning-tracker.md.

## Checklist

- [ ] Ran `eval.py` and recorded TPR and FPR values
- [ ] Identified which injection categories (role_hijack, encoded_payload, indirect) had lowest TPR
- [ ] Tried at least two threshold values (e.g., 0.3 and 0.7) and observed tradeoff
- [ ] Reviewed `detectors/rules.py` and understand the weight system
- [ ] Documented findings in `docs/learning-tracker.md`
- [ ] Committed eval results to `evals/results/`

## Expected Metric

| Metric | Target |
|---|---|
| TPR @ threshold=0.5 | ≥ 65% |
| FPR @ threshold=0.5 | ≤ 15% |

Lower TPR on indirect injection is expected — rule-based detectors see raw user input, not structured tool results. Use `check_tool_result()` for IPI coverage.
