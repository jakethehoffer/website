# Resume Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page static resume website for Jake Hoffman at `C:/Users/14jak/GitHub/website/`, deployable as-is to GitHub Pages.

**Architecture:** One `index.html`, one `styles.css`, one `script.js`. No build step, no framework, no CSS framework. Light theme by default with dark-mode toggle (CSS custom properties + localStorage). Semantic HTML, JSON-LD Person schema, IntersectionObserver-based scroll fade-in. Targets < 200 KB total page weight and Lighthouse ≥ 95 on Performance, Accessibility, Best Practices, and SEO.

**Tech Stack:** Plain HTML5, CSS3 (custom properties + grid + flexbox), vanilla JS (ES2020). Google Fonts (Inter + JetBrains Mono). LibreOffice (headless) to export `resume.pdf` from the source `.docx`.

**Spec:** `docs/superpowers/specs/2026-05-12-resume-website-design.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── index.html            single-page resume site
├── styles.css            all styles, light + dark via CSS custom properties
├── script.js             theme toggle, mobile nav, IntersectionObserver fade-in
├── resume.pdf            generated from the .docx during Task 15
├── README.md             short repo note + how to serve locally
├── .gitignore            standard web project ignores
└── assets/
    └── avatar.svg        initials placeholder ("JH")
```

`index.html`: structured, semantic markup of every section in the spec; loads the two fonts via `<link rel="preconnect">` + Google Fonts CSS; embeds JSON-LD Person schema; references `styles.css` and `script.js`.

`styles.css`: CSS custom properties at `:root` (light), overridden on `:root[data-theme="dark"]` (dark). Reset, typography, layout container, then per-section styles top-down.

`script.js`: three concerns — theme toggle (read `localStorage` `jh-theme`, apply, write on click), mobile hamburger (toggle a CSS class on the nav), IntersectionObserver to add `.is-visible` to sections as they enter the viewport.

`assets/avatar.svg`: 200×200 SVG with a circle background and the initials "JH" centered. Color picks accent and on-accent text via `currentColor` so it adapts to theme.

---

## Verification Approach

Static sites don't have unit tests in the traditional sense. Each task that produces visible output ends with a manual verification step: open `index.html` in a browser (or hit `http://localhost:8000` after `python -m http.server 8000`) and confirm the described behavior. The final task (Task 16) runs Chrome DevTools Lighthouse for objective scoring.

Where JS behavior is added (theme toggle, IntersectionObserver), the verification step calls out the exact action to take and the exact result to look for.

---

## Task 1: Scaffold the project

**Files:**
- Create: `C:/Users/14jak/GitHub/website/.gitignore`
- Create: `C:/Users/14jak/GitHub/website/index.html` (empty placeholder)
- Create: `C:/Users/14jak/GitHub/website/styles.css` (empty placeholder)
- Create: `C:/Users/14jak/GitHub/website/script.js` (empty placeholder)
- Create: `C:/Users/14jak/GitHub/website/assets/.gitkeep`

- [ ] **Step 1: Write `.gitignore`**

```gitignore
# OS
.DS_Store
Thumbs.db

# Editors
.vscode/
.idea/

# Build / temp
*.log
.tmp/
.tmp_*

# AI sync working files are committed; nothing to ignore there

# Local resume working copies (the canonical resume.pdf is committed)
*.docx
!resume-source.docx
```

- [ ] **Step 2: Create placeholder `index.html`**

```html
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Jake Hoffman</title></head>
  <body></body>
</html>
```

- [ ] **Step 3: Create empty `styles.css` and `script.js`**

`styles.css`:
```css
/* styles.css — filled in later tasks */
```

`script.js`:
```js
// script.js — filled in later tasks
```

- [ ] **Step 4: Create `assets/.gitkeep`**

Just an empty file so the directory is tracked.

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add .gitignore index.html styles.css script.js assets/.gitkeep
git -C "C:/Users/14jak/GitHub/website" commit -m "chore: scaffold static site files"
```

---

## Task 2: HTML skeleton — all sections with semantic structure

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html`

- [ ] **Step 1: Replace `index.html` with the full semantic skeleton**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Jake Hoffman — Computer Engineering @ Queen's University</title>
    <meta name="description" content="Jake Hoffman — 3rd-year Computer Engineering student at Queen's University. Builds production-grade software in Python, JavaScript, C/C++, Java, and Dart." />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>

    <header class="site-header">
      <nav class="site-nav" aria-label="Primary">
        <a class="nav-brand" href="#top">Jake Hoffman</a>
        <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Open navigation">
          <span></span><span></span><span></span>
        </button>
        <ul class="nav-menu" id="nav-menu">
          <li><a href="#about">About</a></li>
          <li><a href="#skills">Skills</a></li>
          <li><a href="#projects">Projects</a></li>
          <li><a href="#experience">Experience</a></li>
          <li><a href="#education">Education</a></li>
          <li><a href="#contact">Contact</a></li>
          <li>
            <button class="theme-toggle" type="button" aria-label="Switch theme">
              <span class="theme-toggle__label">Theme</span>
            </button>
          </li>
        </ul>
      </nav>
    </header>

    <main id="main">
      <section id="top" class="hero"></section>
      <section id="about" class="section"></section>
      <section id="skills" class="section"></section>
      <section id="projects" class="section"></section>
      <section id="experience" class="section"></section>
      <section id="education" class="section"></section>
      <section id="contact" class="section"></section>
    </main>

    <footer class="site-footer"></footer>

    <script src="script.js" defer></script>
  </body>
