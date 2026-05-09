# Day 13 References: Capstone Attack — Red-Teaming

## Standards and Threat Catalogs

- OWASP LLM Top 10 2025 — Full list: https://genai.owasp.org/
- MITRE ATLAS — Adversarial Threat Landscape for AI Systems: https://atlas.mitre.org/
- NIST AI RMF 1.0 — Govern, Map, Measure, Manage: https://airc.nist.gov/RMF/Overview

## Research: Prompt Injection Attacks

- Greshake, K. et al. (2023), "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection":
  https://arxiv.org/abs/2302.12173

- Perez, F. & Ribeiro, I. (2022), "Ignore Previous Prompt: Attack Techniques For Language Models":
  https://arxiv.org/abs/2211.09527

- Zhan, Q. et al. (2024), "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents":
  https://arxiv.org/abs/2403.02691

## Real Incidents (2025)

- EchoLeak (CVE-2025-32711) — Microsoft Copilot leaked calendar emails via indirect prompt injection through email body content:
  https://nvd.nist.gov/vuln/detail/CVE-2025-32711

- GitHub MCP prompt injection (May 2025) — injection via repository README content processed by the GitHub MCP server:
  https://github.com/github/mcp-server/security

- CVE-2025-59944 — Cursor IDE: prompt injection via MCP tool description field, allowing tool description to override cursor instructions:
  https://nvd.nist.gov/vuln/detail/CVE-2025-59944

- CVE-2025-68143/68144/68145 — Anthropic Git MCP server: git commit message and branch name injection:
  https://nvd.nist.gov/vuln/search/results?query=CVE-2025-68143

## SSRF and URL Bypass Techniques

- PortSwigger Web Academy — SSRF with filter bypass:
  https://portswigger.net/web-security/ssrf/bypassing-ssrf-filters

- Alternative IP representations for SSRF bypass (decimal, hex, octal):
  https://www.hackingarticles.in/ssrf-vulnerability-exploitation/

- AWS EC2 metadata endpoint (169.254.169.254) exploitation via SSRF:
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-security-warnings.html

## Adaptive Attack Research

- Johann Rehberger, "Embrace The Red" — comprehensive injection technique catalog with adaptive examples:
  https://embracethered.com/blog/

- Andy Ayrey et al. (2024), "Many-Shot Jailbreaking" — threshold-based detection evasion:
  https://www.anthropic.com/research/many-shot-jailbreaking

- Shen et al. (2023), "'Do Anything Now': Characterizing and Evaluating In-The-Wild Jailbreak Prompts on Large Language Models":
  https://arxiv.org/abs/2308.03825

## Red-Teaming Methodology

- OWASP Testing Guide — penetration testing methodology applicable to AI systems:
  https://owasp.org/www-project-web-security-testing-guide/

- NIST SP 800-115 — Technical Guide to Information Security Testing and Assessment:
  https://csrc.nist.gov/publications/detail/sp/800-115/final

- Microsoft, "Responsible AI Maturity Model" — red-teaming in AI context:
  https://blogs.microsoft.com/on-the-issues/2022/06/21/microsofts-responsible-ai-program/
