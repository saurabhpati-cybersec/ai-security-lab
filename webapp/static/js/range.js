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
