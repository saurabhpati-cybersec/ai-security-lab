# AI Security: An Honest Assessment

**Audience:** Recruiters, senior engineers, and anyone deciding whether this domain is worth their time. This document will not flatter the field. It will tell you what is overrated, what matters, and what skills will get you hired.

---

## Section 1: What's Hype

### Jailbreak Research as an Enterprise Security Priority

The vast majority of jailbreak research is academic work dressed up as enterprise security advice. Direct prompt injection — telling the AI "ignore your instructions and do X instead" — requires the attacker to already control the user's input channel. In practice, that means the attacker already has the user's session or is the user. That threat model exists, but it ranks well below phishing, credential theft, and unpatched VPNs on any serious enterprise risk register.

OWASP LLM01 covers prompt injection and it is real. But the community weights direct injection — the simpler, flashier attack — far above indirect injection, which is harder to pull off and dramatically more dangerous in production systems. Jailbreak papers produce impressive demos. Red-teaming for "AI safety" — testing whether a model will produce harmful content — is not the same discipline as agent security. Treating them as equivalent wastes analyst time.

The enterprise question is not "can I make GPT-4 say something rude." The question is: "can an attacker influence what my agent does with my internal tools." Those are different problems requiring different skill sets.

### "Prompt Firewalls" as a Solution

There are now products — some from credible vendors — that claim to detect and block prompt injection before it reaches the model. The problem is that none of them have published calibrated true positive rates and false positive rates against real indirect injection datasets. Not one. They publish vague benchmark numbers against handcrafted examples, which is not the same thing.

Prompt injection via indirect channels is an unbounded attack surface. Every piece of text the agent reads — web pages, email, documents, tool outputs, RAG chunks — is a potential injection vector. A firewall that sits on the user's direct input channel does not cover a poisoned document the agent retrieves from your SharePoint. The attack surface is not the chat box. The attack surface is everything the agent reads.

A detection control with unknown FPR is not a control. It is a checkbox. Before deploying any prompt injection detector in production, you need a calibrated eval: a labeled dataset of benign and injected inputs, a measured TPR at your chosen operating FPR, and a documented false positive rate against real enterprise traffic. Most teams cannot answer any of these questions about the tools they are buying.

### AGI Framing in Security Contexts

Framing routine AI security problems as "alignment problems" or "AGI risk" is counterproductive operationally. The actual threat is a confused agent that read a poisoned document and made a consequential tool call — sent an email it should not have sent, queried a database it should not have queried, exfiltrated data through a parameter it was authorized to write.

That is a software vulnerability. It requires software security controls: sandboxing, tool call auditing, human-in-the-loop gates, anomaly detection. Not philosophical alignment research.

Scale your threat model to what agents actually do: read inputs, reason, call tools, produce outputs. The AGI framing shifts attention away from those four steps toward abstract debates that do not reduce your attack surface today.

### Most Current AI Security Certifications

As of 2025, no major certification covers indirect prompt injection, tool call abuse, or agentic system security in a rigorous, engineering-level way. The certifications that exist treat "AI red-teaming" as a standalone discipline — separate from the detection engineering, threat modeling, and incident response skills that make red-team findings operationally useful.

The field is immature. Certification bodies lag the threat landscape by two to five years in established domains; in a domain this new, expect certs to lag at least that long. A certification that teaches jailbreak identification but not eval harness engineering, STRIDE threat modeling, or SOAR playbook writing is not preparing you for what enterprise teams need. Build portfolio artifacts that demonstrate engineering depth. A working eval harness producing calibrated ASR deltas is more credible than any cert currently available.

### RLHF as a Security Fix

Reinforcement learning from human feedback and safety fine-tuning do reduce certain categories of jailbreaks. Models trained with RLHF are less likely to comply with direct requests for harmful content. That is real and valuable for the chatbot use case.

RLHF does not prevent indirect prompt injection via tool results. When an agent reads a tool result containing a malicious payload, that payload arrives through the same channel as legitimate data — not a user message that safety training learned to scrutinize. Sandboxing and tool call authorization are the controls for agent misbehavior, not fine-tuning.

Teams that treat RLHF as their agent security posture have no agent security posture. They have a model less likely to swear at users and no controls on what tools it calls based on what it reads.

---

## Section 2: What's Actually Useful

Ranked by enterprise value, not by research novelty.

### 1. Indirect Prompt Injection (Highest Priority)

