# Glossary

Terms used throughout this repository, defined precisely for practitioners. Each definition is self-contained; cross-references point to related entries.

---

### Prompt Injection (direct vs indirect)
Prompt injection is an attack in which an adversary embeds instructions in content that is processed by an LLM, causing the model to deviate from its intended behavior. *Direct prompt injection* occurs when the attacker controls the user-facing input channel — the chat message or API request — and inserts adversarial instructions alongside or in place of a legitimate user query; it requires the attacker to have direct access to the input interface. *Indirect prompt injection* occurs when the adversarial instructions are embedded in content the agent retrieves from an external source — a web page, a document, a database record, a tool result — rather than the direct input channel; the user submitting the original query is typically a victim, not the attacker. Indirect injection is the higher-priority enterprise risk because its attack surface is every piece of text the agent reads, not only the chat box.

---

### Indirect Prompt Injection (IPI)
Indirect prompt injection (IPI) is the specific variant of prompt injection in which a malicious payload is embedded in data returned to the agent through a tool call or retrieval step, rather than supplied directly by the user. The agent fetches the content as part of normal operation — retrieving a URL, reading a corpus document, reading email, querying a database — and the LLM then processes the payload alongside legitimate data, treating adversarial instructions as if they were legitimate context. IPI is structurally difficult to prevent because the agent must read untrusted content to function; the solution requires sanitization of tool results, output monitoring, and tool call gating rather than input filtering alone. See also: Lethal Trifecta, RAG.

---

### Lethal Trifecta
The lethal trifecta (coined by Simon Willison, 2023) describes the structural condition under which indirect prompt injection becomes a full data-exfiltration primitive. The three legs are: (1) the agent has access to private or sensitive *data*, (2) the agent is exposed to *untrusted input* that an adversary can influence, and (3) the agent has an *egress* capability — a tool or channel through which data can leave the system (email, webhook, API call, rendered URL). When all three legs are simultaneously present and uncontrolled, a single injected payload can cause the agent to read private data and send it to an attacker-controlled destination using its own authorized capabilities. Threat modeling for agentic systems should begin by checking for the trifecta before any other analysis; if all three legs are present without controls at each, the system has a structural exfiltration vulnerability regardless of other defenses.

---

### OWASP LLM Top 10
The OWASP Top 10 for Large Language Model Applications is a community-maintained list of the ten most critical security risks in LLM-based systems, published by the OWASP Foundation. The 2025 edition covers: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, and LLM10 Unbounded Consumption. The list provides a shared vocabulary for risk communication and a baseline control mapping; it is not exhaustive and does not replace system-specific threat modeling, but it provides the standard reference taxonomy used throughout this repository.

---

### OWASP Agentic Top 10
The OWASP Agentic Security Top 10 is a 2025 OWASP working group publication covering security risks specific to agentic AI systems — systems in which LLMs autonomously plan and execute multi-step tasks using tools, memory, and external integrations. It extends the LLM Top 10 with agent-specific concerns not adequately covered by the chatbot-oriented LLM list. The 2025 edition covers: AAA-01 Prompt Injection and Jailbreaking, AAA-02 Overly Permissive Agent Scopes, AAA-03 Data and Tool Misuse, AAA-04 Insecure Tool Implementations, AAA-05 Data Exfiltration and Privacy Violations, AAA-06 Trust Boundary Violations, AAA-07 Over-reliance on Agent Decisions, AAA-08 Inadequate Monitoring and Logging, AAA-09 Insufficient Context Management, and AAA-10 Supply Chain Vulnerabilities. Threat entries in this repository are mapped to both taxonomies.

---

### MITRE ATLAS
MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) is a MITRE Corporation knowledge base of adversarial tactics, techniques, and procedures (TTPs) targeting AI and machine learning systems, structured analogously to MITRE ATT&CK. ATLAS covers attack techniques at the model level (training data poisoning, model inversion, evasion), at the inference level (prompt injection, LLM jailbreak, adversarial inputs), and at the supply chain level (ML supply chain compromise). It provides a standardized vocabulary for AI-specific attack techniques that complements OWASP's risk-oriented framing; where OWASP identifies what risks exist, ATLAS identifies how attackers execute them. This repository uses ATLAS technique references alongside OWASP mappings for complete threat characterization.

