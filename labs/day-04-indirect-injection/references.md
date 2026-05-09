# Day 4 References: Indirect Prompt Injection

## Documented Incidents (2025)

- Invariant Labs, "GitHub Copilot MCP Indirect Prompt Injection" (May 2025):
  https://invariantlabs.ai/blog/mcp-github-copilot-indirect-prompt-injection

- Supabase Cursor incident (mid-2025) — MCP-enabled IDE injected via repository README:
  Coverage via Embrace The Red and security community reporting.

- CVE-2025-32711 (EchoLeak — Microsoft 365 Copilot):
  IPI via calendar invite body caused private email exfiltration.
  https://nvd.nist.gov/vuln/detail/CVE-2025-32711

- CVE-2025-59944 (Cursor): IPI in MCP tool description caused unauthorized code execution.
  https://nvd.nist.gov/vuln/detail/CVE-2025-59944

- CVE-2025-68143 (Anthropic Git MCP — git commit message IPI):
  https://nvd.nist.gov/vuln/detail/CVE-2025-68143

- CVE-2025-68144 (Anthropic Git MCP — variant):
  https://nvd.nist.gov/vuln/detail/CVE-2025-68144

- CVE-2025-68145 (Anthropic Git MCP — variant):
  https://nvd.nist.gov/vuln/detail/CVE-2025-68145

## Foundational Research

- Greshake, K. et al. (2023). "Not What You've Signed Up For: Compromising Real-World
  LLM-Integrated Applications with Indirect Prompt Injection."
  https://arxiv.org/abs/2302.12173

- Perez, F. & Ribeiro, I. (2022). "Ignore Previous Prompt: Attack Techniques For Language Models."
  https://arxiv.org/abs/2211.09527

## Techniques

- Johann Rehberger, "ASCII Smuggling — Unicode Tag Characters in Prompt Injection" (2024):
  https://embracethered.com/blog/posts/2024/claude-computer-use-prompt-injection-and-ascii-smuggling/

- Johann Rehberger, "Embrace The Red" blog — most comprehensive IPI technique catalog:
  https://embracethered.com/blog/

- Rehberger, J., "Bing Chat: Bing, I want to be a pirate" (early IPI via Bing search results, 2023):
  https://embracethered.com/blog/posts/2023/bing-chat-data-exfiltration-via-markdown-images/

## Conceptual Framework

- Simon Willison, "The lethal trifecta for LLM-based agentic systems":
  https://simonwillison.net/2023/Apr/14/llm-agents/

- Simon Willison, "Indirect prompt injection" (2023):
  https://simonwillison.net/2023/Apr/14/llm-agents/

- OWASP LLM Top 10 2025 — LLM01: Prompt Injection (covers both direct and indirect):
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
