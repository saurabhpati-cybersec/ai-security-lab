# Phase 0 Report — ASR Semantics Fix

## Summary

Corrected the inverted Attack Success Rate (ASR) across the eval harness,
web UI, lab scripts, and stored result files so that ASR = fraction of
attack cases the attack succeeded (the safety `success_criteria` was NOT
met). Benign datasets now report False Positive Rate (FPR); ASR is `null`
for benign. Error cases are excluded from every denominator. The historical
`evals/results/` summaries were back-filled in place (with `.bak`
preservation) so the GUI now displays consistent numbers.

## Per-task changes (11 commits on branch `fix/measurement-and-coverage`)

- **Task 1** — `604a1c3`, `5095c5a`: added `attack_success_rate(case_results)` in `evals/harness/scorers.py` with error-excluded denominator + `None` for undefined. Added `tests/test_asr_semantics.py` with 18 orientation pin tests covering the new helper, `compute_tpr_fpr`, `compute_asr`-as-generic-mean, and the detector-score path in `webapp/api/calibrate.py`.
- **Carry-forward** — `a066c8c`: brought the parent branch's in-flight runner.py edits (compound criteria + `_SECRET_PATTERNS()` shim) over as a standalone chore commit so Task 2's diff stays focused.
- **Task 2** — `19572a8`, `654ef1a`: rewrote `run_eval`'s aggregate-metrics block. Emits `schema_version=2`, `error_rate`, per-case `attack_succeeded`. Benign → `asr=None, fpr=...`. Per-category stats derived from `case_results` with errors excluded. Five new end-to-end runner tests.
- **Task 3** — `45b9269`, `7ff6c67`: added `scripts/rescore_results.py` to back-fill legacy `summary.json` files (idempotent, `.bak` preserved). Added `tests/test_rescore_results.py`. Also fixed the benign-detection heuristic in both runner and rescore — `Path(dataset).stem == "benign"` (the per-case `success_criteria` heuristic mis-classified the real benign dataset, which mixes `"benign"` with `"agent_called_tool:send_message"` for legitimate messaging cases).
- **Task 4** — `cfdf14b`: `webapp/api/runs.py` accepts nullable `asr`, surfaces `fpr` / `error_rate` / `schema_version`. Two new regression tests.
- **Task 5** — `dfc987a`, `c3c1162`: `webapp/templates/eval.html`, `results.html`, and `webapp/static/js/glossary.js` render `FPR` for benign runs, fall back to `N/A` when both are null, guard nulls in the diff (`'N/A (benign dataset)'`), use dynamic ASR/FPR labels in summary tiles, per-category headers, and compare panel. Glossary rewritten + `fpr` entry added.
- **Task 6** — `21e8c17`: chat system prompt, `scripts/eval_all.py` (benign → FPR semantics), `labs/day-03/eval.py` (null-safe), `labs/day-09/eval.py` (clarifying comment explaining `compute_asr` is the generic mean helper there, not the ASR semantic).

## Before / after — `direct_injection` (concrete sample)

```
protected_direct_injection_20260528T160833Z:
  legacy asr=0.9  ->  corrected asr=0.1  (errors=0)

vulnerable_direct_injection_20260528T153459Z:
  legacy asr=0.75  ->  corrected asr=0.25  (errors=0)

vulnerable_direct_injection_20260528T160642Z:
  legacy asr=0.8  ->  corrected asr=0.2  (errors=0)
```

Under the legacy schema, the protected agent showed `asr=0.9` — nearly
identical to vulnerable — because "attack succeeded" and "attack blocked"
were swapped. After the fix, protected shows `asr=0.1` versus vulnerable's
`asr=0.25`, correctly reflecting that the protected agent blocked most
attacks.

## Vuln-vs-prot diff on migrated `evals/results/`

```
dataset                     vuln_max   prot_min      delta  result
---------------------------------------------------------------------------
direct_injection              0.2500     0.1000    +0.1500  defense helps
```

Positive `delta` = vulnerable ASR > protected ASR = defenses help.

## Benign FPR on migrated runs

```
  vulnerable_benign_20260510T074045Z: agent=vulnerable asr=None fpr=0.0
  vulnerable_benign_20260510T074238Z: agent=vulnerable asr=None fpr=0.0
  vulnerable_benign_20260528T054115Z: agent=vulnerable asr=None fpr=0.0
  vulnerable_benign_20260528T071113Z: agent=vulnerable asr=None fpr=0.0
  vulnerable_benign_20260528T161553Z: agent=vulnerable asr=None fpr=0.0
```

The migrated benign runs now correctly report `asr=None` with a numeric
`fpr`. Under the legacy schema they would have shown `asr=0.0`.

## Tests added

- `tests/test_asr_semantics.py` — 18 cases (run-eval end-to-end + orientation pins for `compute_tpr_fpr`, `compute_asr`, and the detector-score path in `webapp/api/calibrate.py`).
- `tests/test_rescore_results.py` — 6 cases (idempotency, attack flip, benign FPR, error exclusion, dataset-stem heuristic).
- Full suite: 186 passed (was 162 baseline).

## Deviations from the brief

- Plan said the day-09 lab eval used `compute_asr` over inverted booleans. After reading the file, this was incorrect — day-09 computes block rate using `True = blocked` and prints "% blocked"; the use of `compute_asr` is as the generic mean helper, which is documented behavior. Resolution: added a clarifying comment instead of a semantic refactor.
- Plan asked to commit migrated `evals/results/` files. The directory is `.gitignore`d, so the migration is local-only (the rescore script is committed; anyone with the same `cases.jsonl` can reproduce the migrated summaries).
- Plan's benign-detection heuristic was `all(case.success_criteria == "benign")`. The real benign dataset mixes criteria, so this heuristic mis-classified benign runs as attack and reported `asr=0.0`. Fixed during the Task 3 cycle by switching to `Path(dataset).stem == "benign"` in both runner and rescore script.
- Phase 1+ (multi-sample CIs, kill-chain criteria, canonicalize-then-detect, Arcanum taxonomy, agent-domain coverage, securing the tool itself, UI polish) are out of scope for P0 and not addressed.

## Known minor follow-ups

All review findings addressed — see commit <SHA>.

- Extracted `per_category_metrics()` to `scorers.py`; `runner.py` and `rescore_results.py` now both call the shared helper, eliminating duplication-drift risk. Pin test added in `test_asr_semantics.py`.
- `results.html` compare panel: replaced the misleading "lower is better" framing with an explicit "B is X pp lower/higher than A" label (user controls left/right, so directional framing was wrong). Colour coding changed to neutral (`delta-neutral`) for both signs.
- Cleared 4 lint nits: `webapp/api/chat.py` (`from collections.abc import AsyncIterator`, two long signatures split); `scripts/eval_all.py` (long note string wrapped).

Remaining non-blocking notes:

- `webapp/api/calibrate.py` is functionally independent of the harness ASR — its `_scores` orientation is pinned by a Task 1 test.
- Only `direct_injection` has both vulnerable + protected runs in the migrated results; `rag_poison` and `tool_abuse` have only vulnerable runs in the local result set.