This is the attack that is actively compromising production systems today. An agent reads untrusted content — a web page, a document, an email, a RAG chunk — that contains an adversarial instruction. The agent follows that instruction because it cannot distinguish legitimate tool output from adversarial payload in that output.

This is not theoretical. Invariant Labs published a GitHub MCP attack in May 2025 demonstrating tool poisoning via repository content. EchoLeak (CVE-2025-32711) showed data exfiltration through Microsoft 365 Copilot via injected content in documents. CVE-2025-59944 affected Cursor's MCP integration. CVE-2025-68143, CVE-2025-68144, and CVE-2025-68145 documented indirect injection vulnerabilities in Anthropic's Git MCP tooling.

Any organization running LLM agents with tool access — which includes every enterprise that deployed Copilot, Claude, or a custom agent with RAG — is exposed to this class of attack right now. This is the top priority.

### 2. Lethal Trifecta Architecture

Simon Willison coined the framing: an agent becomes a data exfiltration primitive when it combines (a) access to private data, (b) exposure to untrusted input, and (c) the ability to communicate externally. When all three legs are present, indirect injection turns into a data exfiltration channel — an attacker plants a payload in content the agent reads, and the agent leaks private data through an authorized outbound tool call.

This framing is the right starting point for threat modeling. Before evaluating any agentic system, map it to these three legs. If all three are present and there are no controls at each leg — data access controls, input sanitization or sandboxing, and outbound tool call gates — the system has a structural exfiltration vulnerability. The trifecta analysis takes one hour and surfaces more risk than a week of ad-hoc testing.

### 3. Eval Engineering

The gap between "we tested it" and "we measured it" is enormous and almost no teams are on the right side of that gap. Deterministic, reproducible evaluation is a transferable skill from software QA that AI security teams desperately lack.

Every team should be able to answer: What is our agent's attack success rate at our current defense configuration? What is our detector's TPR at 5% FPR against our production traffic? What is the confidence interval? Most teams cannot answer any of them.

Eval engineering means building labeled datasets, defining programmatic success criteria, running attacks and defenses against those datasets, computing TPR/FPR/ASR with bootstrap confidence intervals, and tracking those numbers over time. The output is a number that does not rely on anyone's judgment call — and recruiters cannot argue with it.

### 4. Detection and IR for AI Incidents

SOC analysts and SOAR engineers have a structural advantage in this domain. The skills transfer directly: canonical log schemas, streaming anomaly detection, alert engineering, playbook design, human-in-the-loop workflows. The domain is new but the job is the same — detect, alert, triage, respond.

What does not exist yet: standardized log schemas for agent tool calls, SOAR playbooks for AI agent incidents, runbooks for "agent made unexpected external call." The teams that build this infrastructure now will define what good looks like. Detection engineering adapted for AI agents — with agent-native event schemas and alert logic tuned to tool call anomalies — is the highest-demand skill in this space with the fewest people who can do it.

### 5. Threat Modeling for Agentic Systems

STRIDE applied per component, OWASP LLM Top 10 2025, OWASP Agentic Top 10 2025, MITRE ATLAS. Most AI teams have not done a systematic threat model for their agents. An engineer who can produce a complete STRIDE analysis of an agentic system — mapping threats to OWASP controls and MITRE ATLAS techniques — and translate that into a control mapping with prioritized gaps is delivering something most organizations do not have.

The Agentic Top 10 from OWASP (published 2025) covers agent-specific risks that the LLM Top 10 does not fully address: orchestrator exploitation, memory poisoning, agent identity abuse. These frameworks exist. Using them systematically on real systems is the gap.

### 6. RAG Security

Corpus poisoning — inserting adversarial documents into the retrieval corpus to influence agent behavior — is under-studied relative to its exploitability. Embedding-space attacks (manipulating vectors to control retrieval) and citation laundering (getting an agent to cite a poisoned source as authoritative) are directly exploitable in production RAG pipelines. This is a specialist niche but one that is growing as RAG becomes the default deployment pattern for enterprise AI.

---

## Section 3: Market-Valuable Skills, Ranked

1. **Detection engineering adapted for AI agents.** Highest demand, fewest practitioners. SOC engineers who can define agent-native event schemas, write alert logic for tool call anomalies, and build SOAR playbooks for AI incidents are in a category of roughly zero right now. This is where the leverage is.

2. **Eval/red-team engineering.** Reproducible, measurable attacks with calibrated datasets and confidence intervals. The word "red-teaming" is overloaded and undersells this skill. What enterprises need is not someone who can find a creative jailbreak. They need someone who can run a structured attack dataset against their deployed agent, compute ASR, and tell them whether their defense is working to a stated confidence level.

