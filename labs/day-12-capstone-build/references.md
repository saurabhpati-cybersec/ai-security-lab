# Day 12 References: Capstone Build — Defense Composition

## Standards and Frameworks

- OWASP LLM Top 10 2025 — LLM01: Prompt Injection
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/

- OWASP LLM Top 10 2025 — LLM08: Excessive Agency
  https://genai.owasp.org/llmrisk/llm08-excessive-agency/

- NIST AI Risk Management Framework 1.0 — Measure function
  https://airc.nist.gov/RMF/Overview

- NIST SP 800-53 Rev 5 — Security and Privacy Controls
  https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final

## Defense-in-Depth Architecture

- Simon Willison, "The Dual LLM pattern for building AI assistants that can resist prompt injection" (2023):
  https://simonwillison.net/2023/Apr/25/dual-llm-pattern/

- Anthropic, "Core Views on AI Safety":
  https://www.anthropic.com/research/core-views-on-ai-safety

- OpenAI, "GPT-4 System Card" — defense layer discussion:
  https://cdn.openai.com/papers/gpt-4-system-card.pdf

## Evaluation Methodology

- Bootstrap confidence intervals for ASR:
  https://en.wikipedia.org/wiki/Bootstrapping_(statistics)

- NIST IR 8408 — Understanding Stochastic Gradient Descent for Machine Learning Robustness Evaluation:
  https://csrc.nist.gov/publications/detail/ir/8408/final

- Ribeiro et al. (2020), "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList":
  https://arxiv.org/abs/2005.04118

## Research: Composed Defense Architectures

- Perez & Ribeiro (2022), "Ignore Previous Prompt: Attack Techniques For Language Models":
  https://arxiv.org/abs/2211.09527

- Greshake et al. (2023), "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications":
  https://arxiv.org/abs/2302.12173

- Zhan et al. (2024), "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents":
  https://arxiv.org/abs/2403.02691

## False Positive Rate and Usability

- Sommer & Paxson (2010), "Outside the Closed World: On Using Machine Learning for Network Intrusion Detection" — classic FPR/usability tradeoff paper:
  https://people.eecs.berkeley.edu/~dawnsong/papers/oakland10-ids-ml.pdf

- NIST SP 800-94 Rev 1 — Guide to Intrusion Detection and Prevention Systems (IDPS):
  https://csrc.nist.gov/publications/detail/sp/800-94/rev-1/final
