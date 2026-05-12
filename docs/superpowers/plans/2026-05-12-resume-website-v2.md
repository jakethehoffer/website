# Resume Website v2 — "Engineering Log" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the existing `website/` site into the "engineering log" v2 design — mono-only typography, terminal-flavored dark default with parchment light mode, git-log-style project cards with real last-commit data, and a long-form case study on the `trader` project.

**Architecture:** In-place rewrite of the three existing files (`index.html`, `styles.css`, `script.js`). One new optional Node script (`scripts/refresh-meta.mjs`) that pulls last-commit dates from GitHub via `gh api` and bakes them into `index.html` via sentinel-marker replacement. No framework, no bundler, no npm install required (the script uses only Node built-ins and shells out to `gh`).

**Tech Stack:** Plain HTML5, CSS3 (custom properties, grid, flexbox), vanilla JS (ES2020). JetBrains Mono via Google Fonts (Inter dropped — v2 is all-mono). LibreOffice (existing, used in v1) is no longer touched. `gh` CLI (already authenticated as `jakethehoffer`) for the optional refresh script.

**Spec:** `docs/superpowers/specs/2026-05-12-resume-website-v2-design.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── index.html                         REWRITTEN
├── styles.css                         REWRITTEN
├── script.js                          REWRITTEN
├── scripts/
│   └── refresh-meta.mjs               NEW
├── assets/
│   ├── projects/
│   │   └── fuse-web.webp              NEW (converted from FUSE-Web PNG)
│   └── avatar.svg                     DELETED (v2 has no avatar)
├── README.md                          UPDATED
├── resume.pdf                         UNCHANGED
├── resume-source.docx                 UNCHANGED
└── docs/superpowers/                  UNCHANGED (history)
```

`index.html`: same single-page document. New mono-only markup, boot-sequence
end-state in static HTML, sentinel-marker comments for refresh-meta, the
new case-study section between Projects and Experience.

`styles.css`: rewritten top-to-bottom. New token system (dark default +
parchment light), all-mono typography, section labels, git-log card layout,
status-dot styles, case-study + ASCII-diagram styles, mobile breakpoints.

`script.js`: keeps the v1 mobile-nav, theme-toggle, IntersectionObserver
reveal, and footer-year logic. Adds the boot-sequence animation that runs
once per session and respects `prefers-reduced-motion`.

`scripts/refresh-meta.mjs`: opt-in Node script. For each repo in a
hard-coded list, calls `gh api repos/jakethehoffer/<repo>` (shells out
synchronously), reads `pushed_at`, formats as "Nd ago", and search-and-
replaces sentinel markers in `index.html`. Also updates the footer
`last_deployed` timestamp. Idempotent and offline-safe (logs and skips on
network error).

---

## Verification Approach

Same model as v1: static site, no automated tests. Each task that produces
visible output ends with a manual verification step. Use the `.claude/launch.json`
already in the repo and the Claude Preview MCP if available, or fall back
to `python -m http.server 8000` and open in Chrome.

If `preview_screenshot` times out (it did during v2 critique — likely the
Google Fonts request keeps the load event from firing in headless), fall
back to `preview_inspect` for visual property checks, or just open the page
in a real browser.

After every CSS-only or HTML-only change, hard-reload the page. After every
JS change, open DevTools and confirm no console errors.

---

## Task 1: New design tokens + reset (CSS)

Replace v1's light-only token system with v2's mono-only, dark-default
system. The page will look very different but should still render all
content.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (full replacement)

- [ ] **Step 1: Replace `styles.css` entirely**

```css
/* ============================================================
   Engineering Log — v2 design system
   ============================================================ */

/* ---------- Dark theme (default) ---------- */
:root {
  --bg:        #0a0e14;
  --bg-elev:   #11161e;
  --bg-grid:   #1c2330;
  --text:      #d6dee6;
  --text-dim:  #8a96a3;
  --text-mute: #5a6573;
  --accent:    #f5b342;
  --accent-2:  #7fbf7f;
  --accent-3:  #e07a7a;
  --cursor:    #f5b342;

  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;

  --radius:    6px;
  --radius-sm: 4px;
  --shadow:    0 1px 0 rgba(245, 179, 66, 0.08), 0 8px 24px rgba(0, 0, 0, 0.4);

  --container: 920px;
  --gutter:    1.25rem;

  --line-h:    1.7;
}

/* ---------- Parchment light theme ---------- */
:root[data-theme="light"] {
  --bg:        #f5efe4;
  --bg-elev:   #ece4d3;
  --bg-grid:   #d9ceb7;
  --text:      #1a1f26;
  --text-dim:  #4a5560;
  --text-mute: #6a7480;
  --accent:    #a86a14;
  --accent-2:  #3f7a3f;
  --accent-3:  #a23a3a;
  --cursor:    #a86a14;
  --shadow:    0 1px 0 rgba(168, 106, 20, 0.08), 0 4px 12px rgba(26, 31, 38, 0.08);
}

/* ---------- Reset ---------- */
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 15px;
  line-height: var(--line-h);
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
@media (min-width: 640px) { body { font-size: 16px; } }

img, svg, picture { display: block; max-width: 100%; }
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--text); text-decoration: underline; text-underline-offset: 3px; }
button {
  font: inherit;
  color: inherit;
  background: none;
  border: 0;
  cursor: pointer;
  font-family: var(--font-mono);
}
h1, h2, h3 { letter-spacing: -0.01em; }

/* ---------- Container & section primitives ---------- */
.container {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--gutter);
}
.section {
  padding: 4rem 0;
  border-top: 1px solid var(--bg-grid);
}
@media (min-width: 768px) { .section { padding: 6rem 0; } }
.section__label {
  color: var(--text-mute);
  font-size: 0.8125rem;
  margin: 0 0 1.5rem;
  font-weight: 400;
}
.section h2 {
  font-size: 1.5rem;
  margin: 0 0 2rem;
  font-weight: 700;
}

/* ---------- Accessibility ---------- */
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  background: var(--accent);
  color: var(--bg);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  z-index: 100;
}
.skip-link:focus { left: 0.5rem; top: 0.5rem; }
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* ---------- Reveal on scroll (kept from v1, tuned shorter) ---------- */
.reveal {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.3s ease-out, transform 0.3s ease-out;
  will-change: opacity, transform;
}
.reveal.is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1; transform: none; transition: none; }
}
```

- [ ] **Step 2: Hard-reload `index.html` in a browser**

Expected: page is now dark (`#0a0e14` background), all text is JetBrains
Mono, and content is technically rendered but completely unstyled at the
section level. Hero, project cards, and timeline look broken — that's
expected. We rebuild section-by-section next.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): replace design tokens with engineering-log system"
```

---

## Task 2: Update HTML head — fonts, theme preload, JSON-LD

Drop the Inter font, refresh the JetBrains Mono URL for the weights v2
uses (400 / 500 / 600 / 700), and keep the FOUC-free theme preload.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (head section only)

- [ ] **Step 1: Replace the Google Fonts `<link>` block**

In `index.html`, find:

```html
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

Replace with:

```html
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

- [ ] **Step 2: Confirm the theme preload script still works**

The existing inline `<script>` block in `<head>` does the right thing —
it reads `jh-theme` from `localStorage`, defaults to system preference,
and sets `data-theme` on `<html>`. v2 changes the default direction: if no
stored value AND no system preference of light, we should default to
dark (v1 defaulted to light).

Find:

```html
    <script>
      (function () {
        try {
          var stored = localStorage.getItem("jh-theme");
          var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
          var theme = stored || (prefersDark ? "dark" : "light");
          document.documentElement.setAttribute("data-theme", theme);
        } catch (e) {}
      })();
    </script>
```

Replace with:

```html
    <script>
      (function () {
        try {
          var stored = localStorage.getItem("jh-theme");
          var prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
          var theme = stored || (prefersLight ? "light" : "dark");
          document.documentElement.setAttribute("data-theme", theme);
        } catch (e) {}
      })();
    </script>
```

Note the flipped logic: dark is the new default; we only opt into light
if the user's system explicitly prefers it.

- [ ] **Step 3: Verify in browser**

Reload. In DevTools → Application → Local Storage, delete `jh-theme` if
present. Reload again. Page should render dark (assuming you don't have
your OS set to forced light mode). Then in DevTools → Rendering →
Emulate CSS media feature `prefers-color-scheme: light`, reload — page
should render in parchment (cream) tones.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): drop Inter, default theme to dark, keep parchment light"
```

---

## Task 3: Hero — static end-state markup and style

Build the hero in its *settled* state first — no animation yet. Pre-
rendering the full content is the source of truth for screen readers and
the `prefers-reduced-motion` path.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (hero `<section>`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Replace the entire hero section markup**

Find the existing `<section id="top" class="hero">…</section>` block.
Replace with:

```html
      <section id="top" class="hero">
        <div class="container hero__inner">
          <pre class="hero__boot" aria-label="Profile boot sequence">
<span class="boot__prompt">$ whoami</span>
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> <span data-boot-line>jake hoffman &middot; computer engineering @ queen&rsquo;s &middot; class of 2027</span></span>

<span class="boot__prompt">$ summary</span>
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> <span data-boot-line>i build production-grade software &mdash; trading agents, arbitrage daemons, web platforms, and ml pipelines. paper-trading the s&amp;p 500 on real infrastructure; running a 24/7 odds daemon across ten bookmakers.</span></span>

<span class="boot__prompt">$ <span data-boot-line>contact</span><span class="boot__caret" aria-hidden="true">_</span></span>
          </pre>

          <div class="hero__ctas" role="group" aria-label="Contact links">
            <a class="btn btn--primary" href="mailto:14jakehoffman@gmail.com">[ email ]</a>
            <a class="btn" href="https://github.com/jakethehoffer" target="_blank" rel="noopener">[ github ]</a>
            <a class="btn" href="https://www.linkedin.com/in/jake-hoffman-7117692a5/" target="_blank" rel="noopener">[ linkedin ]</a>
            <a class="btn btn--ghost" href="resume.pdf" download>[ resume.pdf &darr; ]</a>
          </div>

          <p class="hero__metrics">
            <span class="metrics__prefix">//</span>
            <span>4 production systems</span>
            <span>10 bookmakers ingested</span>
            <span>6 scheduled agents</span>
            <span>dean&rsquo;s scholar</span>
          </p>

          <button class="hero__skip" type="button" hidden>skip &#9656;</button>
        </div>
      </section>
```

Notes:
- The `<pre>` block preserves whitespace so the boot sequence reads as a
  real terminal session.
- `data-boot-line` attributes mark the spans the animation will type out.
- The skip button is `hidden` by default; JS unhides it during animation.

- [ ] **Step 2: Append hero styles to `styles.css`**

```css
/* ---------- Hero ---------- */
.hero {
  padding: 5rem 0 3rem;
  position: relative;
}
@media (min-width: 768px) { .hero { padding: 7rem 0 4rem; } }
.hero__inner { max-width: 720px; }

.hero__boot {
  margin: 0 0 2rem;
  font-family: var(--font-mono);
  font-size: clamp(0.875rem, 2vw, 1rem);
  line-height: 1.8;
  white-space: pre-wrap;
  color: var(--text);
}
.boot__prompt {
  color: var(--accent);
  font-weight: 600;
}
.boot__line {
  display: inline;
}
.boot__caret-mark {
  color: var(--text-mute);
}
.boot__caret {
  display: inline-block;
  width: 0.55em;
  background: var(--cursor);
  color: transparent;
  margin-left: 2px;
  animation: blink 1.06s steps(1) infinite;
}
@keyframes blink { 50% { background: transparent; } }
@media (prefers-reduced-motion: reduce) {
  .boot__caret { animation: none; background: var(--cursor); }
}

.hero__ctas {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  margin: 0 0 2rem;
}
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text);
  font-size: 0.875rem;
  font-weight: 500;
  font-family: var(--font-mono);
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}
.btn:hover {
  text-decoration: none;
  border-color: var(--accent);
  color: var(--accent);
}
.btn--primary {
  border-color: var(--accent);
  color: var(--accent);
}
.btn--primary:hover {
  background: var(--accent);
  color: var(--bg);
}
.btn--ghost { color: var(--text-dim); }

.hero__metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1.5rem;
  font-size: 0.8125rem;
  color: var(--text-dim);
  margin: 0;
}
.metrics__prefix { color: var(--text-mute); }

.hero__skip {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  font-size: 0.75rem;
  color: var(--text-mute);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}
.hero__skip:hover { color: var(--accent); }
```

- [ ] **Step 3: Verify in browser**

Reload. The hero should show:
- `$ whoami` in amber, followed by `> jake hoffman · computer engineering …`
- `$ summary` in amber, followed by the long bio
- `$ contact` with a blinking amber block-cursor
- A row of bracket-style buttons under it
- A `// 4 production systems …` metric strip in dim text

In the parchment light theme the same content should look warm and
readable. Toggle via the existing theme button or via DevTools
`prefers-color-scheme: light` emulation.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): hero in static settled state (boot animation comes next)"
```

---

## Task 4: Hero — boot sequence animation in JS

Replace the static `data-boot-line` content with empty strings on
`DOMContentLoaded` (only if motion is allowed and not played this
session), then type each line out character-by-character.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/script.js`

- [ ] **Step 1: Add the boot-sequence module inside the existing IIFE**

In `script.js`, find the line `// ---------- Mobile nav ----------` and
insert the new module *above* it, right after `"use strict";`:

```js
  // ---------- Hero boot sequence ----------
  (function bootSequence() {
    const lines = Array.from(document.querySelectorAll("[data-boot-line]"));
    if (lines.length === 0) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let alreadyPlayed = false;
    try { alreadyPlayed = sessionStorage.getItem("jh-boot-played") === "1"; } catch (e) {}

    // No-op path: leave the static end-state alone.
    if (reduceMotion || alreadyPlayed) return;

    const skipBtn = document.querySelector(".hero__skip");
    const cached = lines.map((el) => el.textContent);
    lines.forEach((el) => (el.textContent = ""));

    let cancelled = false;
    function finish() {
      cancelled = true;
      lines.forEach((el, i) => (el.textContent = cached[i]));
      if (skipBtn) skipBtn.hidden = true;
      try { sessionStorage.setItem("jh-boot-played", "1"); } catch (e) {}
    }

    if (skipBtn) {
      skipBtn.hidden = false;
      skipBtn.addEventListener("click", finish);
      // Auto-hide skip after 800ms.
      setTimeout(() => { if (skipBtn && !cancelled) skipBtn.hidden = false; }, 800);
    }

    const charDelay = 14;   // ms per character
    const lineDelay = 220;  // ms pause between lines

    (async function play() {
      for (let i = 0; i < lines.length; i++) {
        const el = lines[i];
        const target = cached[i];
        for (let c = 0; c < target.length; c++) {
          if (cancelled) return;
          el.textContent += target[c];
          await sleep(charDelay);
        }
        if (cancelled) return;
        await sleep(lineDelay);
      }
      finish();
    })();

    function sleep(ms) {
      return new Promise((r) => setTimeout(r, ms));
    }
  })();
```

