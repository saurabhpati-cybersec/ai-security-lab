# ai-security-lab — Step-by-step tutorial

This is a 20-minute hands-on tour. Every step is something you click — no terminal commands after launch. By the end you'll have:

- Sent a prompt-injection attack at an LLM agent and watched it succeed
- Sent the same attack at a defended agent and watched the block fire in real time
- Moved a detector threshold to see TPR/FPR trade off live
- Run a full eval over 32 attack cases and seen the ASR delta

---

## Step 0 · Launch (one command, once)

In a terminal at the repo root:

```bash
./launch.sh           # Linux / macOS
launch.bat            # Windows (double-click also works)
```

**What happens:** the launcher checks Python, installs missing dependencies the first time, starts a FastAPI server on port 8000, and opens your browser.

**What you should see:** a browser tab at `http://localhost:8000` showing a dark-themed welcome page with the title "ai-security-lab" in a cyan→purple→red gradient, a banner of metric tiles, and a grid of CTA cards.

**On the LAN?** The launcher binds to `0.0.0.0` by default, so any device on your network can reach `http://<your-machine-ip>:8000`. There is no auth — only do this on a trusted network.

If you'd rather restrict to localhost only:

```bash
HOST=127.0.0.1 ./launch.sh
```

---

## Step 1 · The first-run tour

The first time you load the welcome page, a 5-step **guided tour** modal appears automatically. Click through it; each step previews where you'll go and why. The tour saves its "seen" state in your browser's localStorage so it doesn't re-appear.

**To replay the tour later:** click the **↻ Replay tour** button at the bottom of the left sidebar.

---

## Step 2 · Add an API key (Settings page)

Click **⚙️ Settings** in the sidebar.

**Why first:** the Attack playground, Eval runner, and most Day-walkthrough buttons need a live LLM. The Calibration page, Results history, Tests page, and the Docs work without a key.

1. Paste your `sk-ant-...` key into the **Anthropic** field, or your `sk-...` key into the **OpenAI** field. (Anthropic is preferred; OpenAI is the automatic fallback.)
2. Click **💾 Save**. The key is written to `.env` in the repo root and also set in the running process — no restart needed. A toast appears bottom-right confirming the save.
3. Click **✓ Validate with a 1-token ping**. A one-token request is sent to confirm the key works. The result lands inline: green = good, red = the API rejected it.

**Sidebar feedback:** the green/red dots next to "Anthropic" and "OpenAI" in the sidebar will flip to green once a key is set. If they stay red, the validation step will tell you why.

---

## Step 3 · Run the offline test suite (Tests page)

Click **🧪 Tests** in the sidebar.

Click **▶ Run tests**. The full pytest suite runs in a subprocess on the server and streams its output to the page line-by-line. Each `PASSED` line lights green; `FAILED` lights red.

**Expected result:** `51 passed in ~2s` and a green summary banner.

This is the offline sanity check — confirms the scorers, detectors, message conversion, base64 decode-and-rescan, and compound criteria are all wired correctly. **No API key needed.**

---

## Step 4 · Send your first attack (Attack playground)

Click **🥷 Attack playground** in the sidebar.

1. Click the **📦 Example payloads** dropdown and pick **`Base64 hidden injection (di-010)`**. The textarea fills with a long string ending in base64-encoded text.
2. Make sure both **vulnerable** and **protected** checkboxes are ticked.
3. Click **▶ Run**.

**What you'll see, top to bottom in each column:**

