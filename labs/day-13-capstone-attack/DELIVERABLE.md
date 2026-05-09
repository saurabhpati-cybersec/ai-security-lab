# Day 13 Deliverable: Capstone Attack — Red-Team Report

## Red-Team Report (Required)

Complete all four sections below and commit as: `docs: add day-13 red-team residual risk report`

---

### 1. ASR Table

Fill in ASR values from live eval runs (requires API key):

| Dataset | Vulnerable ASR | Protected ASR | Delta |
|---------|---------------|--------------|-------|
| benign (FPR) | ~0% | ~0% | — |
| direct_injection | ___ | ___ | ___ |
| indirect_injection | ___ | ___ | ___ |
| tool_abuse | ___ | ___ | ___ |
| rag_poison | ___ | ___ | ___ |
| exfiltration | ___ | ___ | ___ |

---

### 2. Working Adaptive Attacks

Document at least 2 adaptive attack techniques that bypass the protected agent. For each:

**Attack 1:**
- Name:
- Input (exact):
- Agent response (exact):
- Which defense layer failed:
- Why it failed:

**Attack 2:**
- Name:
- Input (exact):
- Agent response (exact):
- Which defense layer failed:
- Why it failed:

---

### 3. Honest Residual Risk Statement

"The following attack classes still succeed against the protected agent:

- [Attack class]: ASR = X.XX — [brief reason]
- [Attack class]: ASR = X.XX — [brief reason]
- [Attack class]: ASR = X.XX — [brief reason]"

No defense removes all risk. Document what remains. A deployment decision based on this agent should factor in these residual risks.

---

### 4. Suggested Next Controls

For each residual risk class, suggest the control that would close or reduce the gap:

| Residual Risk | Suggested Control | Estimated Effort |
|--------------|-----------------|-----------------|
| [class] | [control] | [low/med/high] |
| [class] | [control] | [low/med/high] |

---

## Checklist

- [ ] Ran `python3 labs/day-13-capstone-attack/eval.py --agent protected`
- [ ] Ran all 5 adaptive attacks and recorded results
- [ ] Ran at least one novel adaptive attack not in the pre-built list
- [ ] ASR table populated (live runs preferred; note if estimated)
- [ ] At least 2 working bypass techniques documented with exact input/response
- [ ] Honest residual risk statement written
- [ ] Next controls table filled in
- [ ] Committed: `docs: add day-13 red-team residual risk report`
