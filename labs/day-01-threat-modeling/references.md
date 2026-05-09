# Day 1 References

## Primary — Incidents and Reports

- **Invariant Labs: Hacking GitHub Copilot with MCP and Indirect Prompt Injection (May 2025)**
  https://invariantlabs.ai/blog/mcp-github-copilot
  Demonstration that a GitHub repository README can inject instructions into GitHub Copilot agent actions, exfiltrating files without user awareness.

## Frameworks and Standards

- **OWASP Top 10 for Large Language Model Applications 2025**
  https://owasp.org/www-project-top-10-for-large-language-model-applications/
  The authoritative community list of LLM-specific risks, updated in 2025 to cover agentic patterns. LLM01 through LLM10.

- **OWASP Agentic Security Top 10 2025**
  https://genai.owasp.org/llm-top-10/
  Companion list covering AI agent-specific risks. AAA-01 through AAA-10.

- **MITRE ATLAS — Adversarial Threat Landscape for AI Systems**
  https://atlas.mitre.org/
  Attack taxonomy for machine learning systems, analogous to ATT&CK for AI. Covers techniques used in real-world AI attacks.

## Foundational Concepts

- **Simon Willison — The Lethal Trifecta (prompt injection explained)**
  https://simonwillison.net/2023/May/2/prompt-injection-explained/
  Origin of the "lethal trifecta" framing: data + untrusted input + egress = structural exfiltration risk.

- **Adam Shostack — Threat Modeling: Designing for Security**
  https://www.wiley.com/en-us/Threat+Modeling%3A+Designing+for+Security-p-9781118809990
  The canonical reference for STRIDE threat modeling methodology. Chapter 3 covers STRIDE per component.

## This Repository

- `docs/threat-model.md` — The completed threat model for the reference agent
- `docs/glossary.md` — Definitions of T-NN IDs, STRIDE categories, trifecta legs
- `docs/references.md` — Master reference list for the entire lab series
