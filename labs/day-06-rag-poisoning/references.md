# Day 6 References: RAG Corpus Poisoning

## MITRE ATLAS

- AML.T0020 — Poison Training Data (generalized poisoning technique):
  https://atlas.mitre.org/techniques/AML.T0020

- AML.T0018 — Backdoor ML Model:
  https://atlas.mitre.org/techniques/AML.T0018

## Phantom Document / RAG-Specific Poisoning

- Chan, A. et al. (2024). "Phantom: General Trigger Attacks on Retrieval Augmented Language
  Generation." Formalizes the high-cosine-similarity phantom document attack.
  https://arxiv.org/abs/2405.20485

- Shafran, A. et al. (2024). "Machine Against the RAG: Jamming Retrieval-Augmented Generation
  with Blocker Documents."
  https://arxiv.org/abs/2406.05870

- Zou, A. et al. (2024). "Poisoning Web-Scale Training Datasets is Practical."
  https://arxiv.org/abs/2302.10149

## IPI + Corpus Poisoning Combined

- Greshake, K. et al. (2023). "Not What You've Signed Up For: Compromising Real-World
  LLM-Integrated Applications with Indirect Prompt Injection." Section on corpus-mediated IPI.
  https://arxiv.org/abs/2302.12173

## General Poisoning Literature

- Carlini, N. et al. (2021). "Poisoning the Unlabeled Dataset of Semi-Supervised Learning."
  https://arxiv.org/abs/2105.01622

- Biggio, B. et al. (2012). "Poisoning Attacks against Support Vector Machines."
  (Historical foundation for poisoning attack theory.)
  https://arxiv.org/abs/1206.6389

## OWASP

- OWASP LLM Top 10 2025 — LLM06: Excessive Agency:
  https://genai.owasp.org/llmrisk/llm06-excessive-agency/

- OWASP LLM Top 10 2025 — LLM03: Training Data Poisoning:
  https://genai.owasp.org/llmrisk/llm03-training-data-poisoning/

## Citation Laundering

- Concept discussed in: Willison, S., "The dual LLM pattern" (2023):
  https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
  (The problem of an agent attributing attacker-supplied content to trusted sources.)
