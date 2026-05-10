# Getting Started — AI Security Lab

Step-by-step guide to set up, run, and work through the 14-day curriculum.

---

## Prerequisites

- Python 3.11 or higher
- Git
- At least one API key: Anthropic **or** OpenAI (both is better)
- Basic familiarity with terminal/shell

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/saurabhpati-cybersec/ai-security-lab.git
cd ai-security-lab
```

---

## Step 2 — Set Up API Keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

You can use either key alone or both together. The agents default to Anthropic; switching to OpenAI is one line change in the agent config.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the Anthropic SDK, OpenAI SDK, Pydantic v2, httpx, numpy, rich, and everything else the lab needs.

---

## Step 4 — Run the Smoketest

Verifies the core modules work without calling any API:

```bash
make test
```

Expected output:

```
Smoketest PASSED — 38/38 assertions
```

If this fails, check your Python version (`python3 --version`) and that all dependencies installed cleanly.

---

## Step 5 — Understand the Three Agents

The lab has three agents that share the same tool interface:

| Agent | Location | Purpose |
|---|---|---|
| Reference | `agents/reference/` | Canonical baseline — clean, readable, well-logged |
| Vulnerable | `agents/vulnerable/` | No defenses — your attack target |
| Protected | `agents/protected/` | All defenses applied — your capstone output |

Each agent has three tools:
- `web_fetch` — fetches a URL (8KB limit, SSRF prevention)
- `read_doc` — reads a file from the RAG corpus
- `send_message` — sends an outbound message (logged to `outbox.jsonl`)

---

## Step 6 — Run the Reference Agent

```bash
python3 agents/reference/agent.py
```

This runs a sample task and prints structured log events. You will see the agent:
1. Receive a user task
2. Call tools in a step loop
3. Emit JSON log events for every action
4. Return a final response

---

## Step 7 — Run the Full Eval Suite

With API keys set, run all six datasets against both agents:

```bash
make eval-all
```

This produces:
- `evals/results/cases.jsonl` — one result per test case
- `evals/results/summary.json` — ASR, TPR, FPR with confidence intervals
- `evals/results/latest_summary.md` — human-readable table

Key metrics to watch:
- **ASR (Attack Success Rate)** — lower is better for the protected agent
- **TPR (True Positive Rate)** — how often the detector catches real attacks
- **FPR (False Positive Rate)** — how often it flags benign inputs

---

## Step 8 — Work Through the Labs (14-Day Plan)

Each lab is self-contained in `labs/day-XX-name/`. Open the `brief.md` first, then follow the exploit and defense files.

### Phase 1 — Foundations (Days 0–2)

| Day | What to do |
|---|---|
| `day-00` | Read `brief.md` — honest self-assessment of your AI security knowledge gaps |
| `day-01` | Work through the STRIDE threat model in `docs/threat-model.md`, map to OWASP LLM Top 10 |
| `day-02` | Set up your environment (Steps 1–7 above), run smoketest and evals end-to-end |

### Phase 2 — Attacks (Days 3–7)

Run each attack against the **vulnerable agent**:

```bash
# Example: run the direct injection dataset
python3 evals/harness/runner.py \
  --dataset evals/datasets/direct_injection.jsonl \
  --agent vulnerable