</html>
```

- [ ] **Step 2: Open in browser and verify**

Run: `start "" "C:/Users/14jak/GitHub/website/index.html"`
Expected: a blank, unstyled page with the document title "Jake Hoffman — Computer Engineering @ Queen's University" visible in the tab. No console errors.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(html): add semantic page skeleton with all sections"
```

---

## Task 3: Base CSS — tokens, reset, typography, container

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css`

- [ ] **Step 1: Replace `styles.css` with base styles**

```css
/* ---------- Design tokens (light theme) ---------- */
:root {
  --bg: #ffffff;
  --surface: #f8fafc;
  --surface-2: #f1f5f9;
  --text: #0f172a;
  --text-muted: #475569;
  --border: #e2e8f0;
  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --accent-contrast: #ffffff;

  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;

  --radius: 10px;
  --radius-sm: 6px;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);

  --container: 1080px;
  --gutter: 1.25rem;
}

/* ---------- Reset ---------- */
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: 1rem;
  line-height: 1.6;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
img, svg { display: block; max-width: 100%; }
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); text-decoration: underline; }
button {
  font: inherit;
  color: inherit;
  background: none;
  border: 0;
  cursor: pointer;
}

/* ---------- Layout primitives ---------- */
.container {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--gutter);
}
.section {
  padding: 4rem 0;
  border-top: 1px solid var(--border);
}
.section h2 {
  font-size: 1.5rem;
  margin: 0 0 1.5rem;
  letter-spacing: -0.01em;
}

/* ---------- Accessibility ---------- */
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  background: var(--accent);
  color: var(--accent-contrast);
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
```

- [ ] **Step 2: Verify in browser**

Reload `index.html`. Expected: white background, very subtle dark text from `--text`, fonts have loaded (Inter for body). No layout yet — that comes in section-specific tasks.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(css): add design tokens, reset, typography, layout primitives"
```

---

## Task 4: Hero section — content + style

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="top" class="hero">`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in the hero section**

Replace `<section id="top" class="hero"></section>` with:

```html
<section id="top" class="hero">
  <div class="container hero__inner">
    <div class="hero__avatar" aria-hidden="true">
      <!-- Replaced by assets/avatar.svg in Task 13 -->
      <span class="hero__avatar-initials">JH</span>
    </div>
    <div class="hero__copy">
      <p class="hero__eyebrow">Computer Engineering @ Queen&rsquo;s University</p>
      <h1 class="hero__name">Jake Hoffman</h1>
      <p class="hero__tagline">I build production-grade software &mdash; trading agents, arbitrage daemons, web platforms, and ML pipelines.</p>
      <ul class="hero__chips" aria-label="Core technologies">
        <li>Python</li><li>JavaScript</li><li>C / C++</li><li>SQL</li><li>Next.js</li>
      </ul>
      <div class="hero__ctas">
        <a class="btn btn--primary" href="mailto:14jakehoffman@gmail.com">Email</a>
        <a class="btn" href="https://github.com/jakethehoffer" target="_blank" rel="noopener">GitHub</a>
        <!-- TODO: confirm LinkedIn slug -->
        <a class="btn" href="https://www.linkedin.com/in/jakethehoffer/" target="_blank" rel="noopener">LinkedIn</a>
        <a class="btn btn--ghost" href="resume.pdf" download>Download Resume (PDF)</a>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append hero styles to `styles.css`**

```css
/* ---------- Hero ---------- */
.hero { padding: 5rem 0 3rem; }
.hero__inner {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 2rem;
  align-items: center;
}
.hero__avatar {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: var(--surface-2);
  display: grid;
  place-items: center;
  color: var(--accent);
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 3rem;
  box-shadow: var(--shadow-sm);
}
.hero__avatar-initials { letter-spacing: -0.05em; }
.hero__eyebrow {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0 0 0.5rem;
}
.hero__name {
  font-size: clamp(2.25rem, 4vw, 3.25rem);
  line-height: 1.1;
  margin: 0 0 0.75rem;
  letter-spacing: -0.02em;
}
.hero__tagline {
  font-size: 1.125rem;
  color: var(--text-muted);
  margin: 0 0 1.25rem;
  max-width: 56ch;
}
.hero__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
}
.hero__chips li {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  padding: 0.25rem 0.625rem;
  background: var(--surface-2);
  color: var(--text-muted);
  border-radius: 999px;
}
.hero__ctas { display: flex; flex-wrap: wrap; gap: 0.625rem; }

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.6rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-weight: 500;
  font-size: 0.9375rem;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
}
.btn:hover {
  text-decoration: none;
  background: var(--surface-2);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
.btn--primary {
  background: var(--accent);
  color: var(--accent-contrast);
  border-color: var(--accent);
}
.btn--primary:hover {
  background: var(--accent-hover);
  color: var(--accent-contrast);
}
.btn--ghost {
  background: transparent;
}

@media (max-width: 640px) {
  .hero { padding-top: 3rem; }
  .hero__inner {
    grid-template-columns: 1fr;
    text-align: left;
  }
  .hero__avatar { width: 96px; height: 96px; font-size: 2rem; }
}
```

