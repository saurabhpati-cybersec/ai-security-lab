// webapp/static/js/range.js
"use strict";

const RangeProgress = {
  key(challengeId) { return `range:${challengeId}`; },
  read(challengeId) {
    try {
      const raw = localStorage.getItem(this.key(challengeId));
      return raw ? JSON.parse(raw) : null;
    } catch (_e) { return null; }
  },
  recordAttempt(challengeId, opts) {
    const prev = this.read(challengeId) || { status: "untouched", attempts: 0, first_clear: null, switchboard_dirty: false };
    const next = {
      status: prev.status,
      attempts: prev.attempts + 1,
      first_clear: prev.first_clear,
      switchboard_dirty: prev.switchboard_dirty || opts.switchboardDirty,
    };
    // A "clear" requires goal_achieved === false (defense won) AND no switchboard.
    if (opts.canonicalRun && opts.goalAchieved === false && next.status !== "cleared") {
      next.status = "cleared";
      next.first_clear = new Date().toISOString();
      // First canonical clear drops the dirty flag.
      next.switchboard_dirty = false;
    } else if (next.status !== "cleared") {
      next.status = "attempted";
    }
    localStorage.setItem(this.key(challengeId), JSON.stringify(next));
    return next;
  },
};

window.RangeHub = {
  async init() {
    const grid = document.getElementById("range-categories");
    grid.innerHTML = "";
    const cats = await fetch("/api/range/categories").then(r => r.json());
    for (const c of cats) {
      const cleared = this.countCleared(c.id);
      const card = document.createElement("a");
      card.href = `/range/${c.id}`;
      card.className = "category-card";
      card.innerHTML = `
        <div class="card-name">${c.name}</div>
        <div class="card-progress">${this.pipString(cleared, 4)}</div>
        <div class="card-meta">${cleared}/${c.level_count} cleared</div>
      `;
      grid.appendChild(card);
    }
  },
  countCleared(category) {
    let n = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith(`range:${category}/L`)) {
        try {
          const v = JSON.parse(localStorage.getItem(k));
          if (v && v.status === "cleared") n++;
        } catch (_e) { /* ignore */ }
      }
    }
    return n;
  },
  pipString(filled, total) {
    let s = "";
    for (let i = 0; i < total; i++) s += i < filled ? "●" : "○";
    return s;
  },
};

window.RangeCategory = {
  async init(category) {
    const data = await fetch(`/api/range/${category}`).then(r => r.json());
    document.getElementById("category-title").textContent = data.name;
    const root = document.getElementById("range-levels");
    root.innerHTML = "";
    for (let level = 0; level < 4; level++) {
      const lvl = data.levels.find(l => l.level === level);
      const prog = RangeProgress.read(`${category}/L${level}`);
      const status = (prog && prog.status) || "untouched";
      const row = document.createElement("a");
      row.href = `/range/${category}/L${level}`;
      row.className = `level-row status-${status}`;
      row.innerHTML = `
        <span class="level-tag">L${level}</span>
        <span class="level-title">${lvl ? lvl.title : "Not yet authored"}</span>
        <span class="level-status">${status}${prog && prog.switchboard_dirty ? " *" : ""}</span>
      `;
      root.appendChild(row);
    }
  },
};