---

### Attack Success Rate (ASR)
Attack success rate (ASR) is the fraction of attack attempts in a defined dataset that result in the agent performing the attacker-intended action — executing an unauthorized tool call, exfiltrating data, deviating from its mandate, or producing attacker-specified output. ASR is measured by running a labeled attack dataset against the agent under test, evaluating each outcome against a programmatic success criterion, and dividing successful attacks by total attempts. ASR is always reported with a confidence interval (typically 95% bootstrap CI) and at a specified defense configuration; "ASR before defenses" and "ASR after defenses" are the two primary comparison points. A defended ASR that overlaps the baseline CI provides no statistical evidence of improvement. ASR is the primary metric used in this repository's eval harness.

---

### True Positive Rate (TPR) / False Positive Rate (FPR)
True positive rate (TPR, also called recall or sensitivity) is the fraction of actual attacks that the detector correctly identifies as attacks: TPR = TP / (TP + FN). False positive rate (FPR) is the fraction of legitimate (benign) inputs that the detector incorrectly flags as attacks: FPR = FP / (FP + TN). Both metrics must be reported together; a detector's TPR is only meaningful at a stated FPR, because any detector can achieve 100% TPR by flagging everything (which produces 100% FPR). In production, FPR against real enterprise traffic is the binding constraint — a detector with 5% FPR blocks one in twenty legitimate requests. Calibrated eval means measuring TPR at a chosen operating FPR (e.g., "TPR of 0.87 at FPR 0.05") on a labeled dataset representative of production traffic distributions.

---

### MCP (Model Context Protocol)
Model Context Protocol (MCP) is an open protocol developed by Anthropic that standardizes how LLM applications expose and consume tools, resources, and prompts from external servers. An MCP server is a process that declares a set of tools (functions the LLM can call), resources (data sources the LLM can read), and prompt templates; an MCP client (the agent or application) discovers and invokes these at runtime. MCP enables modular, composable tool ecosystems but introduces a supply chain attack surface: a malicious or compromised MCP server can inject adversarial instructions into tool descriptions, tool results, or resource content that the LLM will process. Real-world attacks documented in CVE-2025-59944 (Cursor), CVE-2025-68143/44/45 (Anthropic Git MCP), and the Invariant Labs GitHub MCP report all exploit this surface.

---

### RAG (Retrieval-Augmented Generation)
Retrieval-Augmented Generation (RAG) is a pattern in which an LLM is augmented with a retrieval step that fetches relevant documents from an external corpus and includes them in the model's context window before generation. The retrieval step typically uses dense vector search (embedding the query and documents, then ranking by cosine similarity) against a vector database. RAG allows agents to answer questions about large document collections without fine-tuning, but it introduces a security surface: the retrieved documents are semi-trusted content that enters the model's reasoning context. A poisoned corpus document retrieved by RAG is an indirect prompt injection vector; a high-cosine-similarity adversarial document can reliably be retrieved for targeted queries, making RAG corpus integrity a first-class security concern. See also: IPI, Lethal Trifecta.

---

### Confused Deputy
The confused deputy problem (coined by Norm Hardy, 1988) describes a vulnerability in which a program with legitimate authority (the deputy) is manipulated into using that authority on behalf of an unauthorized party. In the context of LLM agents, the agent is the confused deputy: it holds operator-granted tool-calling capabilities (the authority), and an attacker who successfully injects instructions causes the agent to exercise those capabilities on behalf of the attacker's intent rather than the user's intent. The agent is not compromised at the code level — it is functioning as designed — but its authority is redirected. Confused deputy attacks are the structural reason that tool scope minimization (least privilege) is a primary agentic security control: an agent with fewer capabilities has less authority to redirect.

---

