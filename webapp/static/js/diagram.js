// Animated trust-boundary diagram with replay button and node tooltips.

const NODE_INFO = {
    user: ['User input', 'The conversation entry point. Semi-trusted: identity known but content may be crafted.'],
    'input-det': ['RulesDetector (input)', '17 regex rules score 0–1. Confidence ≥ 0.6 blocks at the input layer before the LLM sees it.'],
    llm: ['LLM', 'claude-sonnet-4-5 (Anthropic) or gpt-4.1 (OpenAI fallback). Black-box; trust depends entirely on its context.'],
    gateway: ['ToolGateway', 'Policy layer between LLM and tool execution. Enforces per-tool budgets, SSRF deny list, recipient allowlist, byte caps.'],
    web_fetch: ['web_fetch tool', 'EGRESS leg. Fetches external URLs (8 KB cap). SSRF prevention happens in the gateway, not in the tool itself.'],
    read_doc: ['read_doc tool', 'Reads documents from the RAG corpus. Path traversal blocked at the tool layer. Source of IPI when corpus is poisoned.'],
    send_message: ['send_message tool', 'EGRESS leg. Appends to outbox.jsonl. Default policy: deny all external recipients (empty allowlist).'],
    'output-filter': ['OutputFilter', 'Last line of defense. Strips non-allowlisted markdown image/link URLs and redacts known secret patterns.'],
    response: ['Response', 'Final text returned to the user.'],
};

// Cached env probe — fetched once per page load.
let _activeModelLabel = null;
async function getActiveModelLabel() {
    if (_activeModelLabel !== null) return _activeModelLabel;
    try {
        const r = await fetch('/api/env').then(r => r.json());
        _activeModelLabel = r.has_anthropic ? 'claude-sonnet-4-5'
                          : r.has_openai    ? 'gpt-4.1'
                          : 'no key';
    } catch {
        _activeModelLabel = 'unknown';
    }
    return _activeModelLabel;
}

const SVG_TEMPLATE = (showDefenses, modelLabel) => `
<svg viewBox="0 0 900 360" preserveAspectRatio="xMidYMid meet">
  <defs>
    <marker id="arrow-${showDefenses ? 'p' : 'v'}" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="rgba(148,163,184,0.55)"/>
    </marker>
  </defs>

  <rect class="boundary" x="20" y="20" width="860" height="320" rx="8" />
  <text class="boundary-label" x="34" y="36">trusted perimeter</text>

  <g data-node="user">
    <rect class="node-box" x="40" y="150" width="120" height="56" rx="8"/>
    <text class="node-label" x="100" y="174">User input</text>
    <text class="node-sub"   x="100" y="190">semi-trusted</text>
  </g>

  ${showDefenses ? `
  <g data-node="input-det">
    <rect class="node-box" x="200" y="150" width="120" height="56" rx="8"/>
    <text class="node-label" x="260" y="174">RulesDetector</text>
    <text class="node-sub"   x="260" y="190">input check</text>
  </g>` : ''}

  <g data-node="llm">
    <rect class="node-box" x="370" y="150" width="120" height="56" rx="8"/>
    <text class="node-label" x="430" y="174">LLM</text>
    <text class="node-sub"   x="430" y="190">${modelLabel}</text>
  </g>

  ${showDefenses ? `
  <g data-node="gateway">
    <rect class="node-box" x="540" y="150" width="120" height="56" rx="8"/>
    <text class="node-label" x="600" y="174">ToolGateway</text>
    <text class="node-sub"   x="600" y="190">policies + budgets</text>
  </g>` : ''}

  <g data-node="web_fetch">
    <rect class="node-box" x="710" y="40" width="150" height="56" rx="8"/>
    <text class="node-label" x="785" y="64">web_fetch</text>
    <text class="node-sub"   x="785" y="80">EGRESS · untrusted</text>
  </g>
  <g data-node="read_doc">
    <rect class="node-box" x="710" y="150" width="150" height="56" rx="8"/>
    <text class="node-label" x="785" y="174">read_doc</text>
    <text class="node-sub"   x="785" y="190">RAG corpus · semi</text>
  </g>
  <g data-node="send_message">
    <rect class="node-box" x="710" y="260" width="150" height="56" rx="8"/>
    <text class="node-label" x="785" y="284">send_message</text>
    <text class="node-sub"   x="785" y="300">EGRESS</text>
  </g>

  ${showDefenses ? `
  <g data-node="output-filter">
    <rect class="node-box" x="370" y="260" width="120" height="56" rx="8"/>
    <text class="node-label" x="430" y="284">OutputFilter</text>
    <text class="node-sub"   x="430" y="300">strip exfil</text>
  </g>` : ''}

  <g data-node="response">
    <rect class="node-box" x="200" y="260" width="120" height="56" rx="8"/>
    <text class="node-label" x="260" y="284">Response</text>
    <text class="node-sub"   x="260" y="300">to user</text>
  </g>

  <path class="arrow" d="M160,178 L${showDefenses ? 200 : 370},178" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  ${showDefenses ? `<path class="arrow" d="M320,178 L370,178" marker-end="url(#arrow-p)"/>` : ''}
  <path class="arrow" d="M490,178 L${showDefenses ? 540 : 710},178" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  <path class="arrow" d="M${showDefenses ? 660 : 490},168 L710,68" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  <path class="arrow" d="M${showDefenses ? 660 : 490},178 L710,178" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  <path class="arrow" d="M${showDefenses ? 660 : 490},188 L710,288" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  <path class="arrow" d="M430,206 L430,260" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
  <path class="arrow" d="M${showDefenses ? 370 : 370},288 L320,288" marker-end="url(#arrow-${showDefenses ? 'p' : 'v'})"/>
</svg>
`;