- [ ] **Step 3: Verify in browser**

Reload. Expected: name "Jake Hoffman" large at the top, role line above it in mono, initials "JH" inside a circle to the left (or stacked on mobile), chip row, four buttons. Resize the window below 640px; layout stacks vertically and avatar shrinks.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(hero): name, tagline, chip row, primary CTAs"
```

---

## Task 5: About section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="about">`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in About**

Replace `<section id="about" class="section"></section>` with:

```html
<section id="about" class="section">
  <div class="container">
    <h2>About</h2>
    <div class="about">
      <p>Computer Engineering student at Queen&rsquo;s University with a strong foundation in software engineering principles, technical problem solving, and design analysis. Writes clean, maintainable code with attention to testing, logging, and performance.</p>
      <p>Comfortable collaborating with non-technical teammates to ship features that reduce manual work and improve reliability &mdash; from automating workflows on Monday.com to running a 24/7 arbitrage daemon across ten bookmakers.</p>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
/* ---------- About ---------- */
.about { max-width: 70ch; }
.about p { margin: 0 0 1rem; color: var(--text); }
.about p:last-child { margin-bottom: 0; }
```

- [ ] **Step 3: Verify**

Reload. Two paragraphs render under an "About" heading, with a thin top border separating from the hero.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(about): 2-paragraph summary"
```

---

## Task 6: Skills section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="skills">`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in Skills**

Replace `<section id="skills" class="section"></section>` with:

```html
<section id="skills" class="section">
  <div class="container">
    <h2>Skills</h2>
    <div class="skills">
      <div class="skill-group">
        <h3 class="skill-group__label">Languages</h3>
        <ul class="chips">
          <li>Python</li><li>Java</li><li>C</li><li>C#</li><li>C++</li>
          <li>JavaScript</li><li>TypeScript</li><li>Dart</li><li>SQL</li>
        </ul>
      </div>
      <div class="skill-group">
        <h3 class="skill-group__label">Tools &amp; Frameworks</h3>
        <ul class="chips">
          <li>Git</li><li>Next.js</li><li>Supabase</li><li>FastAPI</li>
          <li>Playwright</li><li>Unity</li><li>SQLite</li>
          <li>Monday.com</li><li>Google Apps Script</li><li>Excel</li>
        </ul>
      </div>
      <div class="skill-group">
        <h3 class="skill-group__label">Domains</h3>
        <ul class="chips">
          <li>Machine learning</li><li>Web development</li>
          <li>Automation</li><li>Trading systems</li><li>Mobile apps</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
/* ---------- Skills ---------- */
.skills { display: grid; gap: 1.5rem; }
.skill-group__label {
  font-size: 0.8125rem;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin: 0 0 0.5rem;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
}
.chips li {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  padding: 0.25rem 0.625rem;
  background: var(--surface-2);
  color: var(--text);
  border-radius: 999px;
  border: 1px solid var(--border);
}
```

- [ ] **Step 3: Verify**

Reload. Three groups (Languages, Tools & Frameworks, Domains) with monospace labels and chip rows.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(skills): three grouped chip lists"
```

---

## Task 7: Featured Projects section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="projects">`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in Projects**

Replace `<section id="projects" class="section"></section>` with:

