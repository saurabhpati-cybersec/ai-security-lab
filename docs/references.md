# References

Full bibliography for the ai-security-lab repository. Entries are grouped by category and formatted for reproducibility. For CVEs that cannot be fully verified at time of writing, NVD is the authoritative source for current details.

---

## Frameworks and Taxonomies

**[OWASP LLM Top 10 2025]**
OWASP Top 10 for Large Language Model Applications, 2025 Edition. OWASP Foundation. 2025. URL: https://owasp.org/www-project-top-10-for-large-language-model-applications/
*Relevance: Primary risk taxonomy used throughout this repository; every threat in docs/threat-model.md is mapped to an LLM01–LLM10 entry.*

**[OWASP Agentic Top 10 2025]**
OWASP Top 10 for Agentic AI Systems, 2025 Edition. OWASP Foundation. 2025. URL: https://owasp.org/www-project-top-10-for-agentic-ai-systems/
*Relevance: Agent-specific risk taxonomy covering orchestrator exploitation, excessive agency, and trust boundary violations; every threat in docs/threat-model.md is mapped to an AAA-01–AAA-10 entry.*

**[MITRE ATLAS]**
MITRE ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems. MITRE Corporation. Ongoing (continuously updated). URL: https://atlas.mitre.org/
*Relevance: ATT&CK-structured knowledge base of adversarial ML and LLM techniques; provides technique-level detail for attacks mapped at the OWASP category level.*

---

## Foundational Research and Blog Posts

**[Willison Trifecta]**
"Prompt injection and the lethal trifecta." Simon Willison. simonwillison.net. 2023. URL: https://simonwillison.net/2023/Apr/14/prompt-injection/
*Relevance: Coins the lethal trifecta framing (data + untrusted input + egress = exfiltration primitive) that is the primary structural analysis tool in this repository.*

**[Willison Delimiters]**
"Delimiters won't save you from prompt injection." Simon Willison. simonwillison.net. 2023. URL: https://simonwillison.net/2023/May/11/delimiters-wont-save-you/
*Relevance: Explains why syntactic defenses (XML tags, delimiters) do not prevent injection; informs the repository's position that semantic detection and tool gating are required.*

**[Willison Dual LLM]**
"The dual LLM pattern for building AI assistants that can resist prompt injection." Simon Willison. simonwillison.net. 2023. URL: https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
*Relevance: Proposes separating privileged and unprivileged LLM roles as an architectural mitigation; referenced in the protected agent design.*

**[Willison IPI Tag]**
Ongoing coverage of prompt injection and indirect prompt injection. Simon Willison. simonwillison.net. 2023–2025. URL: https://simonwillison.net/tags/promptinjection/
*Relevance: Continuously updated collection of real-world IPI incidents and research; primary reference for tracking the evolving attack landscape.*

**[Embrace The Red]**
Embrace The Red — AI and LLM security research blog. Johann Rehberger. embracethered.com. 2023–2025. URL: https://embracethered.com/blog/
*Relevance: Documents real-world indirect prompt injection exploits against ChatGPT plugins, Copilot, Bing, and other production systems; primary source for attack technique detail in the lab exercises.*

**[Lakera Guidance]**
Prompt Injection: Attack and Defense. Lakera AI. lakera.ai. 2024. URL: https://www.lakera.ai/blog/prompt-injection-attacks
*Relevance: Practitioner-oriented guidance on prompt injection attack taxonomy and detection approaches; reference for detector design in detectors/.*

---

## MCP and Tool-Use Attacks

**[Invariant MCP]**
"Researchers Discover Prompt Injection Vulnerabilities in GitHub MCP Server." Invariant Labs. invariantlabs.ai. May 2025. URL: https://invariantlabs.ai/blog/mcp-github-prompt-injection
*Relevance: Documents tool description poisoning and indirect injection via repository content in a widely-used MCP server; primary real-world reference for T-10 and T-02.*

---

## CVEs and Vulnerability Reports

**[EchoLeak]**
EchoLeak: Data Exfiltration via Microsoft 365 Copilot Indirect Prompt Injection. Aim Security researchers. 2025. CVE-2025-32711. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Production demonstration of the full lethal trifecta — IPI via document content causes Copilot to exfiltrate private data via a markdown image URL; primary real-world reference for T-06 and T-14.*

**[CVE-2025-59944]**
CVE-2025-59944. Indirect prompt injection vulnerability in Cursor IDE's MCP integration allowing unauthorized action execution via attacker-controlled tool output. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Real-world MCP injection attack in a production development tool; reference for T-02 and T-10.*

**[CVE-2025-68143]**
CVE-2025-68143. Indirect prompt injection vulnerability in Anthropic's Git MCP server via malicious repository content. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Demonstrates that vendor-maintained MCP servers are susceptible to IPI via source repository content; reference for T-03 and T-10.*

**[CVE-2025-68144]**
CVE-2025-68144. Indirect prompt injection vulnerability in Anthropic's Git MCP server — second variant. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Second variant in the Anthropic Git MCP vulnerability cluster; demonstrates breadth of the MCP injection surface.*

**[CVE-2025-68145]**
CVE-2025-68145. Indirect prompt injection vulnerability in Anthropic's Git MCP server — third variant. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Third variant in the Anthropic Git MCP vulnerability cluster; reference for supply chain trust concerns in T-10.*

**[CVE-2025-6514]**
CVE-2025-6514. Indirect prompt injection vulnerability in mcp-remote, allowing injection via proxied remote MCP server content. Source: NVD / vendor advisory. Note: cite from NVD at nvd.nist.gov for current details.
*Relevance: Demonstrates that MCP proxy/relay components are also injection surfaces, extending the attack surface beyond direct MCP servers; reference for T-10 and T-03.*

---

## Benchmarks and Evaluations

**[ASB]**
Agent Security Bench (ASB): Evaluating the Security of LLM-Based Agents. Research team (multiple authors). ICLR 2025. URL: https://openreview.net/forum?id=ASB2025 (check ICLR 2025 proceedings for current URL)
*Relevance: Provides a structured benchmark methodology for evaluating agent security controls, including attack success rate measurement; informs the eval harness design in evals/harness/.*

**[MCPTox]**
MCPTox: A Benchmark for Evaluating Toxicity and Injection Attacks in Model Context Protocol Deployments. URL: https://github.com/MCPTox/benchmark (verify current location at time of use)
*Relevance: MCP-specific injection benchmark providing labeled attack datasets relevant to T-02, T-10; reference for dataset construction in evals/datasets/.*

---

## API and Protocol Documentation

**[Anthropic Docs]**
Anthropic Claude API Documentation. Anthropic. 2024–2025. URL: https://docs.anthropic.com/
*Relevance: Primary reference for Claude API usage, tool use schema, system prompt construction, and model behavior used throughout the reference agent implementation.*

**[OpenAI Docs]**
OpenAI API Documentation. OpenAI. 2024–2025. URL: https://platform.openai.com/docs/
*Relevance: Reference for the OpenAI-compatible tool call schema supported by the agent's thin adapter; required for the multi-provider support described in README.md.*
