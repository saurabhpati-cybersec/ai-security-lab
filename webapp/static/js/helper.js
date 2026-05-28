// On-screen helper: docked right-hand panel for asking about page content.
//
// This file is split across three tasks:
//   Task 9  — toggle, hotkey, empty state, suggestions   (this file's initial form)
//   Task 10 — selection pill + auto-fill on select
//   Task 11 — ask flow (SSE consumer, message rendering, citation chips)
//
// Vanilla JS, no framework. All DOM IDs come from _helper.html.

(function () {
  'use strict';

  // ── DOM refs ────────────────────────────────────────────────────────────
  const $toggle = document.getElementById('helper-toggle');
  const $panel = document.getElementById('helper-panel');
  const $close = document.getElementById('helper-close');
  const $clear = document.getElementById('helper-clear');
  const $thread = document.getElementById('helper-thread');
  const $form = document.getElementById('helper-form');
  const $input = document.getElementById('helper-input');

  if (!$toggle || !$panel || !$form || !$input) return; // panel not on this page

  // ── State ───────────────────────────────────────────────────────────────
  /** Conversation history sent to the backend. role: 'user'|'assistant', content: str. */
  const history = [];
  /** Most-recent selection text auto-filled into the input. Cleared on submit. */
  let pendingSelection = null;

  // ── Panel open/close ────────────────────────────────────────────────────
  function open() {
    $panel.hidden = false;
    $panel.setAttribute('aria-hidden', 'false');
    $toggle.setAttribute('aria-expanded', 'true');
    setTimeout(() => $input.focus(), 0);
  }
  function close() {
    $panel.hidden = true;
    $panel.setAttribute('aria-hidden', 'true');
    $toggle.setAttribute('aria-expanded', 'false');
  }
  function toggle() { $panel.hidden ? open() : close(); }

  $toggle.addEventListener('click', toggle);
  $close.addEventListener('click', close);

  // ── Hotkeys ─────────────────────────────────────────────────────────────
  document.addEventListener('keydown', (ev) => {
    // Don't fire when the user is typing in an input/textarea/contenteditable.
    const tgt = ev.target;
    const isTyping = tgt && (
      tgt.tagName === 'INPUT' ||
      tgt.tagName === 'TEXTAREA' ||
      (tgt.isContentEditable === true)
    );
    if (ev.key === '?' && !isTyping && !ev.metaKey && !ev.ctrlKey) {
      ev.preventDefault();
      toggle();
    } else if (ev.key === 'Escape' && !$panel.hidden) {
      ev.preventDefault();
      close();
    }
  });

  // ── Empty state suggestions ─────────────────────────────────────────────
  document.querySelectorAll('.helper-suggestion').forEach((btn) => {
    btn.addEventListener('click', () => {
      $input.value = btn.textContent.trim();
      $input.focus();
    });
  });

  // ── Clear conversation ──────────────────────────────────────────────────
  $clear.addEventListener('click', () => {
    history.length = 0;
    pendingSelection = null;
    $thread.innerHTML = '';
    // Rebuild empty state.
    const empty = document.createElement('div');
    empty.className = 'helper-empty';
    empty.innerHTML =
      '<p>Conversation cleared. Select any text on the page and ask about it.</p>';
    $thread.appendChild(empty);
  });

  // ── Markdown-lite rendering (citations + code + bold + links) ───────────
  // We do NOT pull in a full markdown library — keep the helper light.
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }
  function renderMarkdownLite(text, citationsMap) {
    let html = escapeHtml(text);
    // Inline code first to avoid stomping on its content.
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Bold.
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Quoted lines.
    html = html.replace(/(^|\n)&gt; ([^\n]+)/g, '$1<blockquote>$2</blockquote>');
    // Citations: [1], [2] → chips (clickable iff the server returned a url).
    html = html.replace(/\[(\d+)\]/g, (m, n) => {
      const cite = citationsMap[Number(n)];
      if (!cite) return m;
      const tip = escapeHtml(cite.path) + (cite.heading ? ' — ' + escapeHtml(cite.heading) : '');
      if (cite.url) {
        return `<a class="helper-citation" href="${cite.url}" target="_blank" rel="noopener" title="${tip}">${n}</a>`;
      }
      // No rendered route for this corpus path — render a non-clickable chip with a tooltip.
      return `<span class="helper-citation" title="${tip}">${n}</span>`;
    });
    // Paragraph breaks.
    html = html.replace(/\n\n+/g, '</p><p>');
    return '<p>' + html + '</p>';
  }

  // ── Message rendering ───────────────────────────────────────────────────
  function clearEmptyState() {
    const empty = $thread.querySelector('.helper-empty');
    if (empty) empty.remove();
  }
  function appendUserBubble(content) {
    clearEmptyState();
    const node = document.createElement('div');
    node.className = 'helper-msg helper-msg-user';
    node.innerHTML = renderMarkdownLite(content, {});
    $thread.appendChild(node);
    $thread.scrollTop = $thread.scrollHeight;
  }
  function appendAssistantBubble() {
    const node = document.createElement('div');
    node.className = 'helper-msg helper-msg-assistant';
    node.innerHTML = '<p class="helper-streaming">…</p>';
    $thread.appendChild(node);
    $thread.scrollTop = $thread.scrollHeight;
    return node;
  }

  // ── SSE ask flow ────────────────────────────────────────────────────────
  let inFlight = null; // AbortController of the current request, if any

  async function ask(question, selection) {
    if (inFlight) inFlight.abort();
    inFlight = new AbortController();

    appendUserBubble(question);
    history.push({ role: 'user', content: question });

    const bubble = appendAssistantBubble();
    let buffer = '';
    let citationsMap = {};

    function rerender() {
      bubble.innerHTML = renderMarkdownLite(buffer, citationsMap);
      $thread.scrollTop = $thread.scrollHeight;
    }
    function showWarning(message) {
      bubble.innerHTML = `<div class="helper-warn">${escapeHtml(message)}</div>` +
                         '<p class="helper-streaming">…</p>';
    }

    try {
      const resp = await fetch('/api/helper/ask', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          question,
          selection: selection, // raw selection text — server runs the lab's RulesDetector on it
          page: window.location.pathname,
          history: history.slice(0, -1), // exclude the just-pushed user turn
        }),
        signal: inFlight.signal,
      });
      if (!resp.ok || !resp.body) {
        showWarning(`Request failed: ${resp.status} ${resp.statusText}`);
        return;
      }

      // Stream the SSE body.
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let pending = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        pending += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = pending.indexOf('\n\n')) >= 0) {
          const raw = pending.slice(0, idx);
          pending = pending.slice(idx + 2);
          const lines = raw.split('\n');
          let event = 'message';
          let data = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            else if (line.startsWith('data:')) data += line.slice(5).trim();
          }
          let payload;
          try { payload = JSON.parse(data); } catch { payload = {}; }
          if (event === 'citations') {
            (payload.citations || []).forEach((c) => { citationsMap[c.n] = c; });
          } else if (event === 'token') {
            buffer += payload.delta || '';
            rerender();
          } else if (event === 'done') {
            // Final render strips the streaming cursor.
            rerender();
            history.push({ role: 'assistant', content: buffer });
          } else if (event === 'error') {
            showWarning(payload.message || 'Helper failed.');
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        showWarning(String(err));
      }
    } finally {
      inFlight = null;
    }
  }

  $form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const q = $input.value.trim();
    if (!q) return;
    const sel = pendingSelection;
    pendingSelection = null;
    $input.value = '';
    ask(q, sel);
  });

  // ── Selection handling: pill + auto-fill ────────────────────────────────
  const $pill = document.getElementById('helper-pill');
  let lastSelectionText = '';

  function clearPill() {
    if ($pill) { $pill.hidden = true; }
  }

  function positionPillNearSelection(range) {
    if (!$pill) return;
    const rect = range.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) { clearPill(); return; }
    // Place the pill just above the top-right of the selection, on top of the page.
    const top = window.scrollY + rect.top - 32;
    const left = window.scrollX + rect.right - 110;
    $pill.style.top = Math.max(window.scrollY + 8, top) + 'px';
    $pill.style.left = Math.max(8, left) + 'px';
    $pill.hidden = false;
  }

  function onSelectionChange() {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
      clearPill();
      lastSelectionText = '';
      return;
    }
    const text = sel.toString().trim();
    if (!text || text.length < 2) {
      clearPill();
      lastSelectionText = '';
      return;
    }
    // Don't fire when the selection is inside the helper itself.
    const range = sel.getRangeAt(0);
    if ($panel.contains(range.startContainer) || $panel.contains(range.endContainer)) {
      clearPill();
      return;
    }
    lastSelectionText = text;
    if ($panel.hidden) {
      // Panel closed — show the pill near the selection.
      positionPillNearSelection(range);
    } else {
      // Panel open — auto-fill the input with the quoted selection.
      clearPill();
      const quoted = text.split('\n').map((l) => '> ' + l).join('\n');
      $input.value = quoted + '\n\n';
      pendingSelection = text;
      $input.focus();
      // Move caret to the end.
      $input.setSelectionRange($input.value.length, $input.value.length);
    }
  }

  document.addEventListener('selectionchange', onSelectionChange);
  // Hide pill on scroll (cheap — selection bbox would be stale anyway).
  window.addEventListener('scroll', clearPill, { passive: true });

  if ($pill) {
    $pill.addEventListener('mousedown', (ev) => {
      // Prevent the click from clearing the selection before we read it.
      ev.preventDefault();
    });
    $pill.addEventListener('click', () => {
      const text = lastSelectionText;
      clearPill();
      open();
      if (text) {
        const quoted = text.split('\n').map((l) => '> ' + l).join('\n');
        $input.value = quoted + '\n\n';
        pendingSelection = text;
        $input.setSelectionRange($input.value.length, $input.value.length);
        $input.focus();
      }
    });
  }

  // Expose minimal API for the next two tasks.
  window.__helper = { open, close, toggle, history, $input, $thread };
})();