- A **verdict banner**:
  - Vulnerable column: usually `⛔ blocked` if the LLM happens to refuse it, or `⚠ detector hit` if any flags fire. (Without defenses, behaviour is at the model's discretion.)
  - Protected column: `⛔ protected blocked the request — 1 policy violation`. That's the RulesDetector input check firing because the decoded base64 contains `"Ignore all previous instructions"`.
- A **KPI strip** with Tool calls / Detector hits / Policy violations / Events emitted.
- An **animated trust-boundary diagram** that replays the run. Nodes light up in sequence:
  - Cyan glow = active in this step
  - Amber = a detector fired here
  - Red = a policy violation blocked this node
  - Green = the final response landed here
- A **↻ Replay** button on each diagram — click to replay the animation.
- **Hover any node** for a tooltip explaining what it does (RulesDetector, ToolGateway, OutputFilter, web_fetch, etc.).
- A **final response** code block.
- A vertical **event timeline** — each card is severity-coloured with an icon, the tool/detector name, score, and matched rules.

**The key teaching moment:** look at the protected column's timeline. The first event is `🚨 detector_hit` with `score=0.95` and `matched=base64_instruction, decoded:ignore_previous`. The next event is `⛔ policy_violation` with `severity=high`. **Then the LLM is never called** — no `🧠 model_call` event. That's defense-in-depth working.

---

## Step 5 · Move a detector threshold (Calibration)

Click **🎚️ Calibration** in the sidebar.

**No API key needed.** Everything on this page is offline regex evaluation across the 6 datasets.

1. The slider sits at **0.60** by default — the RulesDetector's input-block threshold.
2. Drag the slider left to **0.30**. Watch TPR climb (good) while FPR also climbs (bad — benign requests now get blocked).
3. Drag it right to **0.85**. FPR collapses to 0% but TPR drops to single digits — most attacks now slip through.
4. The **TPR vs FPR curve** below redraws as you drag. The vertical dashed cyan line follows the slider position.
5. The **per-dataset table** shows detection rate per attack class at the current threshold.

**The teaching moment:** there is no single "correct" threshold. You pick the operating point your product can tolerate. The two glossary `(?)` icons next to TPR and FPR explain the trade-off in plain language.

---

## Step 6 · The 14-day walkthrough (Day walkthrough)

Click **📚 Day walkthrough** in the sidebar.

This is where most of the learning happens. The left column lists Day 00 → Day 14 with colour-coded badges:

- `foundation` (grey) — days 00, 01, 02
- `attack` (red) — days 03–07
- `defense` (cyan) — days 08–11
- `capstone` (purple) — days 12, 13, 14

Click **`day-03-direct-injection`**.

**What loads on the right:**

1. **Navigation row** at the top — `← Prev` / `Next →` buttons, the day-type badge, and a `✓ Mark complete` toggle.
2. **📋 Steps for this lab (do these in the GUI)** — an ordered checklist:
   - Step 1: `▶ Try direct injection` — clicking the button deep-links to the Playground with the DAN payload pre-filled and auto-runs against the vulnerable agent.
   - Step 2: `⚖️ Compare both` — same payload, both agents.
   - Step 3: `▶ Try base64 variant` — the di-010 case you already saw.
   - Step 4: `📊 Run eval` — opens the Eval runner with `direct_injection` and `vulnerable` pre-selected.
   - Each step has a checkbox; tick it and the step strikes through.
3. **⚡ Quick actions** — buttons for compare / vulnerable-only / protected-only / full eval. These also use the day's canonical example payload.
4. **📖 Full lab brief (CLI reference)** — collapsed `<details>` containing the original CLI-flavoured README, for completeness.

**Progress tracking:** the sidebar shows `X / 15` and a gradient progress bar. Every time you click **✓ Mark complete** on a day, the bar advances and a green toast appears.

**Try this flow:**
- Pick `day-03-direct-injection`.
- Click step 2's `⚖️ Compare both` button. The Playground loads, both checkboxes are ticked, the textarea is filled, and the run starts automatically.
- When you're done, come back to the day walkthrough and click `✓ Mark complete`.
- Click `Next day →` and you're on day 04.

---

## Step 7 · Run a full eval (Eval runner)

Click **📊 Eval runner** in the sidebar.

1. **Dataset** dropdown — pick `direct_injection` (32 cases, smallest attack dataset).
2. **Agent** dropdown — `vulnerable`.
3. **Max API calls** — start with `20` to keep cost low; raise it later.
4. Click **▶ Run eval**.

**What happens:**

- A new run directory is created under `evals/results/`.
- The eval thread starts running cases. The server tails `cases.jsonl` and streams each completed case to your browser via **Server-Sent Events**.
- The **progress bar** advances; the **cases table** fills in row by row with id / category / passed / latency / tools / error.
- On completion, a summary banner shows **ASR / Passed / Failed / Errors / Runtime**, and a per-category breakdown table is rendered below.

**Now run the same dataset against the protected agent:** repeat with `agent = protected`. The vulnerable run will have a high ASR (attacks succeed); the protected run should have a much lower ASR. That delta is the deliverable.

---

## Step 8 · Diff two runs (Results history)

Click **📁 Results history** in the sidebar.

1. The top table lists every directory in `evals/results/` with a summary. Click any row to inspect that run's full case list.
2. The **Diff two runs** section lets you pick a Left and Right run. Click **↔ Diff**.
3. You'll see three metric tiles — Left ASR, Right ASR, **Delta (in percentage points)**.

**Try it:** diff the vulnerable and protected runs you just made. A `−47 pp` delta is the defense working. A `+0 pp` delta means the defense did nothing — go investigate.

---

## Step 9 · Reference docs (Docs)

Click **📖 Docs** in the sidebar.

A grid of CTA cards, one per reference document:

- **🎯 Threat Model** — T-01..T-17 mapped to STRIDE × OWASP × the lethal trifecta. The four full-trifecta threats (T-05, T-06, T-13, T-14) are the priority list.
- **📖 Glossary** — every term used in the lab (IPI, SSRF, confused deputy, HITL, ATLAS, bootstrap CI, etc.).
- **📊 Honest Assessment** — what's hype vs what's market-valued.
- **✅ Build & Deploy Checklist** — lifecycle checklist for shipping an agent securely.
- **✍️ Secure Prompt Design** — guidance on instruction hierarchy, trust tagging, untrusted-content handling.
- **📝 Incident Report Template** — structured post-incident template with trifecta-legs-active baked in.
- **📈 Learning Tracker** — Day-by-day progress sheet you can fill in as you go.
- **🔗 References** — bibliography with 2025 CVEs (EchoLeak, Invariant MCP, etc.).

Many lab steps deep-link directly here (e.g. Day 01's first step opens the threat model).

---

## Glossary tooltips (everywhere)

Anywhere you see a small **`?`** icon next to a term — ASR, TPR, FPR, IPI, SSRF, trifecta, RulesDetector, ToolGateway, OutputFilter, HITL, classifier, benign — click it to read a one-paragraph definition inline. The definitions live in `webapp/static/js/glossary.js` and are reused across pages.

---

## Toasts and feedback

- **Toasts** stack bottom-right of every page, fade out after ~3 s. Save confirmations, complete-marks, validation results all surface here.
- **Skeletons** (animated grey shimmer) show while data loads. If you see one persist, the API call is slow — check the server log.
- **Empty states** appear with a coaching call-to-action when there's no data yet (e.g. "No runs yet → run your first eval").

---

## Sidebar at a glance

The sidebar persists across every page and shows:

- **Brand + tagline**
- **Nav** with active-state highlighting on the current page
- **Environment block** — green/red dot per provider (Anthropic / OpenAI). Click "Add API key" if neither is set.
- **Progress tracker** — `X / 15` days complete with a gradient bar
- **↻ Replay tour** button — re-launches the first-run guided tour

---

## Stopping the server

In the terminal where `./launch.sh` is running, press **Ctrl+C**. Or, from any other terminal:

```bash
pkill -f "uvicorn webapp.server"
```

The server keeps your `.env` keys intact; you don't need to re-enter them on the next launch.

---

## Recommended path for first-time users

1. Settings → add key + validate
2. Tests → confirm 51 / 51 green
3. Attack playground → run the base64 example with both agents
4. Calibration → drag the slider end to end
5. Day walkthrough → Day 00 first step ("Read the honest assessment") opens the right docs page
6. Day 02 → Day 03 → Day 13 in order
7. Eval runner → run direct_injection on vulnerable and protected, then diff
8. Results history → diff
9. Docs → glossary + threat model as reference

If you get stuck on a term, **every important term has a `(?)` icon nearby** — click for the definition.
