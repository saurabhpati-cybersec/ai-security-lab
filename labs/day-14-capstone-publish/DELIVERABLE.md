# Day 14 Deliverable: Capstone Publish

The repo is complete. Complete the checklist below before publishing.

## Checklist

- [ ] README passes recruiter-skim test (600-900 words, table of contents, honest claims section)
- [ ] `evals/results/latest_summary.md` contains real ASR numbers from live eval runs
- [ ] Demo video recorded (3-5 min) following `defense/demo_script.md`
- [ ] Four blog outlines drafted (in `defense/blog_outlines.md` — pick one to publish first)
- [ ] Talk abstract submitted to at least one conference CFP
- [ ] `python3 labs/day-14-capstone-publish/eval.py` returns PASS

## Publishing Steps

1. **Final eval check:**
   ```
   python3 labs/day-14-capstone-publish/eval.py
   ```
   Fix any PARTIAL items before publishing.

2. **Populate latest_summary.md:**
   Run live evals and fill in `evals/results/latest_summary.md` with real ASR numbers.
   Estimated numbers are acceptable only if labeled clearly as estimated.

3. **Recruiter-skim test:**
   - Does the root README.md have a one-paragraph "what this is" at the top?
   - Is there a table of contents or day-by-day lab list?
   - Is there an honest-claims section (from Day 0)?
   - Can a non-technical hiring manager understand the project in 30 seconds?

4. **GitHub repository:**
   ```
   git remote add origin https://github.com/[username]/ai-security-lab.git
   git push -u origin main
   ```

5. **Demo video (3-5 min):**
   Follow `defense/demo_script.md` exactly. Record with terminal visible.
   Suggested tools: OBS Studio, QuickTime, or Loom.

6. **Blog post:**
   Pick one of the four outlines in `defense/blog_outlines.md`. Draft and publish.
   Suggested platforms: personal blog, DEV.to, Medium, or LinkedIn article.

7. **Conference CFP:**
   Submit `defense/talk_abstract.md` to at least one venue.
   See the CFP submission checklist at the bottom of `talk_abstract.md`.

## What You Can Claim

After completing Days 0-14:

- "Built a 14-day AI agent security lab: attacked and defended an LLM agent with real tool access"
- "Implemented and measured prompt injection detection with calibrated TPR/FPR tradeoff"
- "Red-teamed my own defenses; produced a residual risk report with real ASR numbers"
- "Wrote SOAR playbooks (Tines + XSOAR) for AI agent incident response"
- "Published 14 labs with machine-evaluable datasets and a composable defense architecture"

## What You Cannot Claim

- "Production-hardened AI security system" — this is a learning lab, not a production deployment
- "100% injection detection" — the adaptive attack section shows what the defenses miss
- "Novel research" — the techniques are documented in prior work (referenced throughout)

Being honest about scope is what makes the portfolio credible.
