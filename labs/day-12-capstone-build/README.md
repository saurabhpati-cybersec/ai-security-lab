# Day 12: Capstone Build — Compose All Defenses

## 1. Objective

Compose all defense layers into `agents/protected/agent.py`. Confirm the protected agent passes eval-all with documented residual risk. The deliverable is a measured ASR delta between the vulnerable baseline and the protected agent — not a description of defenses, but a number.

---

## 2. Why It Matters

A security control is only as good as its measurement. Deploying defenses without measuring them produces false confidence. This lab proves the defenses work together without breaking benign functionality — the measured ASR delta is the deliverable, not vague "it's more secure."

Production AI agent deployments fail in two directions: the agent is attacked (high ASR, no defenses), or the defenses are so aggressive that the agent stops being useful (high FPR, broken benign behavior). This lab forces you to hold both metrics simultaneously. A false-positive rate of 20% on benign inputs means one in five legitimate user requests gets blocked — that is a security control that kills the product.

The discipline of measuring both TPR (attack surface reduction) and FPR (benign regression) is what separates security engineering from security theater.

---

## 3. Threat Model Reference

| Threat ID | Description |
|-----------|-------------|
| T-01 | Direct prompt injection via user input |
| T-02 | Indirect prompt injection via tool results |
| T-03 | System prompt extraction |
| T-04 | Tool abuse: SSRF via web_fetch |
| T-05 | Tool abuse: path traversal via read_doc |
| T-06 | Confused deputy via send_message |
| T-07 | RAG corpus poisoning |
| T-08 | Data exfiltration via markdown rendering |
| T-09 | Egress via send_message with injected recipient |
| T-10 | Multi-step chaining (injection + tool + exfil) |
| T-11 | Encoded/obfuscated payloads |
| T-12 | Context window exhaustion |
| T-13 | Trust boundary confusion (tool result vs user input) |
| T-14 | Output manipulation via injection |
| T-15 | Lateral movement via tool chaining |
| T-16 | Credential harvesting from corpus |
| T-17 | Agent-to-agent injection (multi-agent escalation) |

This is the capstone integration lab: all T-01 through T-17 are in scope.

---

## 4. Trifecta Mapping

| Leg | Present | Notes |
|-----|---------|-------|
| A — Data access (`read_doc`) | Yes | Protected by ToolGateway path validation |
| B — Untrusted input | Yes | Protected by RulesDetector at input layer |
| C — Egress (`send_message`, `web_fetch`) | Yes | Protected by ToolGateway allowlists + OutputFilter |

All three legs of the lethal trifecta are present and addressed by the composed defense stack. Day 12 verifies this end-to-end.

---

## 5. Prerequisites

- Days 3-11 complete
- `agents/protected/agent.py` built and importable
- All datasets present in `evals/datasets/` (benign, direct_injection, indirect_injection, tool_abuse, rag_poison, exfiltration)
- `evals/harness/runner.py` working (`python3 evals/harness/smoketest.py` passes)
- API key set in `.env` (needed for live eval runs)

Verify the environment:

```
python3 evals/harness/smoketest.py
python3 -c "import sys; sys.path.insert(0,'.'); from agents.protected.agent import ProtectedAgent; print('OK')"
```

---

## 6. Hands-On Lab

**Step 1.** Review `agents/protected/agent.py` and confirm all five defense layers are present:

```
grep -n "RulesDetector\|ToolGateway\|OutputFilter\|ipi_tag\|emit_event" agents/protected/agent.py | head -30
```

You should see: `RulesDetector` for input checking, `ToolGateway` for tool dispatch, `ipi_tag` or equivalent for marking tool results, and `OutputFilter` for response scrubbing. Emit events should appear at each decision point.

**Step 2.** Confirm the import works cleanly:

```
python3 -c "import sys; sys.path.insert(0,'.'); from agents.protected.agent import ProtectedAgent; print('OK')"
```

If this fails, check `agents/protected/__init__.py` exists and `sys.path` is correct.

**Step 3.** Run eval against the benign dataset to confirm no false-positive regression:

```
python3 labs/day-12-capstone-build/eval.py --agent protected --dataset benign
```

The FPR on benign inputs must be at or near 0%. Any benign cases blocked by the defenses indicate the detector thresholds are too aggressive.

**Step 4.** Run eval against the direct injection dataset:

```
python3 labs/day-12-capstone-build/eval.py --agent protected --dataset direct_injection
```

Compare the ASR to the vulnerable baseline. A well-composed defense stack should show ASR significantly below the vulnerable agent's rate.

**Step 5.** Run eval against all datasets:

```
python3 labs/day-12-capstone-build/eval.py --agent protected --dataset all
```

Or use the Makefile shortcut once `make eval-all` is configured.

**Step 6.** Document residual risk: which attack classes still succeed against the protected agent? This is a required output of this lab — see Section 13 (Document).

---

## 7. Attack Scenario

N/A — Day 12 is the build phase, not the attack phase. Day 13 red-teams the protected agent that this day builds.

If you want to preview what Day 13 will test, review:

```
labs/day-13-capstone-attack/attack/adaptive_attacks.py
```

These are the bypass techniques specifically crafted to evade the defenses composed here.