```html
<section id="projects" class="section">
  <div class="container">
    <h2>Featured Projects</h2>
    <div class="projects">
      <article class="project">
        <h3 class="project__name">trader</h3>
        <p class="project__what">24/7 AI swing-trading agent for S&amp;P 500 equities, driven by six scheduled Claude Code routines.</p>
        <p class="project__why">Paper-traded on IBKR + Finnhub news; graduates to live only after 30 paper days of documented outperformance. Designed risk, journaling, and kill-switch from day one.</p>
        <ul class="chips">
          <li>Python</li><li>IBKR</li><li>Finnhub</li><li>pytest</li><li>Claude Code</li>
        </ul>
      </article>

      <article class="project">
        <h3 class="project__name">Odds Aggregator</h3>
        <p class="project__what">Production arbitrage daemon covering 10 bookmakers across 6 sports.</p>
        <p class="project__why">Ingest &rarr; normalize &rarr; detect cross-book arbs &rarr; push alerts to Telegram and Discord. Runs 24/7 on a Windows host with Alembic-managed schema and replay tooling.</p>
        <ul class="chips">
          <li>Python</li><li>Playwright</li><li>SQLite</li><li>Alembic</li><li>FastAPI</li>
        </ul>
      </article>

      <article class="project">
        <h3 class="project__name">[removed]</h3>
        <p class="project__what">Next.js + Supabase platform for [removed-domain].</p>
        <p class="project__why">Role-based accounts (Admin / PM / staff), War Room workflows, resource center. Vitest unit tests plus Playwright smoke checks before each deploy.</p>
        <ul class="chips">
          <li>Next.js</li><li>TypeScript</li><li>Supabase</li><li>Vitest</li><li>Playwright</li>
        </ul>
      </article>

      <article class="project">
        <h3 class="project__name">Mega Tic-Tac-Toe</h3>
        <p class="project__what">Unity game on a 3&times;3 grid of linked Tic-Tac-Toe boards &mdash; each move determines the opponent&rsquo;s next board.</p>
        <p class="project__why">Local + online multiplayer; single player vs. a Minimax-based AI with multiple difficulty levels. Self-shipped indie title.</p>
        <ul class="chips">
          <li>Unity</li><li>C#</li><li>Minimax AI</li><li>Multiplayer</li>
        </ul>
      </article>

      <article class="project">
        <h3 class="project__name">Smart Shoe Navigation</h3>
        <p class="project__what">Dart mobile app pairing via Bluetooth to a &ldquo;Smart Shoe&rdquo; for turn-by-turn directions.</p>
        <p class="project__why">Users enter a destination; the app delivers on-screen prompts plus directional haptic feedback in the shoe itself.</p>
        <ul class="chips">
          <li>Dart</li><li>Flutter</li><li>Bluetooth</li><li>Embedded</li>
        </ul>
      </article>

      <article class="project">
        <h3 class="project__name">Walking / Jumping Classifier</h3>
        <p class="project__what">Python ML pipeline classifying accelerometer time-series as walking vs. jumping.</p>
        <p class="project__why">End-to-end &mdash; data collection, feature engineering, model training, evaluation. Course capstone shipped with reproducible scripts.</p>
        <ul class="chips">
          <li>Python</li><li>NumPy</li><li>scikit-learn</li><li>Signal processing</li>
        </ul>
      </article>
    </div>
    <p class="projects__more">
      <a href="https://github.com/jakethehoffer" target="_blank" rel="noopener">More on GitHub &rarr;</a>
    </p>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
/* ---------- Projects ---------- */
.projects {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 640px) { .projects { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .projects { grid-template-columns: repeat(3, 1fr); } }

.project {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.project:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.project__name {
  font-family: var(--font-mono);
  font-size: 1rem;
  margin: 0 0 0.5rem;
  color: var(--accent);
  letter-spacing: -0.01em;
}
.project__what {
  margin: 0 0 0.5rem;
  font-weight: 500;
}
.project__why {
  margin: 0 0 0.875rem;
  color: var(--text-muted);
  font-size: 0.9375rem;
}
.projects__more {
  margin: 1.5rem 0 0;
  font-family: var(--font-mono);
  font-size: 0.875rem;
}
```

- [ ] **Step 3: Verify**

Reload. Six cards visible. Resize: one column under 640px, two columns 640–1023px, three columns at ≥ 1024px. Hover a card and it should lift slightly.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(projects): 6 featured project cards with responsive grid"
```

---

## Task 8: Experience section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="experience">`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in Experience**

Replace `<section id="experience" class="section"></section>` with:

```html
<section id="experience" class="section">
  <div class="container">
    <h2>Experience</h2>
    <ol class="timeline">
      <li class="timeline__item">
        <header class="timeline__head">
          <h3 class="timeline__role">IT Intern</h3>
          <p class="timeline__org">Lynx Equity Limited</p>
          <p class="timeline__dates">Jun 2024 &ndash; Aug 2024 &middot; Jun 2025 &ndash; Aug 2025</p>
        </header>
        <ul class="timeline__bullets">
          <li>Built a task-management system on Monday.com that streamlined communication between subsidiaries by auto-routing issues to the right workflow queue.</li>
          <li>Designed an On/Off-Boarding workflow with standardized role-based tasks, handoffs, and approvals; delivered a stakeholder demo and shipped feedback into the final product.</li>
          <li>Wrote Google Apps Script (JavaScript) to ingest multiple Excel exports into a single Google Sheet, apply pricing logic, and track unmatched keys for reconciliation; added a Sheets custom menu and logic for dynamic Excel file IDs.</li>
          <li>Built a Monday.com form that prefills user data via URL parameters, reducing setup time for new processes.</li>
          <li>Conducted DNS lookups across subsidiary domains to inventory email providers, SSL status, and other domain metadata.</li>
        </ul>
      </li>

      <li class="timeline__item">
        <header class="timeline__head">
          <h3 class="timeline__role">Independent Game Developer &mdash; Mega Tic-Tac-Toe</h3>
          <p class="timeline__org">Self-published, Unity</p>
          <p class="timeline__dates">Jan 2024 &ndash; Mar 2024</p>
        </header>
        <ul class="timeline__bullets">
          <li>Designed and programmed a Unity game on a 3&times;3 grid of linked Tic-Tac-Toe boards where each move dictates the opponent&rsquo;s next board.</li>
          <li>Shipped local + online multiplayer plus single-player vs. a Minimax-based AI with multiple difficulty levels.</li>
        </ul>
      </li>

      <li class="timeline__item">
        <header class="timeline__head">
          <h3 class="timeline__role">Design Team Member</h3>
          <p class="timeline__org">QMIND &mdash; Queen&rsquo;s AI Hub</p>
          <p class="timeline__dates">Oct 2023 &ndash; Mar 2024</p>
        </header>
        <ul class="timeline__bullets">
          <li>Trained a reinforcement-learning agent to play Blackjack alongside the team.</li>
          <li>Built a tabular Q-learning baseline with training loop and basic tests, then helped migrate the system to a Deep Q-learning version so the model could learn policies beyond a simple lookup table.</li>
        </ul>
      </li>

      <li class="timeline__item">
        <header class="timeline__head">
          <h3 class="timeline__role">Financial Analyst</h3>
          <p class="timeline__org">BMC Pharmacy</p>
          <p class="timeline__dates">Oct 2021 &ndash; Jun 2023</p>
        </header>
        <ul class="timeline__bullets">
          <li>Scoped the animal-drug compounding market opportunity across SW Ontario.</li>
          <li>Tracked monthly, quarterly, and YoY profitability and margin contribution from drug utilization, expanded services, and Rx reports.</li>
        </ul>
      </li>
    </ol>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
/* ---------- Experience / timeline ---------- */
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 1.5rem;
}
.timeline__item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
}
.timeline__head { margin-bottom: 0.75rem; }
.timeline__role {
  margin: 0;
  font-size: 1.0625rem;
  letter-spacing: -0.01em;
}
.timeline__org {
  margin: 0.125rem 0 0;
  color: var(--text);
}
.timeline__dates {
  margin: 0.125rem 0 0;
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-muted);
}
.timeline__bullets {
  margin: 0;
  padding-left: 1.25rem;
}
.timeline__bullets li { margin: 0.25rem 0; color: var(--text); }
```

