# AI Security Alert Catalog

**Version:** 1.0
**Alert Count:** 15 (AI-001 through AI-015)

This catalog defines standardized alerts for AI agent security events. Each alert references fields from the canonical log schema (`log-schema.md`). Severity ratings follow the four-tier model: Critical, High, Medium, Low.

---

## AI-001: Prompt Injection Detector Hit (High Confidence)

**Signal:** `event_type = "detector_hit"` AND `detector_score >= 0.7`

**Severity:** High

**FP notes:**
- Legitimate security testing pipelines that intentionally submit injection patterns for red-team exercises.
- Security documentation or training material ingested into the RAG corpus that contains injection examples as educational content.
- Developers testing detector sensitivity by sending known injection strings.

**Suggested response:**
- Pull the full session log for the `session_id` and review all events before and after the detector hit to establish context.
- Check whether any `tool_call` events occurred after the `detector_hit` at the same or later step; if so, the injection may have influenced agent behavior.
- If `tool_calls` were made following the hit (especially `send_message` or `web_fetch`), escalate immediately to the agent containment playbook.

---

## AI-002: Agent Egress to Non-Allowlisted Domain

**Signal:** `event_type = "tool_call"` AND `tool_name = "web_fetch"` AND `tool_args_redacted.url` domain NOT IN configured egress allowlist

**Severity:** High

**FP notes:**
- A legitimate new vendor or data source that has not yet been added to the domain allowlist.
- API endpoints for recently approved third-party integrations that are awaiting allowlist update.
- Internal tooling that routes through an unexpected subdomain of an allowlisted parent domain.

**Suggested response:**
- Block or freeze the current session immediately to prevent the fetch from completing (if the gateway permits session suspension).
- Review the full URL and the session context to determine whether the destination is legitimate.
- If legitimate, add the domain to the allowlist through the change management process and resume the session; if not legitimate, escalate to the agent containment playbook.

---

## AI-003: Tool Call Budget Exceeded in Single Session

**Signal:** `COUNT(event_type = "tool_call" WHERE session_id = X)` > configured `max_budget` (default: 15)

**Severity:** Medium

**FP notes:**
- Genuinely complex multi-step research tasks that require more tool calls than the default budget.
- Batch processing agents designed to operate on large datasets with many sequential reads.
- Misconfigured budget threshold set too low for the agent's intended workload.

**Suggested response:**
- Retrieve the complete session log and review tool call distribution — check whether the same tool or the same argument is being called repeatedly (loop indicator).
- Examine the sequence of `model_call` and `tool_call` events to detect injection-driven iteration where an attacker is forcing the agent to loop.
- If the session is still active and no attack pattern is found, consider raising the budget limit for this `agent_id` through configuration.

---

## AI-004: Detector Confidence Drift Over 24 Hours

**Signal:** `MEAN(detector_score, 24h rolling window, agent_id = X)` > 1.5x `MEAN(detector_score, 7-day baseline, agent_id = X)`

**Severity:** Medium

**FP notes:**
- A new deployment or version of a security tool integrated with the agent that legitimately discusses injection patterns in its documentation.
- A burst of security-focused user queries (e.g., users asking the agent for cybersecurity information) that incidentally trigger the detector.
- A model update that changed how the model formats responses, causing more rule matches.

**Suggested response:**
- Review a sample of the most recent inputs and `detector_hit` events to determine whether the score increase reflects a genuine pattern change or benign content shift.
- Check deployment logs for system prompt changes (`prompt_hash` drift), model updates, or new tool integrations that coincide with the drift start time.
- If the review suggests a coordinated injection campaign, escalate to the incident response team and consider temporarily lowering the alert threshold for this `agent_id`.

---

## AI-005: Human Review Checkpoint Expired Without Decision

**Signal:** `event_type = "human_review_requested"` AND no corresponding resolution event within 30 minutes of `ts`

**Severity:** Medium

**FP notes:**
- Reviewer is unavailable due to off-hours operation, holiday, or PTO with no backup configured.
- Review queue notification failed to reach the reviewer (email/Slack delivery issue).
- The review was completed in a system that does not write back a resolution event to the log pipeline.

**Suggested response:**
- Auto-deny the pending action: close the checkpoint with a "denied by timeout" resolution so the agent session can fail safely rather than stall indefinitely.
- Notify the assigned reviewer and their backup via an escalation channel (paging if severity warrants it).
- Log the expired checkpoint for SLA review — repeated expirations indicate a capacity or notification reliability problem that requires process adjustment.

---

## AI-006: Trifecta Condition Reached (All Three Legs in One Session)

