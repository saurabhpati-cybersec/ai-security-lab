# Day 9 References: Input/Output Validation

## Primary References

1. **OWASP LLM Top 10 2025, LLM05: Improper Output Handling**
   - https://owasp.org/www-project-top-10-for-large-language-model-applications/
   - Authoritative taxonomy of output-channel attack vectors

2. **Willison, Simon (2023) — "Dual LLM pattern for building more capable, safer agents"**
   - https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
   - The architectural basis for separating privileged agent from sanitization layer

3. **OWASP LLM Top 10 2025, LLM01: Prompt Injection**
   - https://owasp.org/www-project-top-10-for-large-language-model-applications/
   - Input-side attack taxonomy

## Related Reading

- `detectors/output_filter.py` — implementation of the output filter with allowlist configuration
- `detectors/rules.py` — input detector rules and weight system
- Greshake et al. (2023) — "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications" — https://arxiv.org/abs/2302.12173
- Riley (2023) — "Indirect Prompt Injection Threats" — https://embracethered.com/blog/posts/2023/indirect-prompt-injection-threats/
- EchoLeak (CVE-2025-32711) — Microsoft 365 Copilot markdown exfiltration via calendar invite injection