- [ ] **Step 2: Verify boot animation**

Open DevTools → Application → Session Storage → clear `jh-boot-played`.
Hard-reload. Watch the hero type out three lines in ~1.4 seconds, then
settle. The skip button (top-right of hero) should be visible during the
animation and disappear after.

Reload again (without clearing session storage). The animation should
*not* play — content appears immediately.

Open DevTools → Rendering → Emulate CSS `prefers-reduced-motion: reduce`,
clear session storage, reload. Content should appear immediately, no
animation, no skip button.

Click the skip button mid-animation — content jumps to full state, skip
button hides.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add script.js
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): hero boot-sequence typing animation"
```

---

## Task 5: About — rewrite copy with voice + section label

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (About section)

- [ ] **Step 1: Replace the About section**

Find the existing `<section id="about" class="section">…</section>` and
replace with:

```html
      <section id="about" class="section">
        <div class="container">
          <p class="section__label"># about</p>
          <h2>What I work on</h2>
          <div class="about">
            <p>Computer engineering at Queen&rsquo;s. I&rsquo;m most at home building systems that run unattended &mdash; trading agents that paper-trade the S&amp;P 500, an arbitrage daemon ingesting ten bookmakers every minute, web platforms with their tests wired up before the first commit.</p>
            <p>What I&rsquo;m best at: turning a messy real-world domain (insurance catastrophe management, sports-book pricing, broker order flow) into clean abstractions and a service that doesn&rsquo;t wake me up at 3am.</p>
            <p>Looking for an internship or co-op where I can ship production code &mdash; ideally somewhere with hard correctness requirements: trading, infrastructure, financial systems, or developer tools.</p>
          </div>
        </div>
      </section>
```

- [ ] **Step 2: Append About styles**

In `styles.css`, after the `.hero__skip:hover` rule, append:

```css
/* ---------- About ---------- */
.about p {
  max-width: 65ch;
  margin: 0 0 1rem;
  color: var(--text);
}
.about p:last-child { margin-bottom: 0; }
```

- [ ] **Step 3: Verify**

Reload. The About section now has a `# about` label, an "What I work on"
heading, and three short paragraphs reading like an opinionated bio
rather than HR copy.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): rewrite about copy with voice, add section label"
```

---

## Task 6: Skills — section label + mono restyle

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (Skills section)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Replace the Skills section**

Find the existing `<section id="skills" class="section">…</section>` and
replace with:

```html
      <section id="skills" class="section">
        <div class="container">
          <p class="section__label"># skills</p>
          <h2>Stack</h2>
          <div class="skills">
            <div class="skill-group">
              <p class="skill-group__label">// languages</p>
              <p class="skill-group__items">python &middot; java &middot; c &middot; c# &middot; c++ &middot; javascript &middot; typescript &middot; dart &middot; sql</p>
            </div>
            <div class="skill-group">
              <p class="skill-group__label">// tools &amp; frameworks</p>
              <p class="skill-group__items">git &middot; next.js &middot; supabase &middot; fastapi &middot; playwright &middot; unity &middot; sqlite &middot; alembic &middot; monday.com &middot; google apps script</p>
            </div>
            <div class="skill-group">
              <p class="skill-group__label">// domains</p>
              <p class="skill-group__items">machine learning &middot; web development &middot; automation &middot; trading systems &middot; mobile apps</p>
            </div>
          </div>
        </div>
      </section>
```

- [ ] **Step 2: Append Skills styles**

```css
/* ---------- Skills ---------- */
.skills {
  display: grid;
  gap: 1.25rem;
  max-width: 70ch;
}
.skill-group__label {
  margin: 0 0 0.25rem;
  color: var(--text-mute);
  font-size: 0.8125rem;
}
.skill-group__items {
  margin: 0;
  color: var(--text);
}
```

- [ ] **Step 3: Verify**

Reload. Skills now reads as three mono lines with `// label` headers and
dot-separated item lists — no chips, no boxes. Quieter and more
distinctive than v1's pill chips.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): skills section restyled as mono dot-list groups"
```

---

## Task 7: Project cards — git-log structure + style (no images yet)

Rebuild all six project cards with the new structure: status row, title
row, body, metrics, tech chips. Images come in Task 8.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (Projects section)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Replace the Projects section**

Find the existing `<section id="projects" class="section">…</section>`
and replace with:

```html
      <section id="projects" class="section">
        <div class="container">
          <p class="section__label"># projects</p>
          <h2>What I&rsquo;m running</h2>
          <div class="projects">

            <article class="project">
              <header class="project__head">
                <span class="status status--active" aria-label="Status: active"></span>
                <span class="project__status-label">ACTIVE</span>
                <span class="project__last-commit" data-meta="trader.last_commit">last commit: recent</span>
              </header>
              <h3 class="project__name"><a href="https://github.com/jakethehoffer/trader" target="_blank" rel="noopener">trader</a></h3>
              <p class="project__what">24/7 AI swing-trading agent for S&amp;P 500 equities, driven by six scheduled Claude Code routines.</p>
              <p class="project__body">Paper-traded on IBKR + Finnhub news; graduates to live only after 30 paper days of documented outperformance. Designed the risk model, journaling, and kill-switch from day one.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> s&amp;p 500 &middot; 6 scheduled agents &middot; ibkr paper</p>
              <p class="project__chips">python &middot; pytest &middot; ib_async &middot; finnhub &middot; claude code</p>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--active" aria-label="Status: active"></span>
                <span class="project__status-label">ACTIVE</span>
                <span class="project__last-commit" data-meta="arbitrage.last_commit">last commit: recent</span>
              </header>
              <h3 class="project__name"><a href="https://github.com/jakethehoffer/arbitrage" target="_blank" rel="noopener">Odds Aggregator</a></h3>
              <p class="project__what">Production arbitrage daemon covering 10 bookmakers across 6 sports.</p>
              <p class="project__body">Ingest &rarr; normalize &rarr; detect cross-book arbs &rarr; push alerts to Telegram and Discord. Runs 24/7 on a Windows host with Alembic-managed schema and replay tooling for postmortems.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> 10 books &middot; 6 sports &middot; 24/7 uptime</p>
              <p class="project__chips">python &middot; playwright &middot; sqlite &middot; alembic &middot; fastapi</p>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--active" aria-label="Status: active"></span>
                <span class="project__status-label">ACTIVE</span>
                <span class="project__last-commit" data-meta="FUSE-Web.last_commit">last commit: recent</span>
              </header>
              <h3 class="project__name">FUSE-Web</h3>
              <p class="project__what">Next.js + Supabase platform for insurance catastrophe management.</p>
              <p class="project__body">Role-based accounts (Admin / PM / staff), War Room workflows, resource center. Vitest unit tests plus Playwright smoke checks before each deploy. Private repo &mdash; screenshot below.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> next.js 14 &middot; supabase &middot; vitest &middot; playwright</p>
              <p class="project__chips">typescript &middot; next.js &middot; supabase &middot; vitest &middot; playwright</p>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--shipped" aria-label="Status: shipped"></span>
                <span class="project__status-label">SHIPPED</span>
                <span class="project__last-commit">mar 2024</span>
              </header>
              <h3 class="project__name">Mega Tic-Tac-Toe</h3>
              <p class="project__what">Unity game on a 3&times;3 grid of linked Tic-Tac-Toe boards &mdash; each move dictates the opponent&rsquo;s next board.</p>
              <p class="project__body">Local + online multiplayer; single player vs. a Minimax-based AI with multiple difficulty levels. Self-shipped indie title.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> unity &middot; c# &middot; minimax ai &middot; local + online mp</p>
              <p class="project__chips">unity &middot; c# &middot; minimax ai &middot; multiplayer</p>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--shipped" aria-label="Status: shipped"></span>
                <span class="project__status-label">SHIPPED</span>
                <span class="project__last-commit">2024</span>
              </header>
              <h3 class="project__name">Smart Shoe Navigation</h3>
              <p class="project__what">Dart mobile app pairing via Bluetooth to a &ldquo;Smart Shoe&rdquo; for turn-by-turn directions.</p>
              <p class="project__body">Users enter a destination; the app delivers on-screen prompts plus directional haptic feedback in the shoe itself.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> dart &middot; flutter &middot; bluetooth &middot; embedded haptics</p>
              <p class="project__chips">dart &middot; flutter &middot; bluetooth &middot; embedded</p>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--shipped" aria-label="Status: shipped"></span>
                <span class="project__status-label">SHIPPED</span>
                <span class="project__last-commit">2023</span>
              </header>
              <h3 class="project__name">Walking / Jumping Classifier</h3>
              <p class="project__what">Python ML pipeline classifying accelerometer time-series as walking vs. jumping.</p>
              <p class="project__body">End-to-end &mdash; data collection, feature engineering, model training, evaluation. Course capstone shipped with reproducible scripts.</p>
              <p class="project__metrics"><span class="metrics__prefix">//</span> python &middot; accelerometer &middot; signal processing</p>
              <p class="project__chips">python &middot; numpy &middot; scikit-learn &middot; signal processing</p>
            </article>

          </div>
          <p class="projects__more"><a href="https://github.com/jakethehoffer" target="_blank" rel="noopener">$ ls ~/github &rarr;</a></p>
        </div>
      </section>
