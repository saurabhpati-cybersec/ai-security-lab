# AI Agent Incident Response Runbook

## Trigger Conditions

This runbook activates on any of:
- AI-001: Prompt injection detector hit (high confidence, score >= 0.7)
- AI-002: Agent egress to non-allowlisted domain
- AI-003: Tool call budget exceeded in single session
- AI-006: Trifecta condition reached (data + untrusted_input + egress all active)

## Phase 1: Triage (0-15 minutes)

1. Identify session: `grep -h "session_id" evals/results/*/cases.jsonl | tail -20`
2. Check trifecta legs in session log — are all three active simultaneously?
3. Check outbox for unauthorized sends: `tail -50 agents/reference/outbox.jsonl`
4. Check web_fetch calls for non-allowlisted domains
5. Assign severity:
   - CRITICAL: confirmed exfiltration (outbox contains attacker addresses)
   - HIGH: full trifecta active, exfil unconfirmed
   - MEDIUM: single trifecta leg, detector hit only

## Phase 2: Contain (15-30 minutes)

1. Kill agent API key immediately: remove from environment, rotate in secrets manager
2. Block egress at network level if feasible
3. Preserve all evidence before any cleanup:
   ```bash
   cp -r agents/reference/outbox.jsonl /tmp/incident-$(date +%Y%m%d)/
   cp -r evals/results/ /tmp/incident-$(date +%Y%m%d)/
   ```
4. Notify affected users if PII may have been exfiltrated

## Phase 3: Eradicate

1. Identify injection source: which tool result contained the malicious payload?
2. If RAG poisoning: remove poisoned corpus doc and re-index
3. Patch tool allowlist to block the specific attack vector
4. Update detector rules if a new pattern was exploited

## Phase 4: Recover

1. Issue new API key
2. Run full eval suite to confirm fix: `python3 labs/day-11-monitoring-evals/eval.py`
3. Confirm ASR dropped on the relevant attack category
4. Update alert thresholds if detector generated excessive false positives

## Phase 5: Lessons Learned (within 72 hours)

Fill docs/incident-report-template.md. Required fields:
- Which threat ID from docs/threat-model.md was exploited?
- Which trifecta legs were active?
- What detection would have fired earlier?
- Residual risk after remediation
