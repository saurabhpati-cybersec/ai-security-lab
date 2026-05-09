# Day 3 References: Direct Prompt Injection

## Primary Standards

- OWASP LLM Top 10 2025 — LLM01: Prompt Injection
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/

## Research Papers

- Perez, F. & Ribeiro, I. (2022). "Ignore Previous Prompt: Attack Techniques For Language Models."
  https://arxiv.org/abs/2211.09527

- Greshake, K. et al. (2023). "Not What You've Signed Up For: Compromising Real-World LLM-Integrated
  Applications with Indirect Prompt Injection." https://arxiv.org/abs/2302.12173

- Branch, H.J. et al. (2022). "Evaluating the Susceptibility of Pre-Trained Language Models via
  Handcrafted Adversarial Examples." https://arxiv.org/abs/2209.02128

## Simon Willison Blog Series (Authoritative)

- Original prompt injection discovery (2022):
  https://simonwillison.net/2022/Sep/12/prompt-injection/

- "Delimiters won't save you from prompt injection" (2023):
  https://simonwillison.net/2023/May/11/delimiters-wont-save-you/

- Prompt injection tag (ongoing, updated as new incidents emerge):
  https://simonwillison.net/tags/promptinjection/

- "The Dual LLM pattern for building AI assistants that can resist prompt injection" (2023):
  https://simonwillison.net/2023/Apr/25/dual-llm-pattern/

## Historical Context

- Riley Goodside, original prompt injection demonstrations via Twitter (2022):
  https://twitter.com/goodside/status/1569128808308957185

- ChatGPT plugin prompt injection incidents (2023), multiple sources:
  https://embracethered.com/blog/posts/2023/chatgpt-plugin-prompt-injection/

## Encoding-Based Injection Variants

- Johann Rehberger, "Embrace The Red" blog — comprehensive injection technique catalog:
  https://embracethered.com/blog/

- Base64 and encoded payload injection analysis:
  https://embracethered.com/blog/posts/2023/chatgpt-base64-prompt-injection/