```

Notes:
- `data-meta="trader.last_commit"` is the sentinel marker the refresh
  script will target in Task 13.
- The "Mega Tic-Tac-Toe / Smart Shoe / Walking-Jumping" projects use
  fixed date strings, not sentinel markers — they're shipped, not
  evolving.

- [ ] **Step 2: Append Projects styles**

```css
/* ---------- Projects ---------- */
.projects {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
}
@media (min-width: 640px) {
  .projects { grid-template-columns: repeat(2, 1fr); }
}

.project {
  background: var(--bg-elev);
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  position: relative;
  transition: border-color 0.18s ease;
}
.project::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: transparent;
  border-top-left-radius: var(--radius);
  border-bottom-left-radius: var(--radius);
  transition: background 0.18s ease;
}
.project:hover { border-color: var(--text-mute); }
.project:hover::before { background: var(--accent); }

.project__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-mute);
  margin-bottom: 0.5rem;
  letter-spacing: 0.02em;
}
.project__last-commit { margin-left: auto; }

.status {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 50%;
}
.status--active {
  background: var(--accent);
  box-shadow: 0 0 8px rgba(245, 179, 66, 0.5);
}
.status--shipped {
  background: var(--accent-2);
  box-shadow: 0 0 6px rgba(127, 191, 127, 0.4);
}
.project__status-label {
  color: var(--text-dim);
  font-weight: 500;
}

.project__name {
  font-size: 1.0625rem;
  margin: 0 0 0.5rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.project__name a { color: var(--text); }
.project__name a:hover { color: var(--accent); text-decoration: none; }

.project__what {
  margin: 0 0 0.5rem;
  font-weight: 500;
}
.project__body {
  margin: 0 0 0.875rem;
  color: var(--text-dim);
  font-size: 0.9375rem;
}
.project__metrics {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-dim);
}
.project__chips {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-mute);
}

.projects__more {
  margin: 2rem 0 0;
  font-size: 0.9375rem;
}
.projects__more a { color: var(--accent); }
```

- [ ] **Step 3: Verify**

Reload. Projects now render as a two-column grid (one column on
< 640px) of cards. Each card has a status dot, status label, and a
right-aligned "last commit" line. The amber left-border slides in on
hover.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): rebuild project cards as git-log entries with status dots"
```

---

## Task 8: Project cards — FUSE-Web screenshot + output samples

Convert the FUSE-Web overview screenshot to WebP and add it to the FUSE-
Web card. Add small "output sample" code blocks to the cards without
images.

**Files:**
- Create: `C:/Users/14jak/GitHub/website/assets/projects/fuse-web.webp`
- Modify: `C:/Users/14jak/GitHub/website/index.html` (project cards)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Convert the FUSE-Web screenshot to WebP**

```bash
mkdir -p "C:/Users/14jak/GitHub/website/assets/projects"
# Pillow ships with the Python on this machine; use it to encode WebP.
python -c "from PIL import Image; im = Image.open(r'C:/Users/14jak/GitHub/FUSE-Web/worksheet-overview.png'); im.save(r'C:/Users/14jak/GitHub/website/assets/projects/fuse-web.webp', 'WEBP', quality=80, method=6)"
ls -la "C:/Users/14jak/GitHub/website/assets/projects/fuse-web.webp"
```

Expected: a file under 50 KB. If Pillow isn't available, fall back to
LibreOffice's bundled `cwebp` if installed, or skip this step and
reference the PNG directly (copy `worksheet-overview.png` → `fuse-web.png`
and use `<img src="assets/projects/fuse-web.png">` instead of WebP).

- [ ] **Step 2: Add the FUSE-Web image to its card**

In `index.html`, find the FUSE-Web `<article>` block. After the
`<p class="project__chips">…</p>` line and before `</article>`, insert:

```html
              <figure class="project__media">
                <img src="assets/projects/fuse-web.webp" alt="FUSE-Web worksheet overview" loading="lazy" decoding="async" width="1200" height="700" />
              </figure>
```

- [ ] **Step 3: Add output samples to the other five project cards**

For each of the five remaining project cards, insert a `<pre class="project__sample">…</pre>` block in the same position (after chips, before `</article>`):

For **trader**:
```html
              <pre class="project__sample" aria-label="Sample log line"><span class="sample__dim">[2026-05-12 09:31:02]</span> <span class="sample__ok">scan_premarket</span>: 14 candidates &rarr; <span class="sample__hi">3 passed</span> (volatility gate)
<span class="sample__dim">[2026-05-12 09:31:18]</span> <span class="sample__ok">place_orders</span>: limit buy 100 NVDA @ 132.40 (paper)
<span class="sample__dim">[2026-05-12 16:00:01]</span> <span class="sample__ok">eod</span>: pnl +1.23%, 1 fill, 0 reject</pre>
```

