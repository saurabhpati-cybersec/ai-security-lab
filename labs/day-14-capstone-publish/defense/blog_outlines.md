# Blog Post Outlines

## Post 1: "The Lethal Trifecta: Why Your LLM Agent Is a Data Breach Waiting to Happen"

**Audience:** Security engineers evaluating LLM agents for production
**Angle:** Technical, alarming-but-actionable
**Target length:** 1,800-2,200 words
**Target publication:** tl;dr sec newsletter, Daniel Miessler's Unsupervised Learning, or personal blog

**Outline:**

- **Hook:** "The GitHub MCP vulnerability in May 2025 exfiltrated repository secrets via a README. The attacker didn't need access to the repo. They needed one crafted commit message and a developer who ran the MCP server."
- **Define the trifecta:** Three structural properties that create structural risk:
  - Leg A: data access (read_doc, corpus, memory)
  - Leg B: untrusted input (user messages, web content, email, tool results)
  - Leg C: egress (send_message, web_fetch, API calls)
  - All three together: data breach via a single injected instruction
- **Show a concrete attack:** 5-line Python demo — vulnerable agent, one injection, send_message fires
- **Map to OWASP LLM01 + Agentic AAA-01:** not just theoretical, standardized threat classes
- **Show the eval numbers:** ASR 65% → 18% with layered defenses, measured with bootstrap CIs
- **The measurement lesson:** defense without measurement is theater; here's the eval harness
- **CTA:** link to repo, day-12 capstone eval, learning-tracker template

---

## Post 2: "Building a Prompt Injection Detector: TPR, FPR, and Why 'It Feels Right' Isn't a Threshold"

**Audience:** Detection engineers, ML engineers building LLM-integrated products
**Angle:** How-to with real code and calibration methodology
**Target length:** 2,500-3,000 words
**Target publication:** Security Boulevard, Dark Reading, or personal blog

**Outline:**

- **Hook:** "You added a prompt injection detector. It blocks 'ignore previous instructions' variants. It feels comprehensive. Here's what you missed — and how to know you missed it."
- **Why thresholds matter:** FPR cost in production (one-in-five legitimate requests blocked = product failure)
- **Rule-based detector walkthrough:**
  - The 17-rule weight system in `detectors/rules.py`
  - Confidence scoring: sum-of-weights with sigmoid squashing
  - Latency: <5ms, no API calls
  - TPR on direct_injection.jsonl: ~80%; FPR on benign.jsonl: ~3%
- **LLM-as-judge second pass:**
  - Higher TPR on indirect injection and novel phrasing
  - Latency cost: 300-800ms per call
  - When to use it: ambiguous inputs that score 0.4-0.6 on rule detector
- **Calibration methodology:**
  - Threshold sweep: plot TPR vs FPR at each threshold value
  - Pick the threshold that meets your production SLA (e.g., FPR ≤ 5%)
  - Why point estimates lie: bootstrap CIs on 32-case dataset are wide
- **The dataset matters:** what's in direct_injection.jsonl and why each category is different
- **Code walkthrough:** `detectors/rules.py` annotated, eval harness output interpreted
- **CTA:** link to repo, Day 8 detection engineering lab

---

## Post 3: "Indirect Prompt Injection: Five Real Incidents and What They Have in Common"

**Audience:** Security leaders, architects, product managers considering LLM agent deployment
**Angle:** Incident analysis — pattern recognition across real events
**Target length:** 2,000-2,500 words
**Target publication:** SANS Reading Room, InfoSecurity Magazine, or personal blog

**Outline:**

- **Hook:** "You did not give the attacker a login. You gave your AI agent a browser. The attacker gave your agent content. That was enough."
- **Incident 1: GitHub MCP (May 2025):**
  - Vector: repository README content processed by MCP server
  - Impact: arbitrary tool call execution in developer's context
  - Root cause: no trust boundary between MCP tool results and agent instructions
- **Incident 2: EchoLeak (CVE-2025-32711):**
  - Vector: email body content injected into Copilot context
  - Impact: calendar events and email content leaked to attacker-controlled endpoint
  - Root cause: Copilot processed email content without IPI tagging
- **Incident 3: CVE-2025-59944 (Cursor):**
  - Vector: MCP tool description field containing injection
  - Impact: Cursor IDE followed attacker instructions embedded in tool metadata
  - Root cause: tool descriptions treated as trusted system content, not untrusted tool data
- **Incident 4-5: CVE-2025-68143/4/5 (Anthropic Git MCP):**
  - Vector: git commit messages and branch names
  - Impact: developer's Git MCP session hijacked via repository interaction
  - Root cause: structured data fields (commits) not sandboxed from instruction space
- **Common thread across all five:**
  - Untrusted content (email, README, tool result, commit message) reaches the model without trust boundary
  - No IPI tagging, no content-aware output filter
  - Agent's egress capability becomes the exfiltration primitive
- **Controls that would have prevented each:**
  - Trust tagging on tool results
  - ToolGateway allowlisting
  - Output filter for URL/webhook patterns in responses
- **CTA:** link to repo, Day 4 (indirect injection lab), Day 12 (capstone build)

---

## Post 4: "AI Agent Incident Response in Your SOAR: A Practical Guide for SOC Teams"

**Audience:** SOC engineers, detection engineers, SOAR engineers
**Angle:** Practical operations — platform-specific, actionable today
**Target length:** 2,500-3,000 words
**Target publication:** Anton Chuvakin's SIEM blog, SANS Blue Team, or personal blog

**Outline:**

- **Hook:** "Your SIEM has rules for SQL injection, XSS, and lateral movement. It has zero rules for 'LLM agent called send_message with an attacker-controlled recipient.' That gap is growing every month."
- **Why existing SIEM rules miss AI agent attacks:**
  - Agent tool calls look like normal API requests
  - Injection happens inside model context, not on the wire
  - Attribution is hard: was send_message a legitimate request or an injection-driven call?
- **The canonical event schema:**
  - `model_call`: token counts, latency, model ID, prompt hash
  - `tool_call`: tool name, arguments, result summary, caller context
  - `detector_hit`: rule matched, confidence, input hash
  - `policy_violation`: action blocked, reason, event chain ID
  - Why these four fields are sufficient to triage most AI agent incidents
- **Tines story walkthrough:**
  - Trigger: `policy_violation` event via webhook
  - Step 1: enrich with threat intel (is the destination domain known-malicious?)
  - Step 2: page on-call if confidence >0.8 and tool=send_message
  - Step 3: kill-switch: disable agent for affected tenant
  - Full story JSON in `soar-companion/tines/`
- **XSOAR playbook parallel:**
  - Same logic, different platform
  - Incident type: "AI Agent Prompt Injection"
  - Playbook tasks: alert, enrich, contain, remediate, post-incident review
  - YAML in `soar-companion/xsoar/`
- **5 alerts every AI-enabled org should have right now:**
  1. Agent called egress tool (send_message/web_fetch) with unrecognized domain
  2. Detector confidence >0.7 but tool call still executed (threshold bypass)
  3. Agent processed >3 tool results in a single turn (chaining indicator)
  4. Output filter blocked a response (potential successful injection, blocked at last layer)
  5. Agent corpus read followed immediately by egress tool call (exfiltration pattern)
- **CTA:** link to repo, soar-companion/ directory, Day 11 (monitoring/evals lab)