- [ ] **Step 3: Verify**

Reload. Four cards stacked vertically with role / org / dates header and bulleted accomplishments. Most recent (Lynx Equity) at top.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(experience): reverse-chronological timeline of 4 roles"
```

---

## Task 9: Education + Contact + Footer

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (inside `<section id="education">`, `<section id="contact">`, and `<footer>`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)

- [ ] **Step 1: Fill in Education**

Replace `<section id="education" class="section"></section>` with:

```html
<section id="education" class="section">
  <div class="container">
    <h2>Education</h2>
    <article class="education">
      <h3 class="education__school">Queen&rsquo;s University</h3>
      <p class="education__program">BASc, Computer Engineering &middot; Expected 2027</p>
      <p class="education__gpa">Cumulative GPA 3.85 &middot; Dean&rsquo;s Scholar</p>
      <ul class="education__highlights">
        <li>Built a Python ML classifier on accelerometer data for walking vs. jumping.</li>
        <li>Developed a pathfinding algorithm in Python for autonomous rover operation.</li>
        <li>Built a Dart mobile app paired with a Bluetooth &ldquo;Smart Shoe&rdquo; for directional haptic navigation.</li>
      </ul>
    </article>
  </div>
</section>
```

- [ ] **Step 2: Fill in Contact**

Replace `<section id="contact" class="section"></section>` with:

```html
<section id="contact" class="section">
  <div class="container contact">
    <h2>Contact</h2>
    <p>Best way to reach me is email. I&rsquo;m open to internships, co-ops, and interesting side-project collaborations.</p>
    <div class="contact__links">
      <a class="btn btn--primary" href="mailto:14jakehoffman@gmail.com">14jakehoffman@gmail.com</a>
      <a class="btn" href="https://github.com/jakethehoffer" target="_blank" rel="noopener">github.com/jakethehoffer</a>
      <!-- TODO: confirm LinkedIn slug -->
      <a class="btn" href="https://www.linkedin.com/in/jakethehoffer/" target="_blank" rel="noopener">LinkedIn</a>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Fill in Footer**

Replace `<footer class="site-footer"></footer>` with:

```html
<footer class="site-footer">
  <div class="container site-footer__inner">
    <p>&copy; <span id="footer-year">2026</span> Jake Hoffman</p>
    <p class="site-footer__note">Built with HTML, CSS, and a little JS &mdash; <a href="https://github.com/jakethehoffer/website" target="_blank" rel="noopener">view source</a> &#9786;</p>
  </div>
</footer>
```

- [ ] **Step 4: Append styles**

```css
/* ---------- Education ---------- */
.education__school {
  margin: 0;
  font-size: 1.0625rem;
  letter-spacing: -0.01em;
}
.education__program {
  margin: 0.125rem 0;
  color: var(--text);
}
.education__gpa {
  margin: 0 0 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-muted);
}
.education__highlights {
  margin: 0;
  padding-left: 1.25rem;
}
.education__highlights li { margin: 0.25rem 0; }

/* ---------- Contact ---------- */
.contact__links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.625rem;
  margin-top: 1rem;
}

/* ---------- Footer ---------- */
.site-footer {
  border-top: 1px solid var(--border);
  padding: 2rem 0 3rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}
.site-footer__inner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  justify-content: space-between;
}
.site-footer p { margin: 0; }
```

- [ ] **Step 5: Verify**

