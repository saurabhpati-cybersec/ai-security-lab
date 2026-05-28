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
    $thread.innerHTML = '';
    // Rebuild empty state.
    const empty = document.createElement('div');
    empty.className = 'helper-empty';
    empty.innerHTML =
      '<p>Conversation cleared. Select any text on the page and ask about it.</p>';
    $thread.appendChild(empty);
  });

  // ── Form submit (real ask flow comes in Task 11) ────────────────────────
  $form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const q = $input.value.trim();
    if (!q) return;
    // Placeholder — Task 11 replaces this with the SSE ask flow.
    console.log('[helper] would ask:', q);
    $input.value = '';
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
        $input.setSelectionRange($input.value.length, $input.value.length);
        $input.focus();
      }
    });
  }

  // Expose minimal API for the next two tasks.
  window.__helper = { open, close, toggle, history, $input, $thread };
})();