### Trust Boundary
A trust boundary is a line in a system architecture across which the trust level of data or components changes. Data originating inside a trust boundary is assumed to be under the operator's control; data crossing inbound from outside a trust boundary must be treated as potentially adversarial regardless of whether it appears legitimate. In the reference agent, three trust boundaries are relevant: (1) the inbound boundary at user input — between the authenticated user and the agent context; (2) the inbound boundary at tool results — between external sources (`web_fetch`, corpus, external APIs) and the agent context; and (3) the outbound boundary at `send_message` — between the agent context and external recipients. Controls must be applied at each trust boundary crossing; data that crosses an inbound boundary from a less-trusted zone must be sanitized or monitored before being acted upon.

---

### Capability Token
A capability token is a cryptographic or logical credential that grants its holder the right to invoke a specific tool or action within a bounded scope — for a specific session, a specific resource, and with specific parameter constraints. Rather than granting an agent blanket tool access at startup, a capability-token model issues scoped tokens at call time (e.g., "this session may call `send_message` with recipient `support@example.com` up to 3 times"). Tokens can be revoked, audited, and scoped to minimize blast radius if the agent is compromised. Capability tokens are the formal security mechanism underlying the tool gateway's allowlist enforcement; in practice, the tool gateway acts as a token-checking intermediary between the LLM and the tool execution layer.

---

### Tool Gateway
A tool gateway is the policy enforcement layer that sits between an agent's LLM reasoning component and its tool execution layer, intercepting every tool call before it is executed. The gateway validates: the tool name against an allowlist of permitted tools for the current session; each parameter value against type constraints, length limits, pattern allowlists, and blocklists; the call count against a per-tool and per-session budget; and any network destinations against an egress allowlist. The gateway is the primary control point for tool abuse, SSRF, unauthorized egress, and budget exhaustion attacks. It should be implemented as a separate, auditable component with its own test suite — not inline validation inside the tool implementation — so that defenses cannot be bypassed by calling the tool function directly.

---

### Human-in-the-Loop (HITL)
Human-in-the-loop (HITL) is a design pattern in which certain agent actions are paused and routed to a human reviewer before execution, rather than being executed autonomously. HITL is the fallback control for attack scenarios where automated detectors and tool gating are insufficient — specifically, for high-consequence actions (sending messages to large recipient lists, deleting data, making financial transactions) and for edge cases where the detector's confidence is below a threshold. In agentic security, HITL gates are applied selectively: requiring human approval for every tool call eliminates the value of automation, while applying no HITL leaves high-consequence actions fully autonomous. The design decision is: which tool calls, at which confidence thresholds, require human confirmation? This repository implements HITL via a `human_review_requested` log event and a configurable approval gate in the tool gateway.

---

### Bootstrap Confidence Interval
A bootstrap confidence interval is a non-parametric estimate of the uncertainty around a measured statistic (such as ASR, TPR, or FPR) computed by repeatedly resampling the evaluation dataset with replacement and recalculating the statistic on each resample. Because prompt injection eval datasets are typically small (tens to low hundreds of examples), standard normal-approximation confidence intervals may be unreliable; bootstrap CIs make no assumption about the underlying distribution and are valid for small samples. The standard procedure: resample the dataset N times (N ≥ 10,000), compute the statistic on each resample, and take the 2.5th and 97.5th percentiles as the 95% CI bounds. A result such as "ASR = 0.82 (95% CI: 0.71–0.91)" means the true ASR is estimated to fall between 0.71 and 0.91 with 95% confidence under the resampling model. This repository's eval harness computes bootstrap CIs for all reported metrics.

---

### Trifecta Tagging
Trifecta tagging is the practice of annotating each threat entry in a threat model with which of the three lethal trifecta legs it activates — `data` (access to private information), `untrusted_input` (exposure to adversary-controlled content), and `egress` (ability to send data outside the system) — so that the coverage of controls across trifecta legs can be audited at a glance. A threat tagged with all three legs is a full-trifecta threat and requires controls at each leg independently; blocking any single leg breaks the exfiltration chain. Trifecta tagging is applied in the threat table in `docs/threat-model.md` and is the basis for the trifecta matrix. The practice makes it easy to identify which defenses address which structural risks and to detect gaps where a trifecta leg is uncontrolled.
