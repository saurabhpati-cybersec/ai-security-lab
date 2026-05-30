// Shared JS utilities for the ai-security-lab webapp.

export async function apiGet(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
    return r.json();
}

export async function apiPost(path, body) {
    const r = await fetch(path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body || {}),
    });
    if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
    return r.json();
}

let toastStack = null;
function ensureStack() {
    if (toastStack) return toastStack;
    toastStack = document.createElement('div');
    toastStack.className = 'toast-stack';
    document.body.appendChild(toastStack);
    return toastStack;
}

export function toast(msg, kind = 'info', ms = 3200) {
    const stack = ensureStack();
    const t = document.createElement('div');
    t.className = `toast ${kind}`;
    t.innerHTML = msg;
    stack.appendChild(t);
    setTimeout(() => {
        t.classList.add('fade');
        setTimeout(() => t.remove(), 300);
    }, ms);
}

export function skeleton(lines = 3) {
    const out = [];
    for (let i = 0; i < lines; i++) {
        const w = i % 3 === 0 ? '' : (i % 3 === 1 ? 'medium' : 'short');
        out.push(`<div class="skeleton line ${w}"></div>`);
    }
    return out.join('');
}

export function emptyState(icon, title, body, ctaLabel, ctaHref) {
    return `
        <div class="empty-state">
          <div class="icon">${icon}</div>
          <h3>${title}</h3>
          <p>${body}</p>
          ${ctaLabel ? `<a class="btn" href="${ctaHref}">${ctaLabel}</a>` : ''}
        </div>
    `;
}

export function escapeHtml(str) {
    return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// Map a single event into a timeline card
const EVENT_ICONS = {
    model_call: '🧠', tool_call: '🔧', tool_result: '📦',
    detector_hit: '🚨', policy_violation: '⛔',
    human_review_requested: '🙋', final_response: '✅',
};
const EVENT_COLORS = {
    model_call: '#22d3ee', tool_call: '#a78bfa', tool_result: '#94a3b8',
    detector_hit: '#f59e0b', policy_violation: '#ef4444',
    human_review_requested: '#f59e0b', final_response: '#10b981',
};

export function renderEventCard(ev) {
    const sev = ev.severity || null;
    const accent = sev === 'high' ? '#ef4444'
        : sev === 'medium' ? '#f59e0b'
        : EVENT_COLORS[ev.event_type] || '#94a3b8';
    const icon = EVENT_ICONS[ev.event_type] || '•';
    const parts = [];
    if (ev.tool_name) parts.push(`tool=<code>${escapeHtml(ev.tool_name)}</code>`);
    if (ev.detector_name) parts.push(`detector=<code>${escapeHtml(ev.detector_name)}</code>`);
    if (ev.detector_score != null) parts.push(`score=<code>${Number(ev.detector_score).toFixed(2)}</code>`);
    if (ev.model) parts.push(`model=<code>${escapeHtml(ev.model)}</code>`);
    if (ev.tool_result_size) parts.push(`bytes=<code>${ev.tool_result_size}</code>`);
    if (ev.metadata && ev.metadata.reason) parts.push(`reason=<code>${escapeHtml(ev.metadata.reason)}</code>`);
    if (ev.metadata && ev.metadata.matched_rules) {
        const rules = ev.metadata.matched_rules.slice(0, 4).join(', ');
        parts.push(`matched=<code>${escapeHtml(rules)}</code>`);
    }
    if (ev.metadata && ev.metadata.policy_violation) {
        parts.push(`policy=<code>${escapeHtml(ev.metadata.policy_violation)}</code>`);
    }
    const body = parts.length ? `<div class="body">${parts.join(' &middot; ')}</div>` : '';
    const sevPill = sev
        ? `<span class="pill" style="--accent:${accent}">${escapeHtml(sev)}</span>`
        : '';
    return `
        <div class="evt" style="--accent:${accent}">
          <div class="head">
            <span class="icon">${icon}</span>
            <span>${escapeHtml(ev.event_type)}</span>
            ${sevPill}
            <span class="step">step ${ev.step ?? 0}</span>
          </div>
          ${body}
        </div>
    `;
}

export function renderTimeline(events) {
    if (!events || !events.length) return '<div class="banner info">No events captured.</div>';
    return '<div class="timeline">' + events.map(renderEventCard).join('') + '</div>';
}

export function fmtPct(n) {
    if (n == null || Number.isNaN(n)) return '—';
    return (n * 100).toFixed(0) + '%';
}
