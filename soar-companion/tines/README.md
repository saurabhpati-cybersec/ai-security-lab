# Tines SOAR Companion

## What Tines Is

Tines is a no-code SOAR platform widely deployed in security operations teams. Workflows ("stories") connect webhooks, HTTP actions, and integrations without requiring custom code. It is relevant for AI agent IR because security teams can operationalize AI-specific alerts using the same tooling they already run for phishing and malware response.

## Mapping: Canonical Schema → Tines Primitives

| Canonical Concept | Tines Primitive | Notes |
|---|---|---|
| `LogEvent` (any type) | `WebhookAgent` payload | Each event type maps to a field in `body.event_type` |
| Alert condition | `TriggerAgent` rules | Field comparisons on `detector_score`, `event_type`, `trifecta_legs_active` |
| Playbook step | `HTTPRequestAgent` or `SendToStoryAgent` | Enrichment, blocking, ticketing |
| Playbook branch | Second `TriggerAgent` downstream | Separate paths for critical vs. high severity |
| Full playbook | Tines story (linked agents) | `links` array defines execution order |

## Stories in This Directory

| File | Alert | Trigger Condition |
|---|---|---|
| `prompt_injection_triage.json` | AI-001 | `detector_score >= 0.7` and `event_type=detector_hit` |
| `agent_containment.json` | AI-006 or analyst escalation | Trifecta count >= 3 or manual override |
| `exfiltration_response.json` | AI-002 / AI-010 | Egress event not already blocked by OutputFilter |

## Testing with webhook-examples/

1. Import the story JSON into your Tines tenant via **Stories → Import**.
2. Copy the webhook URL from the `WebhookAgent` configuration panel.
3. POST an example payload:

```bash
curl -X POST <your-webhook-url> \
  -H "Content-Type: application/json" \
  -d @webhook-examples/ai_detector_hit.json
```

4. Use `ai_benign.json` to confirm the trigger filter blocks low-signal events.

## Limitations

These are reference implementations. They will not run without:

- A Tines account with the story imported
- Credentials configured: `AI_WEBHOOK_SECRET`, `AGENT_LOG_API_BASE_URL`, `AGENT_LOG_API_KEY`, `JIRA_BASE_URL`, `JIRA_API_TOKEN`, `AGENT_MGMT_API`, `MGMT_API_KEY`
- A working "Security Slack Approval" story in the same team (used by `SendToStoryAgent`)

## Adapting to Your Environment

- **Slack**: Replace `SendToStoryAgent` story reference with a direct Slack `HTTPRequestAgent` posting to your workspace's incoming webhook URL.
- **Ticketing**: Swap the Jira `HTTPRequestAgent` URL and payload structure for ServiceNow, Linear, or your ITSM. Update the credential names accordingly.
- **Egress proxy**: Replace `EGRESS_PROXY_API` in `exfiltration_response.json` with your proxy vendor's block endpoint (Zscaler, Palo Alto, Squid).
