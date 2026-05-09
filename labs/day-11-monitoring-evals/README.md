# Day 11 — Monitoring & Evals: Canonical Logging and IR Runbook

## 1. Objective

Wire the canonical log schema into streaming evaluation; build online detection so that every agent
run produces structured events; build an IR runbook for "agent misbehaving in production." By the
end of this lab you have a complete monitoring pipeline from event emission to incident response.

## 2. Why It Matters

You cannot respond to what you cannot see. Most teams running LLM agents in 2024-2025 have no
structured event log tied to SOAR tooling. SOC/SOAR engineers already have the skills to build
detection and response pipelines — the gap is domain knowledge about what AI agent events to emit
and what to alert on.

This lab bridges that gap. The canonical log schema (`starter/python/log_schema.py`) provides the
structured events; the IR runbook provides the response procedure; and the eval harness provides
automated measurement of whether the monitoring pipeline is working.

## 3. Threat Model Reference

- T-15: Session replay / repudiation — without structured logs, attackers can deny that a session
  occurred or manipulate the record of what happened.

## 4. Trifecta Mapping

Monitoring spans all three trifecta legs. It is not a control for any single leg but rather the
observability layer that detects when any combination of legs becomes active simultaneously:
- Data leg active: `tool_call` events with `read_doc`
- Untrusted input leg active: `detector_hit` events with high confidence scores
- Egress leg active: `tool_call` events with `send_message` or `web_fetch`

The AI-006 alert fires when all three are active in the same session — the full trifecta.

## 5. Prerequisites

- Days 8-10 complete (detection, validation, tool gateway)
- Understanding of the canonical log schema in `starter/python/log_schema.py`
- Familiarity with the IR trifecta model from `docs/threat-model.md`

## 6. Hands-On Lab

### Step 1: Review the canonical log schema

Open `starter/python/log_schema.py` and understand all event types:
- `model_call` — emitted before every LLM inference
- `tool_call` — emitted when the agent requests a tool execution
- `tool_result` — emitted after a tool returns (includes `tool_result_size`)
- `detector_hit` — emitted when a detector fires (includes `detector_score`, `severity`)
- `policy_violation` — emitted when the tool gateway blocks a call
- `human_review_requested` — emitted when HITL checkpoint is triggered
- `final_response` — emitted with the agent's final response to the user

Note the `trifecta_legs_active` field — each event records which trifecta legs are currently
active. Alert AI-006 fires when all three appear in the same session.

### Step 2: Run the eval

```bash
python3 labs/day-11-monitoring-evals/eval.py
```

This runs two checks: the eval harness smoketest and the canonical log schema validation.
Both must pass for the monitoring pipeline to be considered operational.

### Step 3: Read the IR runbook

Open `defense/ir_runbook.md` and study the five IR phases (Triage, Contain, Eradicate, Recover,
Lessons Learned). Note the specific commands for each phase.

### Step 4: Simulate an incident

With an API key configured, simulate a data exfiltration attempt:

```bash
python3 labs/day-07-data-exfiltration/attack/exfil_demo.py send_message_exfil
```

Then check the outbox for unauthorized sends:

```bash
tail -20 agents/reference/outbox.jsonl
```

### Step 5: Walk through the runbook

Using the simulated incident from Step 4, work through each runbook phase:
- Phase 1: Identify the session ID and check trifecta legs
- Phase 2: What would you kill/preserve?
- Phase 3: Which corpus doc was the injection source?
- Phase 4: Run the eval — does it still PASS?
- Phase 5: Fill in `docs/incident-report-template.md`

## 7. Attack Scenario

**Agent misbehaves silently — multiple unauthorized sends before detection:**

Without structured logs and SOAR alerts, mean time to detect an unauthorized `send_message` is
hours or days. By the time a human notices something wrong, the attacker has already received
multiple messages containing sensitive corpus data.

With canonical logging and the AI-008 alert (first-seen recipient):
1. First `send_message` to `evil@attacker.com` emits a `tool_call` event
2. The outbox monitoring pipeline checks the recipient against the known-good list
3. AI-008 fires immediately on the first unauthorized send
4. SOAR creates an incident, pages on-call, and the agent session is terminated
5. Mean time to detect drops from hours to seconds

## 8. Defensive Control

The monitoring pipeline provides three layers:

1. **Canonical log schema** — every agent event is structured, typed, and written to JSONL so that
   downstream tools (Splunk, SOAR, `jq`) can consume it without custom parsing
2. **IR runbook** — 5-phase procedure from triage to lessons learned, with specific grep commands
   for common investigation steps
3. **Eval harness** — automated measurement of whether the monitoring pipeline is functional;
   run after every change to confirm no regression

Cross-reference `soar-companion/shared/alert-catalog.md` (built in Day 17) for the full catalog
of 15 alerts that fire on canonical log events.

## 9. Expected Output

```
PASS: eval harness smoketest
PASS: canonical log schema

Day 11 eval: PASS
For full monitoring eval, run the protected agent against attack datasets
and check that detector_hit events appear in evals/results/*/cases.jsonl
```

## 10. Evaluation

```bash
python3 labs/day-11-monitoring-evals/eval.py
```

Runs smoketest + log schema check. No API key required.

## 11. Difficulty

2/5 — The monitoring components are already built; this lab is about understanding and wiring them.

## 12. Time Required

2–3 hours

## 13. What to Document

- Confirm eval PASS (record in `docs/learning-tracker.md`)
- Read and annotate `defense/ir_runbook.md` with one example per phase from your simulated attack
- Cross-reference `soar-companion/shared/alert-catalog.md` when available (Day 17)

## 14. References

See `references.md` in this directory.

Key references:
- NIST SP 800-61r3. Computer Security Incident Handling Guide. NIST, 2024.
- MITRE ATLAS. AI Threat Matrix. MITRE Corporation.
- Rehberger, J. Embrace The Red. embracethered.com
- Willison, S. LLM security monitoring. simonwillison.net
- OWASP LLM10:2025 Unbounded Consumption.
