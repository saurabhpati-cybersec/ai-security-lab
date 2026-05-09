# detectors/

Three complementary detectors for catching prompt injection and preventing data exfiltration in AI agent pipelines.

## What each detector does

### `RulesDetector` (rules.py)
Regex/heuristic detector that matches known injection patterns: instruction overrides (`ignore previous instructions`), role hijacks (`act as DAN`), system prompt extraction attempts, exfiltration triggers, and hidden Unicode markers. Returns a `DetectionResult` with a confidence score (0.0–1.0) computed from the highest-weight matching rule, boosted slightly when multiple rules fire together.

### `ClassifierDetector` (classifier.py)
LLM-as-judge classifier that sends text to `claude-haiku-4-5` with a carefully worded system prompt, then parses the returned JSON `{"is_injection": bool, "confidence": float, "reasoning": str}`. Higher accuracy than rules alone, at the cost of latency and API spend.

### `OutputFilter` (output_filter.py)
Post-generation filter that scans agent output for exfiltration vectors: markdown images pointing to non-allowlisted domains, hyperlinks to non-allowlisted domains, and known fake secret strings from the lab corpus. Blocked elements are replaced inline; callers receive the cleaned text plus a `violations` list.

## Latency targets

| Detector | Target | Typical (local) |
|---|---|---|
| `RulesDetector.check()` | < 5 ms | < 1 ms |
| `ClassifierDetector.check()` | < 500 ms | 200–400 ms |
| `OutputFilter.filter()` | < 5 ms | < 1 ms |

## How to choose

**Rules-only** — use when latency budget is tight (< 5 ms) or when operating at high volume without per-call API spend. Expect higher false-negative rate on novel phrasings.

**Classifier-only** — use when accuracy matters more than latency and you have an API key. Provides reasoning for each decision, useful for audit trails.

**Compose both with short-circuit** — the recommended pattern for production:
```python
rules_result = rules_detector.check(text)
if rules_result.is_injection:
    return rules_result          # fast path: block immediately
clf_result = classifier_detector.check(text)  # only call LLM when rules pass
```
This keeps median latency near the rules-only baseline while using the classifier as a safety net for evasive injections.

## How to calibrate the threshold

Run both detectors against the provided datasets and pick the operating point that fits your risk tolerance:

```bash
# Score rules detector against all eval datasets
python3 -c "
import sys; sys.path.insert(0, '.')
import json
from detectors.rules import RulesDetector
from pathlib import Path

r = RulesDetector()
for ds in ['benign', 'direct_injection', 'indirect_injection']:
    path = Path(f'evals/datasets/{ds}.jsonl')
    samples = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    hits = sum(1 for s in samples if r.check(s['content']).is_injection)
    print(f'{ds}: {hits}/{len(samples)} flagged')
"
```

Adjust `threshold` (default 0.5 for rules, 0.7 for classifier) until FPR on `benign.jsonl` is acceptable for your use case.

**Important:** TPR and FPR are dataset-dependent. The reference values in docstrings (TPR ~0.85, FPR ~0.05 for the classifier at threshold=0.7) were measured on the bundled lab datasets. Always measure on data representative of your own deployment — real enterprise queries and real attack payloads may differ substantially from the lab corpus.