**Signal:** `trifecta_legs_active` contains all of `["data", "untrusted_input", "egress"]` within a single `session_id`

**Severity:** Critical

**FP notes:**
- A legitimate research agent that is explicitly granted broad permissions (data access + external web + messaging) for an approved use case — extremely rare and should require pre-authorization.
- An agent configuration that marks all sessions as having the "data" leg active even when the current session does not access sensitive data, due to overly broad capability labeling.

**Suggested response:**
- Immediately trigger a manual review of the session: pull all events and examine the sequence to determine whether an exfiltration chain is in progress.
- Check the agent's outbox for any `send_message` or `web_fetch` calls made after the third leg activated; if attacker-controlled addresses are present, initiate the exfiltration response playbook.
- Consider invoking the agent kill-switch to terminate the session and revoke the API key until the review is complete; document the decision and timeline.

---

## AI-007: RAG Retrieval Returned Document with Detector Hit

**Signal:** `event_type = "tool_result"` AND `tool_name = "read_doc"` AND inline detector scan of result content returns `detector_score > 0.5`

**Severity:** High

**FP notes:**
- Security training documents, incident post-mortems, or red-team reports stored in the RAG corpus that contain injection examples as legitimate content.
- Threat intelligence feeds ingested into the corpus that quote malicious payloads for educational purposes.
- Documents containing legacy security warnings or phishing examples from user-submitted content.

**Suggested response:**
- Quarantine the flagged document immediately: remove it from the active retrieval index so future sessions cannot retrieve it until it is reviewed.
- Search the corpus for documents with similar metadata (same author, same upload batch, same source URL) to identify related poisoned documents.
- Review the current session to determine whether the retrieved content influenced subsequent model calls and escalate if tool calls followed the retrieval.

---

## AI-008: Outbox Send_message to First-Seen Recipient

**Signal:** `event_type = "tool_call"` AND `tool_name = "send_message"` AND `tool_args_redacted.recipient` NOT IN historical recipient list for `agent_id`

**Severity:** High

**FP notes:**
- A legitimate new contact: the agent is being used to draft an initial outreach message to a new client or partner for the first time.
- A user explicitly asking the agent to compose and send a message to a new address as part of an approved workflow.
- First run of a newly deployed agent where the historical recipient list is empty.

**Suggested response:**
- Hold the outgoing message pending human approval: do not deliver until a reviewer confirms the recipient and message body are legitimate.
- Review the full session context to determine whether the recipient address appeared in any retrieved documents or web fetched content — if so, this is a strong indicator of injection-driven exfiltration.
- If the recipient and content are confirmed legitimate by a reviewer, deliver the message and add the recipient to the approved historical list.

---

## AI-009: Agent Step Count Exceeded Threshold

**Signal:** `MAX(step WHERE session_id = X)` > 8 (configurable per `agent_id`)

**Severity:** Medium

**FP notes:**
- A complex legitimate multi-step task (e.g., multi-document research with synthesis) that genuinely requires more than 8 tool interactions.
- An agent configuration where the default step threshold is set too conservatively for the designed workload.
- A long-running batch job that is expected to iterate many times.

**Suggested response:**
- Review the session's tool call sequence and look for repeated calls to the same tool with the same or incrementally modified arguments — this pattern is a strong indicator of injection-driven looping.
- Check whether the agent's `model_call` events show consistent reasoning progression or whether the model appears to be re-asking the same question (which suggests the injected instruction is disrupting the agent's memory or goal tracking).
- If attack patterns are absent, evaluate whether the step threshold should be raised for this `agent_id` and update configuration through the change management process.

---

## AI-010: Markdown Image with External URL in Agent Output

**Signal:** `event_type = "final_response"` AND `metadata.output_filter_violations` contains `"blocked_image_url"`

**Severity:** High

**FP notes:**
- Legitimate use of external images where the source domain is not yet in the output filter's allowlist (e.g., a documentation agent referencing official product screenshots from a known vendor CDN).
- An agent responding to a user question about image hosting that includes an example URL in its answer.
- Images from allowlisted domains that are incorrectly flagged due to a subdomain mismatch in the allowlist configuration.

**Suggested response:**
- Review the full `final_response` content and extract all external URLs present in the output — check whether any URL contains query parameters that encode session data, user data, or retrieved document content (data exfiltration via URL).
- Confirm that the OutputFilter successfully blocked the image from rendering in the user-facing interface; if the filter did not fire correctly, this is a gap that requires an immediate patch.
- If the URL is confirmed legitimate, add the domain to the output filter's image allowlist through the standard change management process.