---

## 8. Defensive Control

`agents/protected/agent.py` implements a five-layer composed defense stack:

```
User input
    ↓
[1] RulesDetector.check(input)          — rule-based injection pattern matching
    ↓ (if score < threshold, continue)
[2] LLM call (system prompt + user)     — model reasoning layer
    ↓
[3] ToolGateway.dispatch(tool, args)    — allowlist + argument validation per tool
    ↓
[4] IPI tagging on tool results         — marks tool output as untrusted content
    ↓
[5] OutputFilter.check(response)        — secret and exfil pattern scrubbing
    ↓
Agent response
```

Each layer emits structured events (`policy_violation`, `tool_call`, `model_call`, `detector_hit`) to the canonical log schema. These events are the ingestion surface for SOAR playbooks in Day 11 and `soar-companion/`.

**Layer 1 — RulesDetector:** Pattern-based detection on raw user input. Matches known injection patterns (role hijack, system override, encoded payload, instruction ignore). Threshold-configurable. Latency: <5ms.

**Layer 2 — LLM:** The model itself is not a defense — it is the component being defended. No defense relies solely on model training. However, the system prompt includes explicit instruction hierarchy reinforcement.

**Layer 3 — ToolGateway:** Validates every tool call before execution. `web_fetch` is restricted to an allowlist of domains. `read_doc` enforces path prefix constraints. `send_message` validates recipient domain against an allowlist. Unknown tools are blocked by default.

**Layer 4 — IPI tagging:** Tool results are wrapped with `[UNTRUSTED CONTENT — tool result]` markers before being returned to the model. This implements the trust boundary between system instructions and external content.

**Layer 5 — OutputFilter:** Scans the model's final response for API key patterns, secret-looking strings, and known exfiltration URL patterns. Blocks or redacts before returning to the user.

---

## 9. Expected Output

Running the Day 12 eval produces:

```
protected | benign          | Cases: 20 | FPR target: 0%
protected | direct_injection| Cases: 32 | ASR: ~0.20 (vs vulnerable ~0.65)
```

The exact ASR depends on your configured model and API temperature. Key success criteria:

- FPR on benign inputs: 0% or near-0% (≤ 5%)
- ASR reduction on direct_injection: at least 30 percentage points below vulnerable baseline
- No crashes or unhandled exceptions during eval run

If ASR on direct_injection is still above 0.40, review whether all five defense layers imported correctly.

---

## 10. Evaluation

```
python3 labs/day-12-capstone-build/eval.py --agent protected --dataset all
```

The eval script verifies datasets are present and prints case counts. For live ASR measurement (requires API key):

```
python3 -c "
import sys; sys.path.insert(0,'.')
from evals.harness.runner import run_eval
r = run_eval('evals/datasets/direct_injection.jsonl', 'protected', 60, 'evals/results')
print(f'ASR: {r[\"asr\"]:.2%}')
"
```

Success criteria for this lab:
- Static check: all datasets found (no missing files)
- Live eval: FPR on benign ≤ 5%
- Live eval: ASR on direct_injection ≤ 0.30

---

## 11. Difficulty

3/5

The agent code is already written (Day 11). The work here is measurement and documentation. The difficulty lies in correctly interpreting the eval output and honestly identifying residual risk — not in writing new code.

---

## 12. Time Required

4-6 hours

Breakdown:
- 30 min: verify agent imports and defense layers are present
- 1-2 hours: run evals (benign + direct_injection + all datasets)
- 1 hour: interpret results, compare to vulnerable baseline
- 1-2 hours: document residual risk in `docs/learning-tracker.md`

---

## 13. Document

After completing the lab, record in `docs/learning-tracker.md` for Day 12:

- Protected agent eval output: ASR on each dataset (benign, direct_injection, and any others run)
- Vulnerable baseline ASR for the same datasets (from Day 3-7 runs, or re-run now)
- ASR delta: `(vulnerable_ASR - protected_ASR)` for each dataset
- FPR on benign inputs: number and percentage of blocked benign cases
- 3-5 bullets on residual risk: which attack classes still succeed against the protected agent?

**Required deliverable:** "Protected agent eval output showing ASR delta vs vulnerable. Benign dataset FPR must be 0 or near-0."

Commit your learning-tracker entry:

```
git add docs/learning-tracker.md evals/results/
git commit -m "docs: add day-12 protected agent eval results and residual risk"
```

---

## 14. References

- OWASP LLM Top 10 2025 — LLM01: Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OWASP LLM Top 10 2025 — LLM08: Excessive Agency: https://genai.owasp.org/llmrisk/llm08-excessive-agency/
- NIST AI RMF 1.0 — Measure function: https://airc.nist.gov/RMF/Overview
- Perez & Ribeiro (2022), "Ignore Previous Prompt": https://arxiv.org/abs/2211.09527
- Greshake et al. (2023), "Not What You've Signed Up For": https://arxiv.org/abs/2302.12173
- Simon Willison, "The Dual LLM pattern": https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
- Anthropic, "Claude's Constitution": https://www.anthropic.com/research/claude-character
- Bootstrap confidence intervals for ASR: https://en.wikipedia.org/wiki/Bootstrapping_(statistics)
