# AI Agent Security Checklist

---

## Design

- [ ] **Threat model before building** — enumerate attack surfaces (direct injection, indirect injection, tool abuse, exfiltration) before writing a single line of agent code
- [ ] **Gate architecture on lethal trifecta** — if an agent has all three legs (data access + untrusted input + egress) simultaneously, redesign to remove at least one leg before proceeding
- [ ] **Assign trust labels to every data source** — classify each source as trusted, semi-trusted, or untrusted and document the label in the system prompt header
- [ ] **Specify which tool calls require human approval** — list high-risk actions (send_message, web_fetch to external URLs, file write) that must pause for HITL before execution
- [ ] **Require a measurable eval for every defense** — no defense ships without a corresponding test that produces a numeric result (ASR, TPR at fixed FPR, F1)
- [ ] **Define blast radius for each tool action** — document what data could be read and what external side effects could occur if a given tool call is misused
- [ ] **Scope capabilities per subgoal** — restrict which tools are available at each stage of a multi-step task; do not expose the full tool set for every step
- [ ] **Design egress allowlist before deployment** — enumerate permitted external domains and recipients at design time; default-deny everything else
- [ ] **Document the capability boundary** — write a one-sentence capability statement that also states what the agent cannot do; use it to drive refusal design

---

## Build

- [ ] **Validate tool call arguments against schema before execution** — reject malformed or out-of-schema arguments at the tool gateway layer, not inside the tool itself
- [ ] **Enforce per-tool argument allowlists** — maintain an explicit allowlist of permitted argument values (URLs, recipients, file paths) for every tool that makes external contact
- [ ] **Tag retrieved content as untrusted before passing to LLM** — prefix all content from web_fetch, corpus retrieval, and user-supplied files with `[UNTRUSTED_CONTENT]`
- [ ] **Emit a structured log event for every model_call, tool_call, tool_result, and detector_hit** — use a canonical schema so events can be parsed by a SIEM without preprocessing
- [ ] **Never trust tool result content unconditionally** — treat the payload of a tool result as data, not as instructions, regardless of which tool produced it
- [ ] **Enforce output schema on all tool calls** — validate that tool results conform to an expected structure; reject and flag malformed responses
- [ ] **Unit-test each tool in isolation** — write tests that call the tool directly with both valid and adversarial inputs before integrating it into the agent loop
- [ ] **Validate outbox recipients against allowlist** — send_message and equivalent tools must check the recipient against an allowlist before sending; fail closed on unknown recipients
- [ ] **Test detector at calibrated threshold** — evaluate the detector on a labeled dataset and select the threshold at the target FPR; do not rely on a default or uncalibrated cutoff
- [ ] **Run ruff and black before every commit** — enforce consistent formatting and catch obvious code errors in the pre-commit hook

---

## Deploy

- [ ] **Set max token and step budget per session** — configure a hard ceiling on tokens consumed and tool calls executed per session to limit runaway or hijacked agent behavior
- [ ] **Configure egress URL allowlist in the runtime environment** — enforce the design-time allowlist at the network or gateway layer, not only in prompt instructions
- [ ] **Disable unused tools entirely** — remove tools from the agent's tool registry if they are not required for the current deployment; do not rely on the model to decline to use them
- [ ] **Store API keys in a secrets manager** — do not store credentials in .env files in production; use a dedicated secrets manager with access logging
- [ ] **Set HITL checkpoints for high-risk tool categories** — configure the runtime to pause and request human approval before executing any tool flagged as high-risk at design time
- [ ] **Log model version and prompt hash with every session** — record the exact model identifier and a hash of the system prompt so incidents can be reproduced and attributed
- [ ] **Configure rate limiting per user and per session** — limit how many tool calls and external requests a single user or session can make within a time window

---

## Operate

- [ ] **Stream canonical log events to SIEM or SOAR in real time** — do not batch logs; injection attacks play out in seconds and require immediate visibility
- [ ] **Alert on trifecta condition in a single session** — fire an alert when data access, untrusted input, and egress activity all appear in the same session within a configurable window
- [ ] **Alert on first-seen send_message recipient** — any recipient not previously observed should trigger an alert and optionally a HITL hold before delivery
- [ ] **Alert on detector confidence drift over 24 hours** — track the rolling mean detector score; a significant shift suggests prompt distribution has changed or an attack campaign is underway
- [ ] **Maintain eval regression baseline and fail the build if ASR rises** — run the full attack eval suite on every CI build and block the merge if ASR on the protected agent exceeds the baseline
- [ ] **Rotate API keys on any compromise signal** — define what constitutes a compromise signal (unexpected egress, alert on trifecta, anomalous usage) and make key rotation the immediate first response
- [ ] **Maintain an agent containment playbook with a kill-switch procedure** — document the exact steps to disable the agent (revoke keys, block egress, halt session) and test the procedure before production launch
- [ ] **Preserve full tool call traces for forensic replay** — retain the complete sequence of model inputs, tool calls, and tool results for every session for a defined retention period
- [ ] **Run red-team eval on every major prompt change** — treat a prompt change as a code change; re-run the full attack suite and compare results against the prior baseline before deploying

---

## Retire

- [ ] **Revoke all API keys before decommission** — revoke keys at the secrets manager level; do not rely on the application being shut down to prevent key misuse
- [ ] **Purge agent corpus from the retrieval store** — delete or archive all documents from the vector store or retrieval index that were scoped to this agent
- [ ] **Audit the outbox for unauthorized sends before decommission** — review the full history of send_message and equivalent calls for any recipients or content that were not sanctioned
- [ ] **Document lessons learned using the incident report template** — complete the lessons-learned section of incident-report-template.md for any security events that occurred during the agent's lifetime
