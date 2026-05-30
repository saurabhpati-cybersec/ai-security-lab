// First-run onboarding tour. Walks new users through key pages.

const TOUR_KEY = 'aisl-tour-seen';

const STEPS = [
    {
        title: 'Welcome to ai-security-lab 👋',
        body: `<p>This is a hands-on lab for AI agent security. You'll build, attack, and defend a tool-using
                LLM agent — every defense ships with a measured number, not just a description.</p>
               <p>This 30-second tour points you to the right starting page.</p>`,
        cta: "Let's go →",
    },
    {
        title: 'Step 1 · Settings ⚙️',
        body: `<p>Add your Anthropic or OpenAI API key on the <strong>Settings</strong> page.
                The key stays on your machine. Click "Validate" to send a 1-token ping and confirm it works.</p>
               <p>You can still explore everything <em>except</em> live agent runs without a key.</p>`,
        cta: 'Open Settings',
        href: '/settings',
    },
    {
        title: 'Step 2 · Attack playground 🥷',
        body: `<p>Pick an example payload (try the <code>Base64 hidden injection</code>) and run it.
                The vulnerable agent will fall for it; the protected agent should block it.</p>
               <p>The animated diagram replays every model call, tool call, and policy violation in order.</p>`,
        cta: 'Open Playground',
        href: '/playground',
    },
    {
        title: 'Step 3 · Detector calibration 🎚️',
        body: `<p>Drag the threshold slider — TPR and FPR recompute live across all six datasets.
                <strong>No API key needed</strong>, runs in milliseconds.</p>
               <p>This is the single best way to feel the TPR/FPR trade-off in your gut.</p>`,
        cta: 'Open Calibration',
        href: '/calibration',
    },
    {
        title: 'Step 4 · Day-by-day walkthrough 📚',
        body: `<p>Each day is interactive: read the brief, try the attack on the vulnerable agent,
                run the same payload through the protected agent, mark the day complete.</p>
               <p>Your progress is saved locally — start with <strong>Day 03</strong>.</p>`,
        cta: 'Open Walkthrough',
        href: '/labs',
    },
];

function render(idx) {
    const step = STEPS[idx];
    const last = idx === STEPS.length - 1;
    const html = `
      <div class="tour-card">
        <div class="tour-progress">
          ${STEPS.map((_, i) => `<div class="tour-dot ${i === idx ? 'active' : ''} ${i < idx ? 'done' : ''}"></div>`).join('')}
        </div>
        <h3>${step.title}</h3>
        <div class="tour-body">${step.body}</div>
        <div class="tour-actions">
          <button class="btn secondary" id="tour-skip">Skip the tour</button>
          <span class="spacer"></span>
          ${idx > 0 ? '<button class="btn secondary" id="tour-prev">← Back</button>' : ''}
          ${step.href
            ? `<a class="btn" href="${step.href}" id="tour-cta">${step.cta}</a>`
            : `<button class="btn" id="tour-cta">${step.cta}</button>`}
        </div>
      </div>
    `;
    document.getElementById('tour-overlay').innerHTML = html;

    document.getElementById('tour-skip').onclick = () => finish();
    if (idx > 0) document.getElementById('tour-prev').onclick = () => render(idx - 1);
    if (!step.href) {
        document.getElementById('tour-cta').onclick = () => {
            if (last) finish();
            else render(idx + 1);
        };
    } else {
        // Clicking a step that links elsewhere also marks the tour seen.
        document.getElementById('tour-cta').onclick = () => finish();
    }
}

function finish() {
    localStorage.setItem(TOUR_KEY, '1');
    const overlay = document.getElementById('tour-overlay');
    if (overlay) overlay.remove();
}

export function maybeStartTour() {
    if (localStorage.getItem(TOUR_KEY)) return;
    const overlay = document.createElement('div');
    overlay.id = 'tour-overlay';
    overlay.className = 'tour-overlay';
    document.body.appendChild(overlay);
    render(0);
}

export function forceStartTour() {
    localStorage.removeItem(TOUR_KEY);
    maybeStartTour();
}