Reload. Education card, Contact section with three buttons, footer at the bottom with year and "view source" link.

- [ ] **Step 6: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: education, contact, footer sections"
```

---

## Task 10: Sticky nav + mobile hamburger

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)
- Modify: `C:/Users/14jak/GitHub/website/script.js` (replace)

- [ ] **Step 1: Append nav styles**

```css
/* ---------- Header / nav ---------- */
.site-header {
  position: sticky;
  top: 0;
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: saturate(180%) blur(8px);
  -webkit-backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--border);
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
  font-weight: 600;
  color: var(--text);
}
.nav-brand:hover { text-decoration: none; }
.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  list-style: none;
  margin: 0 0 0 auto;
  padding: 0;
}
.nav-menu a {
  color: var(--text-muted);
  font-size: 0.9375rem;
}
.nav-menu a:hover { color: var(--text); text-decoration: none; }
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
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  padding: 0.375rem 0.625rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
}
.theme-toggle:hover { color: var(--text); }

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
    border-bottom: 1px solid var(--border);
    padding: 0.5rem var(--gutter);
    display: none;
  }
  .nav-menu.is-open { display: flex; }
  .nav-menu li { padding: 0.5rem 0; }
  .nav-menu a { display: block; padding: 0.25rem 0; }
}
```

- [ ] **Step 2: Replace `script.js`**

```js
(function () {
  "use strict";

  // ---------- Mobile nav ----------
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    });
    // Close the menu after tapping a link on mobile.
    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menu.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation");
      });
    });
  }

  // ---------- Footer year ----------
  const yearEl = document.getElementById("footer-year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
```

- [ ] **Step 3: Verify**

Reload. Sticky header visible with nav links on the right. Resize to < 768px: hamburger appears, nav links hide. Click hamburger → menu opens; click a link → menu closes and the page scrolls smoothly to the section.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css script.js
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(nav): sticky header with anchor links and mobile hamburger"
```

---

## Task 11: Dark theme + theme toggle

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)
- Modify: `C:/Users/14jak/GitHub/website/script.js` (append)
- Modify: `C:/Users/14jak/GitHub/website/index.html` (early `<script>` to avoid FOUC)

- [ ] **Step 1: Append dark-theme tokens**

```css
/* ---------- Dark theme ---------- */
:root[data-theme="dark"] {
  --bg: #0b1220;
  --surface: #111827;
  --surface-2: #1f2937;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --border: #1f2937;
  --accent: #60a5fa;
  --accent-hover: #93c5fd;
  --accent-contrast: #0b1220;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4), 0 1px 3px rgba(0, 0, 0, 0.25);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
}
:root[data-theme="dark"] .site-header {
  background: color-mix(in srgb, var(--bg) 80%, transparent);
}
```

- [ ] **Step 2: Add inline pre-paint theme script to `<head>`**

Place this `<script>` block in `index.html` immediately after the `<title>` and before the `<link rel="preconnect">` lines. It runs synchronously so the page paints in the correct theme on first frame (no flash).

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

- [ ] **Step 3: Append theme-toggle logic to `script.js`**

Add inside the existing IIFE (before its closing `})();`):

```js
  // ---------- Theme toggle ----------
  const themeBtn = document.querySelector(".theme-toggle");
  const labelEl = themeBtn ? themeBtn.querySelector(".theme-toggle__label") : null;

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (labelEl) labelEl.textContent = theme === "dark" ? "Light" : "Dark";
    if (themeBtn) themeBtn.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
  }

  // Reflect whatever the early-paint script applied.
  applyTheme(document.documentElement.getAttribute("data-theme") || "light");

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      try { localStorage.setItem("jh-theme", next); } catch (e) {}
      applyTheme(next);
    });
  }
```

- [ ] **Step 4: Verify**

Reload. Click the "Theme" button in the nav — colors invert to dark. Reload again — the page stays dark (persisted to `localStorage`). Open DevTools → Application → Local Storage; confirm `jh-theme = "dark"`. Toggle back to light; reload; stays light. In a fresh incognito window, the theme should match the system preference.

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css script.js index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(theme): dark mode with localStorage persistence and FOUC-free preload"
```

---

## Task 12: Scroll fade-in animations

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (append)
- Modify: `C:/Users/14jak/GitHub/website/script.js` (append)

- [ ] **Step 1: Append animation styles**

```css
/* ---------- Reveal on scroll ---------- */
.reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.45s ease-out, transform 0.45s ease-out;
  will-change: opacity, transform;
}
.reveal.is-visible {
  opacity: 1;
  transform: none;
}
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1; transform: none; transition: none; }
}
```

- [ ] **Step 2: Append observer logic to `script.js`**

Add inside the existing IIFE:

```js
  // ---------- Reveal on scroll ----------
  const targets = document.querySelectorAll("main > section");
  targets.forEach((el) => el.classList.add("reveal"));

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-visible"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -10% 0px" }
    );
    targets.forEach((el) => io.observe(el));
  }
