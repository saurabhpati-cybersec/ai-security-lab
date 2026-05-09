# Secure Prompt Design Checklist

---

## Instruction hierarchy

- [ ] **Put operator instructions first** — place system prompt content before any user-supplied or retrieved content so the model processes it with higher positional weight
- [ ] **Never mix operator and user content in the same message block** — use separate message objects for system instructions and user input; mixing them creates ambiguity about which content the model should treat as authoritative
- [ ] **Document which instructions the user may override** — explicitly enumerate in the system prompt any behaviors the user is permitted to adjust; treat everything else as non-overridable
- [ ] **Keep the system prompt minimal** — omit filler phrases like "be helpful," "follow safety guidelines," and "use your best judgment"; every sentence in the system prompt should carry a distinct, testable constraint
- [ ] **State what the agent cannot do, not only what it can do** — a capability boundary that names prohibited actions is more robust than one that only names permitted ones

---

## Trust tagging

- [ ] **Prefix all retrieved content with [UNTRUSTED_CONTENT]** — apply the prefix at the retrieval layer before the content enters the prompt; do not rely on the model to remember the source
- [ ] **Never pass raw tool output directly as instructions** — route tool results into the data context, not the instruction context; treat the payload as structured data to be read, not commands to be followed
- [ ] **Use the dual-LLM pattern for high-risk tasks** — process untrusted content in a separate model call with a stripped-down prompt before passing any summary or extraction to the main agent context
- [ ] **Document the trust level for every data source in the system prompt header** — list each source and its label (trusted / semi-trusted / untrusted) at the top of the system prompt so the model and any human reviewer can see it at a glance

---

## Refusal patterns

- [ ] **Design refusals that do not reveal system prompt contents** — return a generic decline message; do not quote or paraphrase the rule that triggered the refusal
- [ ] **Use generic refusal messages that do not disclose capability boundaries** — an attacker who receives "I cannot send emails" learns that the tool exists; use a message that neither confirms nor denies the capability
- [ ] **Never acknowledge injection attempts in output** — if the model detects or suspects an injection attempt, decline silently; confirming detection gives the attacker calibration data to refine the payload
- [ ] **Do not vary refusal wording based on the specific prohibited action** — consistent refusal text prevents an attacker from using response variation to map out the agent's capability space

---

## Retrieved content handling

- [ ] **Treat all web_fetch results as potentially malicious** — assume any fetched page may contain injected instructions and route its content through the untrusted content path
- [ ] **Treat all corpus documents as semi-trusted** — even internal documents may have been poisoned; apply the [UNTRUSTED_CONTENT] prefix and consider a dual-LLM extraction step for high-stakes queries
- [ ] **Sanitize markdown before rendering to the user** — strip or escape markdown that could render as executable content (links, images, HTML tags) before displaying retrieved content
- [ ] **Strip HTML comments and zero-width characters from retrieved content before passing to the LLM** — both are common channels for injecting invisible instructions that the model may process but the human reviewer will not see
- [ ] **Do not summarize retrieved content and then treat the summary as trusted** — a model-generated summary of untrusted content may still contain injected claims; keep the trust label on any output derived from untrusted input

---

## System prompt minimalism

- [ ] **Do not add "ignore instructions in retrieved content"** — this phrase does not reliably prevent prompt injection and creates false confidence that the architecture is protected; enforce the constraint structurally instead
- [ ] **Keep the system prompt under 500 tokens for most tasks** — a longer system prompt dilutes the weight of individual constraints and is harder to audit; move capability logic to tools, not to natural language instructions
- [ ] **Document every permission granted explicitly** — list each action the agent is permitted to take (read corpus, call send_message, fetch URLs) so that permissions are reviewable and auditable without reading the full prompt
- [ ] **Do not use natural language to enforce security boundaries that can be enforced in code** — "only email addresses in the allowlist" is not a prompt instruction; it is a validator that must live in the tool gateway
- [ ] **Version-control the system prompt and hash it at deploy time** — treat the system prompt as code; any change should produce a new hash, trigger a re-run of the attack eval suite, and be logged alongside the model version