window.RangeChallenge = {
  challenge: null,
  category: null,
  level: null,
  switchboardDirty: false,
  switchboardOverrides: null,

  async init(category, level) {
    this.category = category;
    this.level = level;
    const reveal = level === 3 ? "?reveal=1" : "";
    this.challenge = await fetch(`/api/range/${category}/L${level}${reveal}`).then(r => r.json());

    document.getElementById("challenge-title").textContent =
      `${this.challenge.title} — L${level}`;
    this.renderScenario();
    this.renderHints();
    this.renderDefenses();
    this.renderDiff();
    this.renderFix();
    this.bindAttackButton();
    this.bindTabs();
    this.bindSwitchboardReset();
    this.bindSwitchboardChange();

    // Prefill the payload textarea if the challenge supplies one.
    if (this.challenge.example_payload) {
      document.getElementById("payload-input").value = this.challenge.example_payload;
    }
  },

  renderScenario() {
    const el = document.getElementById("scenario-block");
    el.innerHTML = `
      <div class="scenario-text">${this._md(this.challenge.scenario)}</div>
      <div class="flag-box">🎯 Goal: <strong>${this._escape(this.challenge.flag)}</strong></div>
    `;
  },

  renderHints() {
    const root = document.getElementById("hint-chips");
    root.innerHTML = "";
    this.challenge.hints.forEach((h, i) => {
      const btn = document.createElement("button");
      btn.className = "hint-chip";
      btn.textContent = `Hint ${i + 1}`;
      btn.onclick = () => {
        btn.textContent = h;
        btn.disabled = true;
        btn.classList.add("revealed");
      };
      root.appendChild(btn);
    });
  },

  bindAttackButton() {
    document.getElementById("attack-btn").onclick = () => this.runAttack();
  },

  async runAttack() {
    const payload = document.getElementById("payload-input").value.trim();
    if (!payload) return;
    const btn = document.getElementById("attack-btn");
    btn.disabled = true;
    btn.textContent = "Running…";
    try {
      const body = {
        challenge_id: this.challenge.id,
        payload,
      };
      if (this.switchboardOverrides) {
        body.switchboard = this.switchboardOverrides;
      }
      const result = await fetch("/api/range/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(r => r.json());

      this.renderVerdict(result);
      this.renderTimeline(result.events || []);
      this.highlightFiredDefense(result.fired_layer);

      const canonicalRun = !this.switchboardOverrides;
      RangeProgress.recordAttempt(this.challenge.id, {
        canonicalRun,
        goalAchieved: result.goal_achieved,
        switchboardDirty: this.switchboardDirty && !canonicalRun,
      });
    } catch (e) {
      this.renderVerdict({ error: String(e) });
    } finally {
      btn.disabled = false;
      btn.textContent = "▶ Attack";
    }
  },

  renderVerdict(result) {
    const el = document.getElementById("verdict-banner");
    el.classList.remove("hidden", "verdict-win", "verdict-blocked", "verdict-neutral", "verdict-error");
    if (result.error) {
      el.classList.add("verdict-error");
      el.textContent = `Error: ${result.error}`;
      return;
    }
    if (result.goal_achieved) {
      el.classList.add("verdict-win");
      el.innerHTML = `<strong>✓ GOAL ACHIEVED</strong> · 🛡 detector evaded: ${result.detector_evaded ? "yes" : "no"}`;
    } else if (result.fired_layer) {
      el.classList.add("verdict-blocked");
      el.innerHTML = `<strong>⛔ BLOCKED BY ${this._escape(result.fired_layer)}</strong> · 🛡 detector evaded: no`;
    } else {
      el.classList.add("verdict-neutral");
      el.innerHTML = `· not blocked, goal not achieved · 🛡 detector evaded: ${result.detector_evaded ? "yes" : "no"}`;
    }
  },

  renderTimeline(events) {
    const root = document.getElementById("event-timeline");
    root.innerHTML = "";
    events.forEach(ev => {
      const card = document.createElement("div");
      card.className = `event event-${ev.event_type || "unknown"}`;
      card.innerHTML = `
        <span class="event-type">${this._escape(ev.event_type || "")}</span>
        <span class="event-detail">${this._escape(ev.detector_name || ev.tool_name || "")}</span>
      `;
      root.appendChild(card);
    });
  },

  // Helpers
  _escape(s) { const d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; },
  _md(s) {
    // Minimal markdown: paragraphs + **bold** + `code`. Avoid pulling a dep.
    return this._escape(s)
      .replace(/\n\n+/g, "</p><p>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/^/, "<p>")
      .concat("</p>");
  },
};
