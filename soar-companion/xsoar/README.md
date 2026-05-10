# Cortex XSOAR 8.x SOAR Companion

## Why AI Agent Telemetry Needs New Playbooks

Cortex XSOAR 8.x ships with hundreds of community playbooks covering phishing,
malware, and cloud-misconfiguration incidents. None of them model the primitives
that make AI agent incidents distinct: multi-step reasoning loops, LLM tool
calls, detector scores from a classifier pipeline, and the prompt-injection
trifecta (sensitive data + untrusted input + egress path). Existing playbooks
also lack incident fields for session context, making it impossible to group
events across the dozens of LogEvents a single compromised session may generate.
The playbooks and integrations in this directory fill that gap.

## Mapping: Canonical Schema → XSOAR Primitives

| Canonical Concept | XSOAR Primitive | Notes |
|---|---|---|
| `LogEvent` (any type) | Custom incident type **AI Agent Incident** | One incident per alert signal, enriched with session context |
| Alert signal (AI-001, AI-002 …) | Trigger condition in playbook task (condition type) | Field comparisons on `aisecuritydetectorscore`, `aisecuritytrifectafull` |
| Playbook step | XSOAR task (action or condition) | `iscommand: true` tasks call integration commands; condition tasks branch flow |
| Severity routing | Condition task with multiple labels | Critical / High / Default branches map to Jira P1, Slack notify, or auto-close |
| Kill switch | `AIAgentKillSwitch.agentkillswitch-revoke` command | Audit-logged API key revocation |

## Importing Into XSOAR

1. **Upload playbook YAML** — Go to *Playbooks → New Playbook → Import*. Upload
   each `.yml` from `playbooks/`. The `fromversion` field requires XSOAR 8.0.0+.
2. **Install custom integrations** — Go to *Settings → Integrations → Upload*.
   Upload each `.yml` from `integrations/`. Configure `base_url` and `api_key`
   for your environment.
3. **Create incident type and fields** — Go to *Settings → Object Setup →
   Incident Types*. Import `incident-fields/ai_agent_incident.yml`. The custom
   `aisecurity*` fields are created as part of this import and become available
   on all **AI Agent Incident** incidents.

## Limitations

These are reference YAML playbooks; they will not execute without a real XSOAR
environment. Specifically:

- Integration commands (`AIAgentLogIntegration`, `AIAgentKillSwitch`,
  `Jira V2`, `SlackV3`) are stubs — credentials and endpoint URLs must be
  configured in your XSOAR instance.
- The `script: ''` field in integration YAMLs is intentional; the Python
  backend must be implemented or replaced with an existing XSOAR integration.
- Condition labels must exactly match the `nexttasks` keys; validate in the
  XSOAR playbook editor after import.

## Parallel with Tines

The three playbooks here are direct parallels to the Tines stories in
`soar-companion/tines/stories/`. The logic and branching are identical; the
syntax and execution model differ. Tines uses linked JSON agents with
`TriggerAgent` for branching; XSOAR uses typed YAML tasks with `condition`
tasks and `nexttasks` maps. Tines stories are event-driven (webhook push); XSOAR
playbooks are incident-driven (pulled from the incident queue). Both platforms
can run the same response logic — choose based on what your SOC already operates.
