# Day 9 Deliverable: Input/Output Validation

Run `python3 labs/day-09-input-output-validation/eval.py` — record the catch rate per dataset. Observe false positive impact on benign.jsonl. Document the TPR/FPR tradeoff.

## Checklist

- [ ] Ran `eval.py` and recorded catch rates for `direct_injection` and `exfiltration`
- [ ] Ran the validation layer against `benign.jsonl` manually and observed FPR
- [ ] Traced at least one exfiltration case through both input check and output filter
- [ ] Extended the output filter with one new secret pattern
- [ ] Documented findings in `docs/learning-tracker.md`

## Expected Metrics

| Dataset | Target Catch Rate |
|---|---|
| direct_injection | ≥ 50% |
| exfiltration | ≥ 40% |

Note: Catch rates are measured without a live agent. Full defense evaluation requires `make eval-all` with the protected agent.
