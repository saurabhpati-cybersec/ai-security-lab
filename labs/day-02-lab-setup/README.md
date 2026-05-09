# Day 2: Lab Environment Setup

## 1. Objective

Bring up the reference agent, run the eval harness smoketest, verify Anthropic and OpenAI adapters, run the smoketest against `benign.jsonl`, and confirm the canonical log schema is populated. By the end of this lab you will have a fully operational environment against which every subsequent attack and defense lab is measured.

---

## 2. Why It Matters

No incident can be measured without a working baseline. Before you attack or defend, you need to know four things:

1. The agent starts, receives a message, and responds — it works.
2. The eval harness produces a number (ASR, TPR, FPR) — you can measure change.
3. The log schema captures every event (model_call, tool_call, tool_result, final_response) — you have forensic evidence.
4. The benign dataset produces 0% FPR at baseline — you have a clean reference point.

Without a working baseline, Day 3's attack result is uninterpretable: you can't know whether the agent was vulnerable or whether the environment was broken. Every security metric is a delta from the baseline established today.

The SOAR playbooks in `soar-companion/` consume log events with the canonical schema defined in `starter/python/log_schema.py`. If that schema is not being emitted, none of the downstream detection and response automation works.

---

## 3. Threat Model Reference

N/A — this is a setup lab, not a direct attack. The threats that the baseline environment exposes (and which are measured starting Day 3) are documented in `docs/threat-model.md`.

---

## 4. Trifecta Mapping

N/A — this lab establishes the baseline against which all attacks are measured. The trifecta framework (data / untrusted_input / egress) applies to attack labs starting Day 3.

---

## 5. Prerequisites

- Python 3.11 or later (`python3 --version`)
- `pip` available (or `uv` for faster installs)
- Git installed and repo cloned
- `.env` file created with `ANTHROPIC_API_KEY` set (required for live agent tests; not required for smoketest)
- `make setup` completed (or `pip install -r requirements.txt` run directly)
- OpenAI API key optional — enables Step 7 adapter verification

---

## 6. Hands-On Lab

**Step 1 — Clone the repo and create your `.env`**

```bash
git clone <repo-url> ai-security-lab
cd ai-security-lab
cp .env.example .env
vi .env   # add: ANTHROPIC_API_KEY=sk-ant-...
```

If you already have the repo cloned, verify your `.env`:

```bash
grep ANTHROPIC_API_KEY .env
```

Expected: `ANTHROPIC_API_KEY=sk-ant-...` (non-empty value).

**Step 2 — Install dependencies**

```bash
make setup
```

This runs `pip install -r requirements.txt`. Verify the key packages are installed:

```bash
python3 -c "import anthropic, openai, dotenv, rich; print('deps OK')"
```

Expected: `deps OK`.

**Step 3 — Run the smoketest**

```bash
python3 evals/harness/smoketest.py
```

Expected terminal output:

```
Running smoketest…

--- regex criteria ---
  ok: regex matches case-insensitively in response
  ...
--- scorers ---
  ok: compute_asr([]) == 0.0
  ...

Smoketest PASSED
```

The smoketest validates the eval harness without making any live API calls. If it fails, diagnose the import error before proceeding.

**Step 4 — Run a manual agent test**

This requires a live `ANTHROPIC_API_KEY` in `.env`.

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from agents.vulnerable.agent import VulnerableAgent
a = VulnerableAgent()
result = a.run('What tools do you have available?')
print(result)
"
```

Expected: the agent describes its three tools (`web_fetch`, `read_doc`, `send_message`). Any structured response confirms the agent is live and callable.

**Step 5 — Run the eval against the benign dataset**

This requires a live API key and consumes API credits (~25 calls). The `max_api_calls=30` guard limits spend.

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from evals.harness.runner import run_eval
r = run_eval(
    'evals/datasets/benign.jsonl',
    'vulnerable',
    max_api_calls=30,
    output_dir='evals/results'
)
print(f'Dataset: benign.jsonl | Agent: vulnerable | Cases: {r[\"total\"]} | Passed: {r[\"passed\"]} | ASR: {r[\"asr\"]:.2f}')
"
```

Expected: `ASR: 1.00` — all 25 benign cases passed (0% false positive rate at baseline). If ASR is below 1.0, check that the eval criteria for benign cases use the `benign` criterion, which always returns True.

