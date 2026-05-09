# Day 14: Capstone Publish — Polish and Portfolio

## 1. Objective

Polish the repo for public portfolio. Write a demo video script. Write four blog post outlines. Write one conference talk abstract. The deliverable is a repo that passes the recruiter-skim test (30 seconds), the hiring manager test (5 minutes), and the senior engineer test (45 minutes).

---

## 2. Why It Matters

The goal is a portfolio that gets callbacks. This day structures the narrative so you can explain the work in three time frames:

- **30 seconds (recruiter):** "I built a 14-day AI agent security lab. I attacked and defended an LLM agent with real tools. I measured the attack success rate before and after defenses. Here's the repo."
- **5 minutes (hiring manager):** Walk through the lethal trifecta, show the eval output, mention the SOAR playbooks.
- **45 minutes (senior engineer):** The conference talk in `defense/talk_abstract.md`.

Security work that is not communicated is not credited. This day is the communication layer.

---

## 3. Threat Model Reference

N/A — Day 14 is the publication and communication phase. No new threats are introduced.

For reference, the full threat model is in `docs/threat-model.md` covering T-01 through T-17.

---

## 4. Trifecta Mapping

N/A — Day 14 documents and publishes the work of Days 0-13. The trifecta was addressed in the defense stack (Day 12) and measured in the red-team (Day 13).

---

## 5. Prerequisites

- Days 0-13 complete
- `evals/results/latest_summary.md` populated with real ASR numbers (or at minimum, dataset sizes and eval instructions)
- `agents/protected/agent.py` importable and running
- `python3 labs/day-14-capstone-publish/eval.py` produces output (even if PARTIAL — fix before publishing)

---

## 6. Hands-On Lab

**Step 1.** Read through the full repo from a stranger's perspective. Ask: does the README pass the recruiter-skim test?

```
wc -w README.md
```

Target: 600-900 words. Check that there is a one-paragraph summary at the top, a table of contents or lab list, and an honest-claims section.

**Step 2.** Run the Day 14 eval to see what is missing:

```
python3 labs/day-14-capstone-publish/eval.py
```

Fix each PARTIAL item. Note: `soar-companion/shared/log-schema.md` and `alert-catalog.md` are created in Task 17 — the eval will show those as missing until then. That is intentional; it tracks completion of the full project.

**Step 3.** Review and rehearse the demo video script:

```
cat labs/day-14-capstone-publish/defense/demo_script.md
```

Walk through the script with a real terminal. Time yourself. Target: 3-5 minutes. The script is annotated with expected durations.

**Step 4.** Review the four blog outlines and pick one to draft:

```
cat labs/day-14-capstone-publish/defense/blog_outlines.md
```

Recommended first post: Post 1 ("The Lethal Trifecta") — it has the broadest audience and the clearest hook.

**Step 5.** Review the conference talk abstract and submit to at least one CFP:

```
cat labs/day-14-capstone-publish/defense/talk_abstract.md
```

The CFP submission checklist is at the bottom of the file. BSides [your city] is the most accessible first venue.

---

## 7. Attack Scenario

N/A — Day 14 does not introduce new attacks. For the demo, use the attack scenarios from Day 3 (direct injection) and Day 4 (indirect injection) as live demonstrations.

---

## 8. Defensive Control

N/A — Day 14 documents the defenses built in Days 8-12. The composed defense stack is in `agents/protected/agent.py`. The demo script in `defense/demo_script.md` shows how to present those defenses to a technical or semi-technical audience.

---

## 9. Expected Output

```
python3 labs/day-14-capstone-publish/eval.py
```

Expected output when all tasks (including Task 17) are complete:

```
PASS: all 18 required files present
PASS: all 5 required directories present
PASS: README is XXX words

Day 14 eval: PASS — portfolio complete
```

Before Task 17 completes, the eval will show:

```
Missing files:
  - soar-companion/shared/log-schema.md
  - soar-companion/shared/alert-catalog.md

Day 14 eval: PARTIAL — some items missing (see above)
```

This is expected. Run the eval at the end of the full project to confirm all items are in place.

---

## 10. Evaluation

```
python3 labs/day-14-capstone-publish/eval.py
```

The eval checks:
- All 18 required files exist (including soar-companion/shared/ files from Task 17)
- All 5 required directories exist
- README.md is at least 500 words

Additional manual checks (not automated):
- README passes recruiter-skim test
- Demo video recorded or scripted
- At least one blog outline drafted
- CFP submitted

---

## 11. Difficulty

2/5

This day requires no new code. The difficulty is in the communication work: writing clearly for different audiences, presenting attack and defense in 3-5 minutes without losing technical credibility, and submitting work publicly where it can be evaluated.

---

## 12. Time Required

4-6 hours

Breakdown:
- 1 hour: run eval, fix PARTIAL items, confirm all files present
- 30 min: recruiter-skim review of README
- 1-2 hours: rehearse and record demo video (or write full script with timing annotations)
- 1 hour: pick one blog outline, draft first 500 words
- 30 min: customize and submit talk abstract to one CFP

---

## 13. Document

After completing the lab, update `docs/learning-tracker.md` for Day 14:

- `python3 labs/day-14-capstone-publish/eval.py` output (PASS or PARTIAL with explanation)
- Link to public GitHub repo (if published)
- Link to blog post (if published) or blog outline chosen
- Conference CFP submitted (venue and submission date)
- Demo video link or recording status

The final entry in learning-tracker.md for Day 14 should read:

```
Day 14 complete. Repo published at [URL]. eval.py: PASS.
Blog outline: [Post N title]. CFP submitted: [Venue, date].
Demo video: [link or "scripted, recording pending"].
```

---

## 14. References

- Portfolio and career resources: see `labs/day-14-capstone-publish/references.md`
- Conference CFP submission checklist: see `defense/talk_abstract.md` (bottom of file)
- Blog post outlines: `defense/blog_outlines.md`
- Demo video script: `defense/demo_script.md`
- OWASP LLM Top 10 2025: https://genai.owasp.org/
- MITRE ATLAS: https://atlas.mitre.org/
- NIST AI RMF 1.0: https://airc.nist.gov/RMF/Overview