---

## AI-011: Repeated Detector Hits for Same User ID

**Signal:** `COUNT(event_type = "detector_hit" WHERE user_id = X, 1h rolling window)` > 3

**Severity:** High

**FP notes:**
- Security researchers or red-team members who are authorized to submit injection patterns as part of their work.
- Ongoing red-team exercises where multiple injection attempts per hour are expected and pre-authorized.
- A user submitting security-related queries (e.g., asking about prompt injection defense) where the query content itself triggers the detector.

**Suggested response:**
- Temporarily rate-limit the `user_id` to reduce the attack surface while the review is in progress: reduce their allowed session rate or require additional authentication for new sessions.
- Escalate to the security team for a manual review of the user's recent session history across all agents, looking for successful injections (tool calls following detector hits).
- Check whether the user's account credentials may have been compromised and are being used by an external attacker to launch repeated injection attempts.

---

## AI-012: Model Adapter Fallback Fired (Primary Degraded)

**Signal:** `metadata.adapter_fallback = true`

**Severity:** Low

**FP notes:**
- Expected behavior during a primary LLM provider outage or maintenance window — the fallback is working as designed.
- Transient network issues causing the primary adapter to time out on a subset of requests.
- A planned canary deployment that intentionally routes a fraction of traffic to the backup model.

**Suggested response:**
- Log the fallback event for SLA tracking: note the start time and duration to inform the provider SLA review cycle.
- Verify that the backup model is operating with the same system prompt, capability restrictions, and security posture as the primary — a backup model with different safety tuning could introduce unexpected behavior.
- Monitor for elevated `detector_score` values during the fallback period, as a different model may respond differently to the same inputs.

---

## AI-013: Tool Gateway Policy Violation

**Signal:** `event_type = "policy_violation"` AND `metadata.gateway_blocked = true`

**Severity:** Medium

**FP notes:**
- The agent attempting a legitimate action that exceeds its currently configured scope — for example, a research agent trying to access a data store it has been approved for in a different environment but not yet in production.
- An overly restrictive gateway policy that blocks routine operations, causing the agent to fail on normal tasks.
- A timing issue where the agent's capability token has expired mid-session.

**Suggested response:**
- Review the blocked action in the context of the full session to determine whether it was agent-initiated (normal reasoning) or injection-driven (the agent was manipulated into attempting the blocked action).
- Examine the gateway policy rule that fired to determine whether it is correctly configured for this `agent_id` — if the rule is overly broad, schedule a policy review.
- If the block appears injection-driven, escalate to the prompt injection triage playbook.

---

## AI-014: Capability Token Reuse Outside Intended Scope

**Signal:** `event_type = "tool_call"` AND `metadata.capability_token` does not match the expected token for the current `step` and `agent_id` combination

**Severity:** High

**FP notes:**
- The agent legitimately replanning mid-task: a reasoning step causes the agent to change its approach, leading it to reuse a token issued for an earlier planned step in a new context.
- A bug in the token issuance logic that assigns the wrong expected token to certain steps.
- A stateless token implementation that does not enforce step binding.

**Suggested response:**
- Terminate the current session immediately to prevent further tool calls with the mismatched token — a token scoped to one operation should not be usable in another context.
- Review the token issuance logic for the affected `agent_id` to determine whether the mismatch is a logic bug or evidence of token theft/replay by an attacker.
- Audit recent sessions for the same `agent_id` to check whether similar token mismatches occurred previously without being detected.

---

## AI-015: Multiple Sessions Hitting Same Poisoned URL or Document

**Signal:** `COUNT(DISTINCT session_id WHERE tool_result content matches injection pattern, 1h rolling window)` > 2

**Severity:** Critical

**FP notes:**
- A popular legitimate URL or widely-used document that coincidentally contains text that pattern-matches injection signatures (e.g., a security blog post about prompt injection that is referenced in many research tasks).
- A shared RAG document that is retrieved frequently and contains flagged text that is actually legitimate security documentation.
- A high-volume agent deployment where many sessions naturally access the same resources.

**Suggested response:**
- Block the URL or quarantine the document immediately across all agents: update the URL blocklist and/or remove the document from the retrieval index to prevent additional sessions from being exposed.
- Retrieve the full session logs for all affected sessions and triage each one: determine which sessions made tool calls after retrieving the poisoned content, and escalate those to the agent containment playbook.
- Check for coordinated campaign indicators: examine whether affected `user_id` values share any pattern, whether the poisoned source appeared recently in the corpus, and whether other similar URLs or documents exist in accessible data sources.