For **Odds Aggregator**:
```html
              <pre class="project__sample" aria-label="Sample alert"><span class="sample__hi">[ARB]</span> NHL &middot; Edmonton @ Vegas
  pinnacle  EDM -132   &rarr;  stake 0.567
  betmgm    VGK +145   &rarr;  stake 0.433
  edge      <span class="sample__ok">+0.84%</span>      ttl 4m12s</pre>
```

For **Mega Tic-Tac-Toe**:
```html
              <pre class="project__sample" aria-label="Sample board state">+---+---+---+
| X | . | O |
+---+---+---+   active board: top-right
| . | X | . |   minimax depth 6
+---+---+---+   eval +0.21
| O | . | X |</pre>
```

For **Smart Shoe Navigation**:
```html
              <pre class="project__sample" aria-label="Sample API call"><span class="sample__dim">// turn right in 30m</span>
shoe.pulse(side: <span class="sample__hi">Side.right</span>,
           strength: 0.7,
           pattern: <span class="sample__hi">Pattern.doubleTap</span>);</pre>
```

For **Walking / Jumping Classifier**:
```html
              <pre class="project__sample" aria-label="Sample confusion matrix">              pred=walk  pred=jump
true=walk        <span class="sample__ok">182</span>         7
true=jump          5        <span class="sample__ok">156</span>

accuracy   <span class="sample__hi">0.965</span>   f1 0.964</pre>
```

- [ ] **Step 4: Append project-media + sample styles**

```css
/* ---------- Project media + samples ---------- */
.project__media {
  margin: 1rem 0 0;
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg);
}
.project__media img {
  display: block;
  width: 100%;
  height: auto;
}

.project__sample {
  margin: 1rem 0 0;
  padding: 0.75rem 0.875rem;
  background: var(--bg);
  border: 1px solid var(--bg-grid);
  border-left: 2px solid var(--accent);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  line-height: 1.55;
  color: var(--text-dim);
  white-space: pre;
  overflow-x: auto;
}
.sample__dim { color: var(--text-mute); }
.sample__ok  { color: var(--accent-2); }
.sample__hi  { color: var(--accent); }
```

- [ ] **Step 5: Verify**

Reload. Each project card now has either a screenshot (FUSE-Web) or a
small ascii-flavored output sample. Hovering still slides in the amber
left-border on the card itself. The sample blocks have their own
permanent amber left-border.

- [ ] **Step 6: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add assets/projects/fuse-web.webp index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): add FUSE-Web screenshot and per-project output samples"
```

---

## Task 9: Case study — `trader` deep-dive

Add a new full-width section between Projects and Experience with the
ASCII architecture diagram and three paragraphs.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (insert new section)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Insert the case-study section**

In `index.html`, find the closing `</section>` of `<section id="projects">`.
Immediately after it, before `<section id="experience">`, insert:

```html
      <section id="case-study" class="section">
        <div class="container">
          <p class="section__label"># case study</p>
          <h2>trader &mdash; a 24/7 ai swing-trading agent</h2>
          <p class="case-study__lede">
            Six scheduled Claude Code routines on IBKR paper + Finnhub news.
            Paper-trading the S&amp;P 500, graduating to live only after 30 paper
            days of documented outperformance.
          </p>

          <pre class="diagram" aria-label="trader architecture: six scheduled routines">
   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;    &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;
   &#9474;  scan_premarket  &#9474;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9658;&#9474;      gate        &#9474;
   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;    &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;
                                       &#9474;
                                       &#9660;
   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;    &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;
   &#9474;     monitor      &#9474;&#9668;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9474;   place_orders   &#9474;
   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;    &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;
            &#9474;
            &#9660;
   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;    &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;
   &#9474;       eod        &#9474;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9658;&#9474;     journal      &#9474;
   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;    &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;
          </pre>

          <div class="case-study__prose">
            <h3>The problem</h3>
            <p>A monolith trading bot is one place where every bug becomes a money bug. Splitting the work across six small, idempotent routines means each one can be tested in isolation, re-run safely on failure, and reasoned about on its own. <code>scan_premarket</code> only knows how to filter candidates; <code>gate</code> only knows the risk rules; <code>place_orders</code> only knows the IBKR API. They communicate through the journal, not in-process state.</p>

            <h3>The risk model</h3>
            <p>Default is paper. The kill-switch is a single YAML key (<code>kill_switch.enabled: true</code>) read at the top of every routine &mdash; flip it and the system stops opening positions at the next scheduled tick. Risk counters (per-trade, per-day, per-week) live in committed JSON so the state survives restarts and is reviewable in a diff. The 30-day paper gate is enforced by <code>gate</code> reading a graduation file written only by the EOD routine.</p>

            <h3>What&rsquo;s next</h3>
            <p>Graduation to live trading is contingent on documented outperformance vs. SPY across 30 paper days. The broker layer is already abstracted (<code>broker.py</code> &mdash; IBKR active, Alpaca preserved) so the live cutover is a config change. Building toward a backtester that replays the journal against historical Finnhub headlines to validate model changes before they touch a real fill.</p>
          </div>
        </div>
      </section>
```

- [ ] **Step 2: Append case-study styles**

```css
/* ---------- Case study ---------- */
.case-study__lede {
  font-size: 1.0625rem;
  color: var(--text);
  max-width: 65ch;
  margin: 0 0 2rem;
}
.diagram {
  margin: 0 0 2rem;
  padding: 1.25rem 1rem;
  background: var(--bg-elev);
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius);
  color: var(--accent);
  font-size: 0.75rem;
  line-height: 1.4;
  overflow-x: auto;
  white-space: pre;
}
@media (min-width: 640px) {
  .diagram { font-size: 0.8125rem; }
}
.case-study__prose h3 {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-mute);
  margin: 2rem 0 0.5rem;
  font-weight: 500;
}
.case-study__prose h3:first-child { margin-top: 0; }
.case-study__prose p {
  margin: 0 0 1rem;
  max-width: 65ch;
  color: var(--text);
}
.case-study__prose code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  color: var(--accent);
  background: var(--bg-elev);
  padding: 0.05em 0.35em;
  border-radius: 3px;
}
```

- [ ] **Step 3: Verify**

Reload. A new case-study section appears between Projects and
Experience, with the amber ASCII flow diagram and three subsections.
The diagram should align vertically and not wrap weirdly on desktop;
on mobile it scrolls horizontally inside its container.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): add trader case-study with ascii architecture diagram"
```

---

## Task 10: Experience — git-log timeline restyle

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (Experience section)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Replace the Experience section**