3. **Threat modeling for agentic systems.** Not chatbots. Not "AI systems" generically. Specifically: tool-using agents with memory and external integrations, modeled in STRIDE, mapped to OWASP and MITRE ATLAS, with a resulting control gap list. This is a deliverable. Teams that can produce it will be hired.

4. **SOAR playbook design for AI incidents.** Direct transfer from IR practice. Tines, XSOAR, Sentinel SOAR — the platforms are the same. The playbooks are new: what do you do when your agent made an unexpected external tool call? When does a human review a flagged tool invocation? How do you isolate a compromised agent session? These playbooks do not exist. Writing them is portfolio work.

5. **Tool gateway and sandbox design.** Platform-level work with higher technical barrier. Designing the layer that sits between the agent and its tools — enforcing tool call authorization, input/output sanitization, rate limiting, and audit logging — requires infrastructure engineering skills. High value, harder to fake with a blog post.

6. **RAG security.** Specialist niche, growing. Under-studied in proportion to how widely RAG is deployed. An engineer who can characterize the attack surface of a specific RAG pipeline — retrieval manipulation, corpus poisoning, citation exploitation — and propose concrete mitigations is ahead of the field.

---

## Section 4: Beginner Mistakes to Avoid

**Treating the system prompt as the security boundary.** It is not. Tool results bypass it. The system prompt tells the agent how to behave in the absence of conflicting instruction. A poisoned tool result is a conflicting instruction that arrives through a channel the system prompt cannot govern.

**Testing only direct injection.** Direct injection is the easy demo. Indirect injection via RAG and web retrieval is the actual enterprise risk. If your red-team findings cover only inputs the attacker directly controls, you have tested the wrong attack surface.

**Building detectors without calibrating them.** A detector with an unknown false positive rate is not deployable in production. You do not know what you are blocking. Calibrate every detector against a realistic benign distribution before putting it in a production pipeline. A 95% true positive rate sounds good until you learn it comes with a 30% false positive rate on normal enterprise documents.

**Confusing safety alignment research with operational security.** Safety alignment research is a legitimate academic field. It is not the operational security practice your team needs. Understanding the distinction — and being able to explain it to stakeholders — is itself a valuable skill.

**Skipping the threat model and going straight to tools.** Tool selection without a threat model produces a collection of controls with unknown coverage. The threat model tells you what you are defending. Without it, you cannot know whether your tools address the right risks.

**Measuring "blocked" without measuring false positive rate on benign inputs.** A control that blocks everything achieves 100% attack blocking with a 100% false positive rate. Teams that report "we blocked X attacks" without reporting "and we blocked Y legitimate requests" are reporting half the number. Both halves matter.

---

## Section 5: How to Turn This Into Portfolio Output

Four concrete outputs from completing this repository that produce artifacts a recruiter or senior engineer can evaluate:

**1. `evals/results/latest_summary.md` — ASR delta table.** An attack success rate table showing baseline ASR vs. defended ASR for each attack category, with confidence intervals. This is a number. It does not depend on anyone's opinion of whether your work is good. A baseline ASR of 0.82 and a defended ASR of 0.11 with a 95% confidence interval is a claim that can be verified or challenged. That is what separates engineering from storytelling.

**2. The protected agent.** A composed defense — input validation, tool call sandboxing, output filtering, anomaly detection — that you can demo against the attack datasets. Not a writeup about defenses. A running system that demonstrably reduces ASR against a documented attack set. Show the before and after numbers.

**3. SOAR playbooks — Tines and XSOAR.** A Tines story that ingests agent tool call logs, runs anomaly detection, and routes high-confidence alerts to a human review queue is a deliverable most AI security job descriptions ask for and almost no candidates can provide. XSOAR playbooks for the same use case cover the other major enterprise platform.

**4. A conference talk abstract: "Detecting AI Agent Attacks in Your SOAR."** A submittable abstract demonstrating the SOC-to-AI-security translation enterprise teams need. The argument: SOC engineers already have the detection and IR skills AI security teams lack. The talk draws on the alert engineering, playbook design, and HITL workflow work in this repository — not a thought leadership piece, an engineering talk with numbers, code, and demo material.

These four outputs are specific, measurable, and hard to fake. They answer the question that matters to a hiring manager: can this engineer build something that works and prove it works.
