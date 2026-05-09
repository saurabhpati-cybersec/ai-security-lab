# ai-security-lab

A 14-day, depth-focused curriculum for engineers learning AI agent security by building, attacking, and defending a real tool-using agent. Every lab targets an agent with tools—no chatbot-only exercises. Every defense ships with an eval that produces a number. The material is written for SOC analysts, SOAR engineers, and detection engineers who already understand threat modeling and incident response and want to apply those skills to LLM-based systems.

## What this contains

| Section | Purpose | Key files |
|---|---|---|
| Reference agent | Canonical agent: 3 tools, explicit step loop, structured logging | `agents/reference/` |
| Vulnerable agent | Reference agent with defenses removed; attack target | `agents/vulnerable/` |
| Protected agent | Reference agent with all defenses applied; capstone output | `agents/protected/` |
| Eval harness | Runs attack/defense datasets, computes TPR/FPR/ASR with CIs | `evals/harness/` |
| Datasets (6 JSONL) | Benign, injected, exfil, tool-abuse, RAG-poison, edge-case | `evals/datasets/` |
| Detectors | Rule-based and LLM-as-judge prompt injection detectors | `detectors/` |
| Labs (day-00–day-14) | One lab per day; each has a brief, exploit, defense, eval | `labs/` |
| SOAR companion | Tines stories and XSOAR playbooks for AI agent IR | `soar-companion/` |
| Docs / threat model | STRIDE threat model, OWASP mapping, architecture notes | `docs/` |

## The 14-day plan

### Phase 1 – Foundations (Days 0–2)

| Day | Focus |
|---|---|
| 0 | Honest self-assessment; map gaps to curriculum |
| 1 | STRIDE threat model; OWASP LLM Top 10 mapping |
| 2 | Environment setup; smoketest; evals end-to-end |

### Phase 2 – Attacks (Days 3–7)

| Day | Attack |
|---|---|
| 3 | Direct injection: hijack agent task via system prompt |
| 4 | Indirect injection: payload embedded in fetched page |
| 5 | Tool abuse: coerce `send_message` outside mandate |
| 6 | RAG poisoning: adversarial doc in retrieval corpus |
| 7 | Data exfiltration: corpus leak via tool arg channel |

### Phase 3 – Defenses (Days 8–11)

| Day | Defense |
|---|---|
| 8 | Detection engineering: rules + LLM-as-judge, calibrate TPR/FPR |
| 9 | I/O validation: input allowlists, output exfil blocking |
| 10 | Tool sandboxing: per-tool allowlists, budgets, egress |
| 11 | Monitoring and evals: log ingestion, regression gate |

### Phase 4 – Capstone (Days 12–14)

| Day | Task |
|---|---|
| 12 | Build protected agent with all Phase 3 defenses |
| 13 | Red-team your protected agent; measure ASR delta |
| 14 | Write-up, OWASP mapping, SOAR playbooks, publish |

## Reference agent

The reference agent exposes three tools: `web_fetch` (retrieves a URL), `read_doc` (reads from the RAG corpus), and `send_message` (sends an outbound message to a configurable endpoint). It runs an explicit step loop—plan, act, observe, repeat—rather than a framework-managed loop, so the control flow is readable and attackable.

The vulnerable and protected variants share the same tool interface and the same step loop. They differ only in what happens at decision points: the vulnerable variant skips all validation; the protected variant passes inputs and outputs through detectors and a tool gateway before every tool call and after every model response.

Every execution emits structured log events for: `model_call`, `tool_call`, `tool_result`, `detector_hit`, `policy_violation`, `human_review_requested`, and `final_response`. These events feed the eval harness and can be forwarded to a SIEM or SOAR.

The primary model is Anthropic claude-sonnet-4-5 (or current Sonnet). OpenAI models are supported via a thin adapter that normalizes the tool-call schema; switching is one env var.

## Setup

```bash
git clone <repo>
cd ai-security-lab
cp .env.example .env   # add your keys
pip install -r requirements.txt
make test              # smoketest
make eval-all          # full eval suite
```

## What you can claim after finishing

- Built and attacked a tool-using LLM agent
- Engineered injection detection with calibrated TPR/FPR
- Implemented tool gateway: allowlists, budgets, egress
- Red-teamed own defense; measured ASR before/after
- Mapped to OWASP LLM Top 10 and Agentic Top 10
- Wrote Tines + XSOAR playbooks for AI agent IR
- Built eval harness with bootstrap confidence intervals

## What you cannot claim

- Production-grade RLHF or fine-tuning
- Adversarial ML at the model weights level
- Large-scale red-teaming infrastructure
- Formal verification of LLM behavior
- Real-world attacker dwell time or lateral movement

## License

MIT. Acknowledgements: [OWASP LLM Security Project](https://owasp.org/www-project-top-10-for-large-language-model-applications/), [Simon Willison](https://simonwillison.net/), [Embrace The Red](https://embracethered.com/) (Johann Rehberger), [Invariant Labs](https://invariantlabs.ai/).
