# References

## Simon Willison — Lethal Trifecta

- Willison, S. "Prompt injection and the 'lethal trifecta'" — https://simonwillison.net/2023/Apr/14/prompt-injection/
- Willison, S. "Delimiters won't save you from prompt injection" — https://simonwillison.net/2023/May/11/delimiters-wont-save-you/
- Willison, S. "The dual LLM pattern for building AI assistants that can resist prompt injection" — https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
- Willison, S. ongoing coverage at https://simonwillison.net/tags/promptinjection/

## Invariant Labs — GitHub MCP Attack (May 2025)

- Invariant Labs. "Researchers Discover Prompt Injection Vulnerabilities in GitHub MCP Server" — May 2025
- Coverage: https://invariantlabs.ai/blog/mcp-github-prompt-injection
- Demonstrates indirect prompt injection via repository content poisoning into MCP tool output

## EchoLeak — CVE-2025-32711

- CVE-2025-32711: Microsoft 365 Copilot indirect prompt injection via document content
- "EchoLeak: Data Exfiltration via Microsoft 365 Copilot" — Aim Security, 2025
- Demonstrates the lethal trifecta in a production enterprise deployment

## CVE-2025-59944 — Cursor MCP

- CVE-2025-59944: Indirect prompt injection in Cursor's MCP integration
- Payload delivered via tool output causing unauthorized action execution
- Reported 2025

## CVE-2025-68143, CVE-2025-68144, CVE-2025-68145 — Anthropic Git MCP

- Three CVEs covering indirect prompt injection vulnerabilities in Anthropic's Git MCP tooling
- Demonstrate that even vendor-maintained MCP servers are susceptible to injection via repository content
- Reported 2025

## OWASP LLM Top 10 2025

- OWASP Top 10 for Large Language Model Applications — 2025 edition
- https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Covers: LLM01 Prompt Injection, LLM02 Insecure Output Handling, LLM03 Training Data Poisoning, and seven others

## OWASP Agentic Top 10 2025

- OWASP Top 10 for Agentic AI Applications — 2025 edition
- https://owasp.org/www-project-top-10-for-agentic-ai-systems/ (working group project)
- Covers orchestrator exploitation, memory poisoning, agent identity abuse, excessive agency, and related agent-specific risks not addressed by the LLM Top 10

## MITRE ATLAS

- MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)
- https://atlas.mitre.org/
- Adversarial ML tactics and techniques knowledge base; maps to MITRE ATT&CK structure
- Relevant matrices: ML Supply Chain Compromise, LLM Prompt Injection, LLM Jailbreak, Craft Adversarial Data