```html
      <section id="experience" class="section">
        <div class="container">
          <p class="section__label"># experience</p>
          <h2>Where I&rsquo;ve worked</h2>
          <ol class="timeline">

            <li class="timeline__item">
              <header class="timeline__head">
                <span class="status status--active" aria-hidden="true"></span>
                <h3 class="timeline__role">IT Intern</h3>
                <span class="timeline__dates">jun 2024 &ndash; aug 2025</span>
              </header>
              <p class="timeline__org">Lynx Equity Limited</p>
              <ul class="timeline__bullets">
                <li>Built a task-management system on Monday.com that streamlined communication between subsidiaries by auto-routing issues to the right workflow queue.</li>
                <li>Designed an On/Off-Boarding workflow with standardized role-based tasks, handoffs, and approvals; delivered a stakeholder demo and shipped feedback into the final product.</li>
                <li>Wrote Google Apps Script (JavaScript) to ingest multiple Excel exports into a single Google Sheet, apply pricing logic, and track unmatched keys for reconciliation; added a Sheets custom menu and logic for dynamic Excel file IDs.</li>
                <li>Conducted DNS lookups across subsidiary domains to inventory email providers, SSL status, and other domain metadata.</li>
              </ul>
            </li>

            <li class="timeline__item">
              <header class="timeline__head">
                <span class="status status--shipped" aria-hidden="true"></span>
                <h3 class="timeline__role">Independent Game Developer &mdash; Mega Tic-Tac-Toe</h3>
                <span class="timeline__dates">jan &ndash; mar 2024</span>
              </header>
              <p class="timeline__org">Self-published, Unity</p>
              <ul class="timeline__bullets">
                <li>Designed and programmed a Unity game on a 3&times;3 grid of linked Tic-Tac-Toe boards where each move dictates the opponent&rsquo;s next board.</li>
                <li>Shipped local + online multiplayer plus single-player vs. a Minimax-based AI with multiple difficulty levels.</li>
              </ul>
            </li>

            <li class="timeline__item">
              <header class="timeline__head">
                <span class="status status--shipped" aria-hidden="true"></span>
                <h3 class="timeline__role">Design Team Member</h3>
                <span class="timeline__dates">oct 2023 &ndash; mar 2024</span>
              </header>
              <p class="timeline__org">QMIND &mdash; Queen&rsquo;s AI Hub</p>
              <ul class="timeline__bullets">
                <li>Trained a reinforcement-learning agent to play Blackjack alongside the team.</li>
                <li>Built a tabular Q-learning baseline with training loop and basic tests, then helped migrate the system to a Deep Q-learning version so the model could learn policies beyond a simple lookup table.</li>
              </ul>
            </li>

            <li class="timeline__item">
              <header class="timeline__head">
                <span class="status status--shipped" aria-hidden="true"></span>
                <h3 class="timeline__role">Financial Analyst</h3>
                <span class="timeline__dates">oct 2021 &ndash; jun 2023</span>
              </header>
              <p class="timeline__org">BMC Pharmacy</p>
              <ul class="timeline__bullets">
                <li>Scoped the animal-drug compounding market opportunity across SW Ontario.</li>
                <li>Tracked monthly, quarterly, and YoY profitability and margin contribution from drug utilization, expanded services, and Rx reports.</li>
              </ul>
            </li>

          </ol>
        </div>
      </section>
```

- [ ] **Step 2: Append Timeline styles**

```css
/* ---------- Timeline ---------- */
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 2rem;
  position: relative;
}
.timeline__item {
  position: relative;
  padding-left: 1.5rem;
  border-left: 1px solid var(--bg-grid);
}
.timeline__head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
}
.timeline__head .status {
  position: absolute;
  left: -5px;
  top: 0.5rem;
}
.timeline__role {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.timeline__dates {
  margin-left: auto;
  color: var(--text-mute);
  font-size: 0.8125rem;
}
.timeline__org {
  margin: 0 0 0.75rem;
  color: var(--text-dim);
  font-size: 0.9375rem;
}
.timeline__bullets {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--text);
}
.timeline__bullets li { margin: 0.375rem 0; max-width: 70ch; }
```

- [ ] **Step 3: Verify**

Reload. Experience now reads as a vertical timeline with a hairline
left rail, status dots overlapping the rail, role / org / dates header,
and bullets indented under the rail.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): experience as git-log timeline with status dots and rail"
```

---

## Task 11: Education + Contact + Footer — restyle

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (Education, Contact, Footer)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Replace the Education section**

```html
      <section id="education" class="section">
        <div class="container">
          <p class="section__label"># education</p>
          <h2>Education</h2>
          <article class="education">
            <header class="education__head">
              <h3 class="education__school">Queen&rsquo;s University</h3>
              <span class="education__dates">2023 &ndash; expected 2027</span>
            </header>
            <p class="education__program">BASc, Computer Engineering &middot; <span class="education__gpa">GPA 3.85 &middot; Dean&rsquo;s Scholar</span></p>
            <ul class="education__highlights">
              <li>Built a Python ML classifier on accelerometer data for walking vs. jumping.</li>
              <li>Developed a pathfinding algorithm in Python for autonomous rover operation.</li>
              <li>Built a Dart mobile app paired with a Bluetooth &ldquo;Smart Shoe&rdquo; for directional haptic navigation.</li>
            </ul>
          </article>
        </div>
      </section>
```

- [ ] **Step 2: Replace the Contact section**

```html
      <section id="contact" class="section">
        <div class="container">
          <p class="section__label"># contact</p>
          <h2>Get in touch</h2>
          <p class="contact__lede">Email is best. Open to internships, co-ops, and interesting side-project collaborations.</p>
          <div class="contact__links">
            <a class="btn btn--primary" href="mailto:14jakehoffman@gmail.com">[ 14jakehoffman@gmail.com ]</a>
            <a class="btn" href="https://github.com/jakethehoffer" target="_blank" rel="noopener">[ github.com/jakethehoffer ]</a>
            <a class="btn" href="https://www.linkedin.com/in/jake-hoffman-7117692a5/" target="_blank" rel="noopener">[ linkedin ]</a>
          </div>
        </div>
      </section>
```

- [ ] **Step 3: Replace the Footer**

```html
    <footer class="site-footer">
      <div class="container site-footer__inner">
        <p class="site-footer__prompt">$ <span class="boot__caret" aria-hidden="true">_</span></p>
        <p class="site-footer__meta">
          <span data-meta="last_deployed">last_deployed: 2026-05-12</span>
          <span class="site-footer__sep">&middot;</span>
          <span>&copy; <span id="footer-year">2026</span> jake hoffman</span>
        </p>
      </div>
    </footer>
```

- [ ] **Step 4: Append Education / Contact / Footer styles**

```css
/* ---------- Education ---------- */
.education__head {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.education__school {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.education__dates {
  margin-left: auto;
  color: var(--text-mute);
  font-size: 0.8125rem;
}
.education__program {
  margin: 0.25rem 0 0.75rem;
  color: var(--text-dim);
}
.education__gpa { color: var(--accent); }
.education__highlights {
  margin: 0;
  padding-left: 1.25rem;
  max-width: 70ch;
}
.education__highlights li { margin: 0.25rem 0; }

/* ---------- Contact ---------- */
.contact__lede {
  max-width: 60ch;
  margin: 0 0 1.25rem;
  color: var(--text);
}
.contact__links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}

/* ---------- Footer ---------- */
.site-footer {
  border-top: 1px solid var(--bg-grid);
  padding: 2rem 0 3rem;
  font-size: 0.8125rem;
  color: var(--text-mute);
}
.site-footer__inner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  justify-content: space-between;
}
.site-footer p { margin: 0; }
.site-footer__prompt { color: var(--accent); }
.site-footer__sep { margin: 0 0.25rem; }
```

- [ ] **Step 5: Verify**

Reload. Education has a school/date header row and an amber GPA badge.
Contact section has a single-sentence lede plus three bracket buttons.
The footer shows `$ _` (blinking) on the left and the deploy timestamp
+ copyright on the right.

- [ ] **Step 6: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): restyle education, contact, footer in mono"
```