function nodeRect(container, name) {
    const g = container.querySelector(`[data-node="${name}"]`);
    return g ? g.querySelector('rect') : null;
}

function clearStates(container) {
    container.querySelectorAll('.node-box').forEach(el =>
        el.classList.remove('active', 'detected', 'violated', 'success')
    );
}

function flash(rect, cls, ms = 800, sticky = false) {
    if (!rect) return;
    rect.classList.add(cls);
    if (!sticky) {
        setTimeout(() => rect.classList.remove(cls), ms);
    }
}

function attachTooltips(container) {
    let tip = container.querySelector('.svg-tooltip');
    if (!tip) {
        tip = document.createElement('div');
        tip.className = 'svg-tooltip';
        tip.style.display = 'none';
        container.appendChild(tip);
    }
    container.querySelectorAll('[data-node]').forEach(g => {
        const name = g.getAttribute('data-node');
        const info = NODE_INFO[name];
        if (!info) return;
        const rect = g.querySelector('rect');
        rect.addEventListener('mouseenter', (e) => {
            const r = container.getBoundingClientRect();
            const ge = g.getBoundingClientRect();
            tip.innerHTML = `<div class="t-title">${info[0]}</div>${info[1]}`;
            tip.style.left = (ge.left - r.left) + 'px';
            tip.style.top = (ge.bottom - r.top + 4) + 'px';
            tip.style.display = 'block';
        });
        rect.addEventListener('mouseleave', () => tip.style.display = 'none');
    });
}

function buildScript(events, showDefenses) {
    // Convert events into a step list of {node, cls, sticky?} actions.
    const steps = [];
    let firstModelCall = true;
    for (const ev of events) {
        switch (ev.event_type) {
            case 'model_call':
                if (showDefenses && firstModelCall) {
                    steps.push({ node: 'input-det', cls: 'active' });
                    firstModelCall = false;
                }
                steps.push({ node: 'llm', cls: 'active' });
                break;
            case 'tool_call':
                if (showDefenses) steps.push({ node: 'gateway', cls: 'active' });
                if (ev.tool_name) steps.push({ node: ev.tool_name, cls: 'active' });
                break;
            case 'tool_result':
                if (ev.tool_name) steps.push({ node: ev.tool_name, cls: 'active', ms: 400 });
                break;
            case 'detector_hit':
                if (ev.detector_name === 'OutputFilter') steps.push({ node: 'output-filter', cls: 'detected' });
                else steps.push({ node: 'input-det', cls: 'detected' });
                break;
            case 'policy_violation':
                steps.push({ node: showDefenses ? 'gateway' : 'input-det', cls: 'violated', sticky: true });
                if (ev.tool_name) steps.push({ node: ev.tool_name, cls: 'violated', sticky: true });
                break;
            case 'final_response':
                if (showDefenses) steps.push({ node: 'output-filter', cls: 'success', sticky: true });
                steps.push({ node: 'response', cls: 'success', sticky: true });
                break;
        }
    }
    return steps;
}

function play(container, steps) {
    clearStates(container);
    let i = 0;
    function tick() {
        if (i >= steps.length) return;
        const s = steps[i++];
        flash(nodeRect(container, s.node), s.cls, s.ms || 800, s.sticky || false);
        setTimeout(tick, 550);
    }
    tick();
}

export async function renderDiagram(container, events, variant) {
    const showDefenses = variant === 'protected';
    const steps = buildScript(events, showDefenses);
    const modelLabel = await getActiveModelLabel();

    container.innerHTML = `
        <div class="diagram-controls">
            <button class="btn secondary" data-action="replay">↻ Replay</button>
            <span class="muted" style="font-size:11px;">${steps.length} steps · hover any node for details</span>
        </div>
        ${SVG_TEMPLATE(showDefenses, modelLabel)}
        <div class="diagram-legend">
          <span class="legend-ok">active</span>
          <span class="legend-hit">detector hit</span>
          <span class="legend-block">blocked</span>
          <span class="legend-done">final</span>
        </div>
    `;
    container.style.position = 'relative';
    attachTooltips(container);

    container.querySelector('[data-action="replay"]').onclick = () => play(container, steps);

    setTimeout(() => play(container, steps), 200);
}