```

- [ ] **Step 3: Verify**

Reload. The hero fades up on first paint; scroll down and each subsequent section fades up as it enters the viewport. Toggle "Reduce motion" in OS settings (or DevTools → Rendering → Emulate CSS `prefers-reduced-motion`); reload — sections appear immediately with no animation.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css script.js
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: scroll fade-in with prefers-reduced-motion fallback"
```

---

## Task 13: Initials avatar SVG

**Files:**
- Create: `C:/Users/14jak/GitHub/website/assets/avatar.svg`
- Delete: `C:/Users/14jak/GitHub/website/assets/.gitkeep` (no longer needed)
- Modify: `C:/Users/14jak/GitHub/website/index.html` (swap initials span for `<img>`)
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (tidy avatar rule)

- [ ] **Step 1: Create `assets/avatar.svg`**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-label="Jake Hoffman avatar placeholder">
  <circle cx="100" cy="100" r="100" fill="currentColor" opacity="0.12" />
  <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-opacity="0.25" stroke-width="2" />
  <text x="100" y="118" text-anchor="middle" font-family="JetBrains Mono, ui-monospace, monospace" font-size="80" font-weight="600" fill="currentColor" letter-spacing="-4">JH</text>
</svg>
```

- [ ] **Step 2: Delete the placeholder**

```bash
rm "C:/Users/14jak/GitHub/website/assets/.gitkeep"
```

- [ ] **Step 3: Replace the hero avatar in `index.html`**

Find:

```html
<div class="hero__avatar" aria-hidden="true">
  <!-- Replaced by assets/avatar.svg in Task 13 -->
  <span class="hero__avatar-initials">JH</span>
</div>
```

Replace with:

```html
<div class="hero__avatar" aria-hidden="true">
  <img src="assets/avatar.svg" alt="" width="160" height="160" />
</div>
```

- [ ] **Step 4: Adjust avatar CSS**

In `styles.css`, replace the existing `.hero__avatar` rule with:

```css
.hero__avatar {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  overflow: hidden;
  color: var(--accent);
  box-shadow: var(--shadow-sm);
  background: var(--surface-2);
}
.hero__avatar img { width: 100%; height: 100%; }
```

Remove the now-unused `.hero__avatar-initials` rule.

- [ ] **Step 5: Verify**

Reload. The "JH" initials avatar renders from the SVG file (right-click → "View image" should open the SVG). Toggle the theme — the SVG's `currentColor` adapts.

- [ ] **Step 6: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add assets/avatar.svg index.html styles.css
git -C "C:/Users/14jak/GitHub/website" rm assets/.gitkeep
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(assets): initials placeholder avatar SVG"
```

---

## Task 14: SEO — JSON-LD Person schema + Open Graph

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (`<head>`)

- [ ] **Step 1: Insert Open Graph tags**

Just before the closing `</head>`, add:

```html
<meta property="og:type" content="profile" />
<meta property="og:title" content="Jake Hoffman — Computer Engineering @ Queen's University" />
<meta property="og:description" content="3rd-year Computer Engineering student. Builds trading agents, arbitrage daemons, web platforms, and ML pipelines." />
<meta property="og:url" content="https://jakethehoffer.github.io/website/" />
<meta name="twitter:card" content="summary" />
```

- [ ] **Step 2: Insert JSON-LD Person schema**

Just before `</head>`, after the OG tags:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Jake Hoffman",
  "email": "mailto:14jakehoffman@gmail.com",
  "url": "https://jakethehoffer.github.io/website/",
  "alumniOf": {
    "@type": "CollegeOrUniversity",
    "name": "Queen's University"
  },
  "jobTitle": "Computer Engineering Student",
  "knowsAbout": [
    "Python", "JavaScript", "C", "C++", "C#", "Java", "Dart", "SQL",
    "Next.js", "Supabase", "Unity", "Playwright", "FastAPI",
    "Machine learning", "Automation", "Trading systems"
  ],
  "sameAs": [
    "https://github.com/jakethehoffer",
    "https://www.linkedin.com/in/jakethehoffer/"
  ]
}
</script>
```

- [ ] **Step 3: Verify**

Reload. Open DevTools → Elements; expand `<head>`; both blocks should be present. Paste the JSON-LD into Google's Rich Results Test (https://search.google.com/test/rich-results) and confirm "Person" is detected without errors.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(seo): Open Graph tags and schema.org Person JSON-LD"
```

---

## Task 15: Export resume.pdf from the source .docx

