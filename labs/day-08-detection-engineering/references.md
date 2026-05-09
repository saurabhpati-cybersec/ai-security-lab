# Day 8 References: Detection Engineering

## Primary References

1. **OWASP LLM Top 10 2025, LLM01: Prompt Injection**
   - https://owasp.org/www-project-top-10-for-large-language-model-applications/
   - The authoritative categorization of prompt injection attack types

2. **Zheng et al. (2023) — "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena"**
   - https://arxiv.org/abs/2306.05685
   - LLM-as-judge calibration methodology for classification tasks

3. **Efron & Tibshirani (1993) — "An Introduction to the Bootstrap"**
   - ISBN 978-0412042317
   - Foundation of bootstrap confidence interval methodology used in `scorers.py`

4. **Confusion Matrix Notation**
   - TPR = TP / (TP + FN); FPR = FP / (FP + TN)
   - Standard binary classification terminology applied to injection detection

## Related Reading

- `detectors/README.md` — detector internals, extension guide, and threshold tuning
- `evals/harness/README.md` — eval harness architecture and scorer documentation
- Willison, Simon (2022) — "Prompt injection attacks against GPT-3" — https://simonwillison.net/2022/Sep/12/prompt-injection/
- Perez & Ribeiro (2022) — "Ignore Previous Prompt: Attack Techniques for Language Models" — https://arxiv.org/abs/2211.09527