**Step 6 — Verify log events emitted**

After the eval run, check `evals/results/` for output:

```bash
ls evals/results/
# Should contain a directory or cases.jsonl from the run

# If a run directory was created:
ls evals/results/$(ls evals/results/ | grep -v .gitkeep | tail -1)/
```

Open `cases.jsonl` and verify it contains JSON objects with at minimum:
- `case_id`
- `prompt`
- `response`
- `tool_calls`
- `passed`

This confirms the harness is writing structured output that can be ingested by SOAR.

**Step 7 — (Optional) Verify the OpenAI adapter**

If you have `OPENAI_API_KEY` set in `.env`:

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from starter.python.openai_client import get_openai_client
client = get_openai_client()
response = client.chat.completions.create(
    model='gpt-4.1',
    messages=[{'role': 'user', 'content': 'Say hello in one word.'}],
    max_tokens=10
)
print(response.choices[0].message.content)
"
```

Expected: a single-word greeting. This confirms the OpenAI adapter is functional for labs that compare model behavior.

---

## 7. Attack Scenario

N/A — this is a setup lab. No attack is demonstrated here.

However, note that the baseline environment established today is **already vulnerable by design**. The vulnerable agent (`agents/vulnerable/agent.py`) has no input sanitization, no output detection, and no recipient allowlist on `send_message`. Day 3 will send the first direct injection payload and demonstrate that it works against this baseline.

The absence of controls is intentional: you need a vulnerable baseline to measure the effect of controls added in Days 8-10.

---

## 8. Defensive Control

N/A — foundational setup lab, no defense implemented.

---

## 9. Expected Output

**Smoketest (no API key required):**

```
Running smoketest…

--- regex criteria ---
  ok: regex matches case-insensitively in response
  ok: regex returns False when pattern not found
  ok: regex is case-insensitive (uppercase pattern, mixed-case text)
--- agent_called_tool criteria ---
  ...
Smoketest PASSED
```

**Day 2 eval (no API key required):**

```
PASS: smoketest
PASS: all critical imports
PASS: 6 datasets found
```

**Live benign eval (requires API key):**

```
Dataset: benign.jsonl | Agent: vulnerable | Cases: 25 | Passed: 25 | ASR: 1.00
```

ASR=1.00 on benign means all 25 benign cases passed — 0% false positive rate at baseline.

---

## 10. Evaluation

```bash
python3 labs/day-02-lab-setup/eval.py
```

The eval script runs three checks without requiring a live API key:

1. **Smoketest:** runs `evals/harness/smoketest.py` and checks for "Smoketest PASSED"
2. **Imports:** verifies `VulnerableAgent`, `LogEvent`, and `run_eval` import cleanly from repo root
3. **Datasets:** checks that 6 JSONL datasets exist in `evals/datasets/`

All three must pass. Prints `PASS` or `FAIL` with the specific failure reason.

---

## 11. Difficulty

1/5 — Setup and verification only. No threat analysis or code authoring required. The challenge is environment-specific (API keys, Python path).

---

## 12. Time Required

1–2 hours

- ~15 min: clone, install, create `.env`
- ~5 min: run smoketest
- ~30–60 min: troubleshoot any import or environment issues
- ~15 min: run live benign eval (if API key available)

---

## 13. Document

Deliverable for `DELIVERABLE.md`:

- Screenshot or terminal output of `python3 evals/harness/smoketest.py` printing "Smoketest PASSED"
- Terminal output of `python3 labs/day-02-lab-setup/eval.py` with all 3 checks passing
- (With live API key) Output of benign.jsonl eval showing ASR near 1.0 and `cases.jsonl` created in `evals/results/`
- Log events emitted for `model_call`, `tool_call`, `tool_result`, `final_response` event types

---

## 14. References

- [Anthropic Python SDK documentation](https://docs.anthropic.com/en/api/client-sdks)
- [OpenAI Python SDK documentation](https://platform.openai.com/docs/libraries/python-library)
- [python-dotenv documentation](https://github.com/theskumar/python-dotenv)
- [rich library (Progress, Console) documentation](https://rich.readthedocs.io/en/stable/)
- [Python 3.11 release notes](https://docs.python.org/3/whatsnew/3.11.html)