**Files:**
- Create: `C:/Users/14jak/GitHub/website/resume-source.docx` (copy of the user's source)
- Create: `C:/Users/14jak/GitHub/website/resume.pdf` (generated)

- [ ] **Step 1: Copy the source `.docx` into the repo**

```bash
cp "C:/Users/14jak/OneDrive/Desktop/Jake's new resume (2).docx" "C:/Users/14jak/GitHub/website/resume-source.docx"
```

(The `.gitignore` from Task 1 ignores `*.docx` except `resume-source.docx`, so this file commits and other working `.docx` copies don't.)

- [ ] **Step 2: Convert to PDF with LibreOffice via the docx skill helper**

```bash
python "C:/Users/14jak/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/40995ef3-d08f-45ed-bc0b-2aeeab63ddeb/a71cadf8-88e2-4b1e-8a5b-7de236af5ddf/skills/docx/scripts/office/soffice.py" --headless --convert-to pdf --outdir "C:/Users/14jak/GitHub/website" "C:/Users/14jak/GitHub/website/resume-source.docx"
```

The output should be `resume-source.pdf` in the website directory.

- [ ] **Step 3: Rename to `resume.pdf`**

```bash
mv "C:/Users/14jak/GitHub/website/resume-source.pdf" "C:/Users/14jak/GitHub/website/resume.pdf"
```

- [ ] **Step 4: Verify**

Open `resume.pdf` in a PDF viewer. Confirm it renders cleanly (no missing fonts, no garbled characters where smart quotes used to be). Then in the website, click the "Download Resume (PDF)" button — the browser should download or open the same PDF.

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add resume-source.docx resume.pdf
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: include resume.pdf generated from source docx"
```

If the script in Step 2 isn't available, fall back to opening the `.docx` in Word and "Save As → PDF" manually, then continue at Step 3.

---

## Task 16: README + final smoke tests + Lighthouse

**Files:**
- Create: `C:/Users/14jak/GitHub/website/README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# website

Single-page resume for Jake Hoffman. Plain HTML, CSS, and a touch of vanilla JS &mdash; no framework, no build step.

## Serve locally

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/>.

You can also just double-click `index.html` &mdash; it works file:// too.

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo, then in **Settings → Pages**, source = `main` branch / root.

## Replace the placeholders

- `assets/avatar.svg` &mdash; swap with a real headshot at `assets/avatar.jpg` (and update the `<img src>` in `index.html`).
- LinkedIn URL &mdash; search `index.html` for the `TODO: confirm LinkedIn slug` comment.
- `resume.pdf` &mdash; regenerate from a fresh `.docx` whenever the resume changes.

## Files

- `index.html` &mdash; single-page document, semantic markup, JSON-LD Person schema.
- `styles.css` &mdash; design tokens, light + dark themes, all section styles.
- `script.js` &mdash; mobile nav, theme toggle, IntersectionObserver fade-in, footer year.
- `assets/avatar.svg` &mdash; initials placeholder.
- `resume.pdf` &mdash; downloadable resume.
- `docs/superpowers/` &mdash; design spec and implementation plan.
```

- [ ] **Step 2: Run final smoke tests**

Serve locally:

```bash
python -m http.server 8000 --directory "C:/Users/14jak/GitHub/website"
```

Then in a browser at <http://localhost:8000>:
- Confirm every section renders and is reachable via the nav anchors.
- Toggle theme; reload; confirm persistence.
- Resize to 360, 768, 1280 widths; confirm responsive behavior.
- Tab through the page using only the keyboard; confirm focus is visible on every interactive element and the "Skip to content" link works.
- Click "Download Resume (PDF)" → PDF downloads / opens.

- [ ] **Step 3: Run Lighthouse**

In Chrome DevTools → Lighthouse → "Analyze page load" with all four categories checked. Target ≥ 95 on each of Performance, Accessibility, Best Practices, SEO. Note any sub-95 score and the suggested fix in the commit message.

- [ ] **Step 4: Validate HTML**

Paste the served HTML into https://validator.w3.org/nu/ (or the offline equivalent). Confirm zero errors. Warnings about the preconnect / Google Fonts pattern are fine.

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add README.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add README with local-serve and deploy notes"
```

---

## Task 17: Update .ai-sync handoff

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/.ai-sync/state.md` (via the helper script — do not edit the file directly)

- [ ] **Step 1: Run the handoff command**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "Built single-page resume website at C:/Users/14jak/GitHub/website/. Static HTML/CSS/JS, light+dark theme, scroll fade-in, 6 featured projects, JSON-LD Person schema, exported resume.pdf from source docx." -FilesChanged "index.html, styles.css, script.js, assets/avatar.svg, resume.pdf, resume-source.docx, README.md, docs/superpowers/specs/2026-05-12-resume-website-design.md, docs/superpowers/plans/2026-05-12-resume-website.md" -TestsRun "Manual: opened in Chrome/Firefox, theme toggle persistence, mobile hamburger at <768px, keyboard tab order, prefers-reduced-motion. Lighthouse pending review on user side." -Blockers "LinkedIn slug is placeholder (jakethehoffer); confirm before publishing." -NextSteps "1) Confirm LinkedIn URL. 2) Drop real headshot at assets/avatar.jpg and update <img src>. 3) Push to GitHub and enable Pages."
```

- [ ] **Step 2: Verify**

`cat "C:/Users/14jak/GitHub/website/.ai-sync/state.md"` — confirm the "Latest Decisions" and "Next Steps" sections have updated text, and an entry appears in the Activity Log.

---

## Closing checklist

After Task 17:
- [ ] All 17 task headings checked off above.
- [ ] `git -C "C:/Users/14jak/GitHub/website" log --oneline` shows ~17 commits with clean, conventional messages.
- [ ] LinkedIn TODO comment still present (until Jake confirms the slug).
- [ ] No `*.docx` working files committed except `resume-source.docx`.