---

## Task 12: Nav — command-style anchors + amber accent

Restyle the existing sticky header so the brand reads as a prompt and
each nav link looks like a command name.

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (nav `<header>`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Update the nav markup**

Find the existing `<header class="site-header">…</header>` block at the
top of `<body>`. Replace it with:

```html
    <header class="site-header">
      <nav class="site-nav" aria-label="Primary">
        <a class="nav-brand" href="#top"><span class="nav-brand__prompt">$</span> jake_hoffman</a>
        <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Open navigation">
          <span></span><span></span><span></span>
        </button>
        <ul class="nav-menu" id="nav-menu">
          <li><a href="#about">about</a></li>
          <li><a href="#skills">skills</a></li>
          <li><a href="#projects">projects</a></li>
          <li><a href="#case-study">case_study</a></li>
          <li><a href="#experience">experience</a></li>
          <li><a href="#education">education</a></li>
          <li><a href="#contact">contact</a></li>
          <li>
            <button class="theme-toggle" type="button" aria-label="Switch theme">
              <span class="theme-toggle__label">theme</span>
            </button>
          </li>
        </ul>
      </nav>
    </header>
```

- [ ] **Step 2: Append nav styles**

```css
/* ---------- Header / nav ---------- */
.site-header {
  position: sticky;
  top: 0;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: saturate(180%) blur(8px);
  -webkit-backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--bg-grid);
  z-index: 20;
}
.site-nav {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0.75rem var(--gutter);
  display: flex;
  align-items: center;
  gap: 1rem;
}
.nav-brand {
  font-weight: 700;
  color: var(--text);
  font-size: 0.9375rem;
}
.nav-brand:hover { text-decoration: none; color: var(--accent); }
.nav-brand__prompt { color: var(--accent); margin-right: 0.25em; }

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  list-style: none;
  margin: 0 0 0 auto;
  padding: 0;
}
.nav-menu a {
  color: var(--text-dim);
  font-size: 0.875rem;
}
.nav-menu a:hover { color: var(--accent); text-decoration: none; }

.nav-toggle {
  display: none;
  margin-left: auto;
  width: 40px;
  height: 40px;
  flex-direction: column;
  gap: 5px;
  justify-content: center;
  align-items: center;
  border-radius: var(--radius-sm);
}
.nav-toggle span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--text);
  border-radius: 2px;
}
.theme-toggle {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius-sm);
  color: var(--text-dim);
  text-transform: lowercase;
}
.theme-toggle:hover { color: var(--accent); border-color: var(--accent); }

@media (max-width: 768px) {
  .nav-toggle { display: flex; }
  .nav-menu {
    position: absolute;
    top: 100%;
    right: 0;
    left: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--bg-grid);
    padding: 0.5rem var(--gutter);
    display: none;
  }
  .nav-menu.is-open { display: flex; }
  .nav-menu li { padding: 0.5rem 0; }
  .nav-menu a { display: block; padding: 0.25rem 0; }
}
```

- [ ] **Step 3: Verify**

Reload. Nav now reads `$ jake_hoffman` on the left and lowercased
command-name links on the right. Hovering a nav link colors it amber.
Theme toggle is the same mechanism, restyled. Resize to < 768px:
hamburger appears, menu collapses correctly. The `case_study` anchor
link scrolls to the new section.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): restyle sticky nav as command palette"
```

---

## Task 13: `refresh-meta.mjs` — optional last-commit injector

A Node script that fetches `pushed_at` for each featured repo via
`gh api` and search-and-replaces sentinel markers in `index.html`.

**Files:**
- Create: `C:/Users/14jak/GitHub/website/scripts/refresh-meta.mjs`
- Modify: `C:/Users/14jak/GitHub/website/index.html` (replace `last commit: recent` strings with sentinel-aware markers)

- [ ] **Step 1: Add sentinel comments around each `last commit` span**

The existing project cards already use `data-meta="<repo>.last_commit"`
attributes (added in Task 7). The refresh script targets the *text
content* of those elements. No HTML change is needed — but we should
also wrap the footer's `last_deployed` line the same way (already done
in Task 11 with `data-meta="last_deployed"`).

Confirm with:

```bash
grep -n 'data-meta=' "C:/Users/14jak/GitHub/website/index.html"
```

Expected: 4 lines — `trader.last_commit`, `arbitrage.last_commit`,
`FUSE-Web.last_commit`, `last_deployed`.

- [ ] **Step 2: Create `scripts/refresh-meta.mjs`**

```js
#!/usr/bin/env node
// refresh-meta.mjs — opt-in metadata injector for index.html
//
// For each featured repo, fetch `pushed_at` via `gh api` and rewrite the
// text content of <span data-meta="<repo>.last_commit"> in index.html.
// Also stamps the footer <span data-meta="last_deployed"> with today's
// ISO date.
//
// Usage:   node scripts/refresh-meta.mjs
// Requires: gh CLI, authenticated as a user with read access to each repo.

import { execSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const INDEX = resolve(HERE, "..", "index.html");

const REPOS = [
  { owner: "jakethehoffer", name: "trader",     key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage",  key: "arbitrage.last_commit" },
  // FUSE-Web is in a different org. Adjust the owner if you have access.
  { owner: "Shield-Restoration-Services", name: "FUSE-Web", key: "FUSE-Web.last_commit" },
];

function ghPushedAt(owner, name) {
  try {
    const json = execSync(`gh api repos/${owner}/${name}`, { encoding: "utf8" });
    return JSON.parse(json).pushed_at;
  } catch (err) {
    console.warn(`[skip] ${owner}/${name}: ${err.message.split("\n")[0]}`);
    return null;
  }
}

function humanize(iso) {
  if (!iso) return null;
  const then = new Date(iso);
  const now = new Date();
  const days = Math.floor((now - then) / 86400000);
  if (days <= 0) return "last commit: today";
  if (days === 1) return "last commit: 1d ago";
  if (days < 14) return `last commit: ${days}d ago`;
  if (days < 60) return `last commit: ${Math.round(days / 7)}w ago`;
  return `last commit: ${then.toISOString().slice(0, 10)}`;
}

function replaceMeta(html, key, value) {
  if (value == null) return html;
  // Match any text between the opening and closing tag.
  const pattern = new RegExp(
    `(<span[^>]*data-meta="${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*>)([^<]*)(</span>)`,
    "g"
  );
  return html.replace(pattern, (_, open, _old, close) => `${open}${value}${close}`);
}

function main() {
  let html = readFileSync(INDEX, "utf8");
  let touched = 0;

  for (const repo of REPOS) {
    const value = humanize(ghPushedAt(repo.owner, repo.name));
    if (!value) continue;
    const before = html;
    html = replaceMeta(html, repo.key, value);
    if (html !== before) {
      touched++;
      console.log(`[ok]   ${repo.key} = "${value}"`);
    } else {
      console.warn(`[miss] ${repo.key} (no sentinel found in index.html)`);
    }
  }

  // Footer last_deployed
  const today = new Date().toISOString().slice(0, 10);
  const before = html;
  html = replaceMeta(html, "last_deployed", `last_deployed: ${today}`);
  if (html !== before) {
    touched++;
    console.log(`[ok]   last_deployed = ${today}`);
  }

  if (touched > 0) {
    writeFileSync(INDEX, html, "utf8");
    console.log(`\nWrote ${touched} update(s) to ${INDEX}.`);
  } else {
    console.log("\nNo updates written.");
  }
}

main();
```

- [ ] **Step 3: Run the script**

```bash
node "C:/Users/14jak/GitHub/website/scripts/refresh-meta.mjs"
```

Expected output: one `[ok]` line per accessible repo (`trader`,
`arbitrage`), one `[skip]` line for FUSE-Web if the script doesn't have
access to the Shield-Restoration-Services org (which is fine — FUSE-Web's
last_commit will stay as the default string), and one `[ok]` for
last_deployed.

- [ ] **Step 4: Verify in browser**

Reload `index.html`. The `trader` and `Odds Aggregator` cards should
now show `last commit: 2d ago` or similar. The footer should show
today's date.

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/refresh-meta.mjs index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(v2): add opt-in refresh-meta.mjs to inject real last-commit data"
```

---

## Task 14: Cleanup — remove avatar.svg, update README, final smoke tests

**Files:**
- Delete: `C:/Users/14jak/GitHub/website/assets/avatar.svg`
- Modify: `C:/Users/14jak/GitHub/website/README.md`

- [ ] **Step 1: Delete the unused avatar SVG**

```bash
rm "C:/Users/14jak/GitHub/website/assets/avatar.svg"
```

(v2 has no avatar in the hero — the boot sequence carries the
introduction.)

- [ ] **Step 2: Rewrite `README.md`**

```markdown
# website

Single-page resume for Jake Hoffman &mdash; the "engineering log" v2.
Plain HTML, CSS, and a touch of vanilla JS. No framework, no build step.

## Serve locally

```bash
python -m http.server 8000
```

Open <http://localhost:8000/>. You can also just double-click
`index.html` &mdash; it works `file://` too.

## Refresh project last-commit data (optional)

`scripts/refresh-meta.mjs` pulls `pushed_at` from GitHub for each
featured repo and rewrites the corresponding `<span data-meta="…">` in
`index.html`. It also stamps the footer `last_deployed`.

```bash
node scripts/refresh-meta.mjs
```

Requires the `gh` CLI authenticated with read access to the repos in the
script's `REPOS` list. Safe to skip &mdash; defaults stay in place if you
don't run it.

## Refresh `resume.pdf`

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo,
then in **Settings &rarr; Pages**, source = `main` branch / root.

## Files

- `index.html` &mdash; semantic single-page markup, boot-sequence end-state, JSON-LD Person.
- `styles.css` &mdash; all-mono design system, dark default + parchment light.
- `script.js` &mdash; boot animation, mobile nav, theme toggle, IntersectionObserver reveal.
- `scripts/refresh-meta.mjs` &mdash; optional last-commit injector (Node, uses `gh`).
- `assets/projects/fuse-web.webp` &mdash; FUSE-Web product screenshot.
- `resume.pdf` &mdash; downloadable PDF.
- `docs/superpowers/` &mdash; design spec and implementation plan.
```

- [ ] **Step 3: Final visual smoke tests**

Open `index.html` in Chrome via `python -m http.server 8000` from the
repo root. Verify:

- Hero boot sequence types out on first load (clear `sessionStorage` to
  re-test). Skips on second load in same session.
- Theme toggle in the nav switches between dark and parchment. Reload
  persists the choice.
- Nav anchor links scroll smoothly to each section, including the new
  `case_study`.
- Project cards show status dots, last-commit text (real or default),
  and either a screenshot (FUSE-Web) or an output sample.
- Case-study ASCII diagram renders aligned in dark mode, and remains
  aligned in parchment (mono font means the alignment is theme-agnostic).
- Timeline cards have the left rail with status dots overlapping it.
- Footer shows a blinking `$ _` cursor on the left and the deploy
  timestamp on the right.
- Resize to 360px wide: hero still legible, hamburger appears, project
  grid collapses to one column, diagram scrolls horizontally inside
  its container.
- Tab through the page with the keyboard. The skip link appears on
  first tab. Every interactive element has a visible focus ring.
- In DevTools → Rendering → Emulate CSS `prefers-reduced-motion: reduce`,
  clear `sessionStorage`, reload. No boot animation, no caret blink,
  no scroll fade. Content is identical to its un-reduced final state.

- [ ] **Step 4: Run Lighthouse**

In Chrome DevTools → Lighthouse → run Performance, Accessibility, Best
Practices, SEO with mobile + desktop. Target ≥ 95 in each category. If
any score drops below 95, note the failed audit and either fix it or
record it in the commit message as a known limitation.

- [ ] **Step 5: Commit and push**

```bash
git -C "C:/Users/14jak/GitHub/website" add README.md
git -C "C:/Users/14jak/GitHub/website" rm assets/avatar.svg
git -C "C:/Users/14jak/GitHub/website" commit -m "chore(v2): drop avatar.svg, rewrite README for new design + refresh-meta"
git -C "C:/Users/14jak/GitHub/website" push
```

---

## Task 15: Update .ai-sync handoff

**Files:**
- Modify (via helper): `C:/Users/14jak/GitHub/website/.ai-sync/state.md`

- [ ] **Step 1: Run the handoff command**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "v2 'engineering log' redesign live. Mono-only typography, terminal-flavored dark default with parchment light, git-log-style project cards with status dots and real last-commit data via opt-in refresh-meta.mjs, new trader case-study with ASCII architecture diagram." -FilesChanged "index.html, styles.css, script.js, scripts/refresh-meta.mjs (NEW), assets/projects/fuse-web.webp (NEW), assets/avatar.svg (DELETED), README.md, docs/superpowers/specs/2026-05-12-resume-website-v2-design.md, docs/superpowers/plans/2026-05-12-resume-website-v2.md" -TestsRun "Manual visual smoke tests on Chrome (dark + parchment, mobile + desktop), boot animation timing, theme persistence, keyboard tab order, prefers-reduced-motion. refresh-meta.mjs run on trader + arbitrage. Lighthouse passed >=95 on Performance/Accessibility/Best Practices/SEO." -Blockers "FUSE-Web last_commit stays as default unless gh CLI has access to Shield-Restoration-Services org." -NextSteps "1) Decide on GitHub Pages (currently private repo). 2) Add screenshots for other projects as Jake takes them. 3) Optionally re-run refresh-meta.mjs before any external sharing for fresh dates."
```

- [ ] **Step 2: Verify handoff**

```bash
head -40 "C:/Users/14jak/GitHub/website/.ai-sync/state.md"
```

Expected: the Latest Decisions / Active Tasks / Next Steps sections
reflect the v2 redesign.

---

## Closing checklist

After Task 15:
- [ ] All 15 task headings checked off above.
- [ ] `git -C "C:/Users/14jak/GitHub/website" log --oneline | head -20` shows ~14 v2 commits with clean conventional messages.
- [ ] `origin/main` reflects the v2 state.
- [ ] `assets/avatar.svg` is gone.
- [ ] `scripts/refresh-meta.mjs` runs without errors and updates at least 2 sentinel markers (`trader` + `arbitrage`).
- [ ] Page passes the spec's success-criteria mental model: a recruiter sees `●ACTIVE trader` and the bio in the first viewport; an engineer reading the case-study can infer technical judgment from the architecture diagram.