```

| Day | Attack | Dataset |
|---|---|---|
| `day-03` | Direct injection — hijack agent via crafted user prompt | `direct_injection.jsonl` |
| `day-04` | Indirect injection — payload hidden in a fetched web page | `indirect_injection.jsonl` |
| `day-05` | Tool abuse — coerce `send_message` outside its mandate | `tool_abuse.jsonl` |
| `day-06` | RAG poisoning — adversarial document in the corpus | `rag_poison.jsonl` |
| `day-07` | Data exfiltration — leak corpus contents via tool args | `exfiltration.jsonl` |

Each lab's `exploit/` folder contains example payloads. Study them, understand *why* they work, then move to the defense.

### Phase 3 — Defenses (Days 8–11)

Apply each defense layer and re-run evals to measure improvement:

| Day | Defense | Key file |
|---|---|---|
| `day-08` | Detection engineering — rules + LLM-as-judge detector | `detectors/rules.py`, `detectors/classifier.py` |
| `day-09` | I/O validation — input allowlists, output exfil blocking | `detectors/output_filter.py` |
| `day-10` | Tool sandboxing — per-tool allowlists, budgets, egress control | `labs/day-10-sandboxing-permissions/defense/tool_gateway.py` |
| `day-11` | Monitoring and evals — log ingestion, regression gate | `starter/python/log_schema.py` |

After each day, run the eval to see your ASR drop:

```bash
make eval-all
```

### Phase 4 — Capstone (Days 12–14)

| Day | Task |
|---|---|
| `day-12` | Wire all Phase 3 defenses into `agents/protected/agent.py` |
| `day-13` | Red-team your protected agent, measure ASR delta vs vulnerable |
| `day-14` | Write your findings, map to OWASP, review SOAR playbooks |

---

## Step 9 — Explore the SOAR Companion

The `soar-companion/` folder contains ready-to-import automation for security teams:

```
soar-companion/
├── shared/
│   ├── log-schema.md          # 18-field canonical log schema
│   ├── alert-catalog.md       # AI-001 through AI-015 alert definitions
│   └── playbook-templates/    # Mermaid flowcharts for 4 response playbooks
├── tines/
│   └── stories/               # 3 Tines story JSONs — import directly
└── xsoar/
    ├── playbooks/             # 3 XSOAR 8.x playbook YAMLs
    ├── integrations/          # 2 integration stubs
    └── incident-fields/       # 18 custom AI security incident fields
```

**To use with Tines:** Go to your Tines tenant → Stories → Import → upload a JSON from `soar-companion/tines/stories/`.

**To use with XSOAR:** Upload YAMLs from `soar-companion/xsoar/playbooks/` via Settings → Integrations → Playbooks.

---

## Step 10 — Switching Between Anthropic and OpenAI

The adapters in `starter/python/` normalize both APIs to the same interface.

**Use Anthropic (default):**
```python
from starter.python.anthropic_client import AnthropicAdapter
client = AnthropicAdapter()
response, logs = client.run(messages, tools)
```

**Use OpenAI:**
```python
from starter.python.openai_client import OpenAIAdapter
client = OpenAIAdapter()
response, logs = client.run(messages, tools)
```

Both adapters accept the same tool definitions and return the same `(response_text, log_events)` tuple.

---

## Common Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run smoketest (no API key needed)
make test

# Run full eval suite
make eval-all

# Run a specific dataset against a specific agent
python3 evals/harness/runner.py \
  --dataset evals/datasets/direct_injection.jsonl \
  --agent vulnerable

# Run the reference agent
python3 agents/reference/agent.py

# Run the vulnerable agent
python3 agents/vulnerable/agent.py

# Run the protected agent
python3 agents/protected/agent.py

# Lint and format
ruff check .
black .

# Clean cache files
make clean
```

---

## Troubleshooting

**`ModuleNotFoundError`** — Run `pip install -r requirements.txt` from the repo root.

**`ANTHROPIC_API_KEY not set`** — Make sure `.env` exists and has your key. The `.env` file must be in the repo root.

**`Smoketest FAILED`** — Check Python version (`python3 --version` must be 3.11+).

**Eval hangs** — You may have hit a rate limit. Wait 30 seconds and retry.

**`send_message` writes to `outbox.jsonl`** — This is expected. It's the agent's outbound channel, logged locally for inspection.

---

## Project Structure

```
ai-security-lab/
├── agents/
│   ├── reference/          # Canonical agent (read this first)
│   ├── vulnerable/         # Attack target
│   └── protected/          # Capstone output
├── detectors/
│   ├── rules.py            # Rule-based detector (17 rules, <1ms)
│   ├── classifier.py       # LLM-as-judge detector (<500ms)
│   └── output_filter.py    # Output exfil blocker
├── evals/
│   ├── datasets/           # 6 JSONL datasets (187 total cases)
│   ├── harness/            # Runner, scorers, smoketest
│   └── results/            # Output from eval runs
├── labs/                   # Day-by-day labs (day-00 through day-14)
├── soar-companion/         # Tines + XSOAR automation
├── starter/python/         # Adapters, log schema, shared utilities
├── docs/                   # Threat model, glossary, references
├── .env.example            # Copy to .env and add your keys
├── requirements.txt
└── Makefile
```
