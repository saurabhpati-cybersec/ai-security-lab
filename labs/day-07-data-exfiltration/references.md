# Day 7 References: Data Exfiltration

## Primary Incidents

- CVE-2025-32711 (EchoLeak — Microsoft 365 Copilot):
  IPI via calendar invite caused private email exfiltration via markdown image URL encoding.
  https://nvd.nist.gov/vuln/detail/CVE-2025-32711

- EchoLeak disclosure (Aim Security, 2025):
  https://www.aim.security/lp/echoleak-vulnerability-disclosure

- Perplexity Comet agent search history exfiltration (2025):
  https://embracethered.com/blog/ (search "Perplexity")

## Foundational Technique Documentation

- Johann Rehberger, "Bing Chat: Data Exfiltration via Markdown Images" (2023):
  Original documentation of the markdown image exfiltration channel.
  https://embracethered.com/blog/posts/2023/bing-chat-data-exfiltration-via-markdown-images/

- Rehberger, J. "ChatGPT Data Exfiltration Vulnerability" (2023):
  https://embracethered.com/blog/posts/2023/chatgpt-data-exfiltration/

- Rehberger, J. "Embrace The Red" — full exfiltration technique catalog:
  https://embracethered.com/blog/

## Conceptual Framework

- Simon Willison, "The lethal trifecta for LLM-based agentic systems" (2023):
  Canonical framing: data access + untrusted input + egress = data breach primitive.
  https://simonwillison.net/2023/Apr/14/llm-agents/

- Greshake, K. et al. (2023). "Not What You've Signed Up For: Compromising Real-World
  LLM-Integrated Applications with Indirect Prompt Injection." Section on exfiltration.
  https://arxiv.org/abs/2302.12173

## OWASP

- OWASP LLM Top 10 2025 — LLM02: Sensitive Information Disclosure:
  https://genai.owasp.org/llmrisk/llm02-sensitive-information-disclosure/

- OWASP Agentic Security Top 10 — AAA-05: Data Leakage and Exfiltration:
  https://genai.owasp.org/agenticsecurity/

- OWASP LLM Top 10 2025 — LLM07: System Prompt Leakage:
  https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/

## Defense Direction (for Days 8-10)

- OWASP LLM Top 10 2025 — LLM06: Excessive Agency (limiting egress capability):
  https://genai.owasp.org/llmrisk/llm06-excessive-agency/

- NCSC UK, "Securing AI: A Framework for Understanding AI-related Security Risks" (2023):
  https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development
