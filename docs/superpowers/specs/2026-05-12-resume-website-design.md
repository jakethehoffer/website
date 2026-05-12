# Resume Website — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved — implementation pending

## Goal

A single-page personal resume website for Jake Hoffman that recruiters can scan
in under 10 seconds on mobile and that gives technical readers enough depth to
believe Jake builds real software. Lives in the `website/` repo; deploys cleanly
to GitHub Pages or any static host.

## Non-Goals

- No SPA framework, no build step, no bundler.
- No backend, contact form, analytics, blog, or CMS.
- No 3D / WebGL gimmicks. Polished and conservative beats clever for the
  audience (internship recruiters, hiring managers at financial / enterprise
  shops, plus tech startups).
- No CSS frameworks (Tailwind, Bootstrap). Hand-written CSS keeps the file
  count small and the page fast.

## Audience and Success Criteria

**Primary audience:** internship/co-op recruiters and technical hiring managers.

**The 7-second test (above-the-fold on mobile, no scroll required):**
1. Name
2. Role label ("Computer Engineering Student @ Queen's University")
3. One-sentence value prop
4. Three CTAs: Email, GitHub, Resume PDF
5. LinkedIn icon button (and one more above-the-fold tech-stack chip row)

**The 30-second test (one scroll):** reader sees at least one featured project
card with an impact line and a tech-stack chip row.

## Information Architecture

Single page, sections in this order with sticky top nav:

1. **Hero**
   - Avatar (initials placeholder; replaced when user drops a real image)
   - `<h1>` "Jake Hoffman"
   - `<p>` role line
   - 1-sentence summary
   - CTA buttons: Email, GitHub, LinkedIn, Download Resume (PDF)
2. **About** — 2–3 sentences from the resume's Summary of Qualifications.
3. **Skills** — Three groups of chips:
   - *Languages:* Python, Java, C, C#, C++, JavaScript, Dart, SQL
   - *Tools & Frameworks:* Git, Next.js, Supabase, Unity, Playwright, FastAPI,
     SQLite, Monday.com, Google Apps Script, Excel
   - *Domains:* Machine learning, web development, automation, trading systems,
     mobile apps
4. **Featured Projects** — 6 cards in a responsive grid (3 cols ≥ 1024px,
   2 cols ≥ 640px, 1 col below). Each card has:
   - Project name
   - One-sentence *what it is*
   - One-sentence *impact / why it's interesting*
   - 3–5 tech chips
   - Optional GitHub link (if public)

   The 6 projects:
   - **trader** — 24/7 AI swing-trading agent for S&P 500 equities, driven by
     six scheduled Claude Code routines on IBKR (paper) + Finnhub news.
   - **Odds Aggregator** — Production arbitrage daemon: ingests odds from 10
     bookmakers across 6 sports, detects cross-book arbs, pushes alerts to
     Telegram + Discord. 24/7 on Windows host.
   - **FUSE-Web** — Next.js + Supabase web platform for insurance catastrophe
     management, with role-based accounts, workflow toggles, and a resource
     center. Built tests with Vitest + Playwright.
   - **Mega Tic-Tac-Toe** — Unity game built on a 3×3 grid of linked
     Tic-Tac-Toe boards. Local + online multiplayer; single player vs.
     Minimax-based AI opponent with multiple difficulty levels.
   - **Smart Shoe Navigation App** — Dart mobile app that pairs via Bluetooth
     to a "Smart Shoe" and delivers turn-by-turn directions via on-screen
     prompts and directional haptic feedback in the shoe.
   - **Walking/Jumping Classifier** — Python ML pipeline classifying
     accelerometer data as walking vs. jumping. Built end-to-end: data
     collection, feature extraction, training, evaluation.

   Below the grid: "More on GitHub →" link surfacing the rest (crypto
   triangular-arbitrage bot, money / PSA Pokémon flipping pipeline, YouTube
   automation pipeline, Workshop-Arcade, claude-usage-widget, goon-maps).

5. **Experience** — Timeline-style cards, reverse chronological:
   - **IT Intern, Lynx Equity Limited** (Jun 2024 – Aug 2024; Jun 2025 – Aug 2025)
   - **Independent Game Developer — Mega Tic-Tac-Toe** (Jan 2024 – Mar 2024)
   - **Design Team Member, QMIND – Queen's AI Hub** (Oct 2023 – Mar 2024)
   - **Financial Analyst, BMC Pharmacy** (Oct 2021 – Jun 2023)
   Bullet points lifted from the resume, quantified where possible.

6. **Education** — Queen's University, BASc Computer Engineering, expected
   2027. GPA 3.85, Dean's Scholar. Coursework highlights: rover pathfinding,
   ML accelerometer classifier, Bluetooth Smart Shoe mobile app.

7. **Contact** — Email link, GitHub, LinkedIn. Small footer with year +
   "Built with HTML, CSS, and a little JS — view source ☺".

## Visual Design

**Mode:** light by default, dark-mode toggle in top-right that respects
`prefers-color-scheme` and persists to `localStorage` under key
`jh-theme`.

**Type:**
- Body: Inter (400, 500, 600, 700) via Google Fonts with `display=swap`.
- Mono: JetBrains Mono (400, 500) for code-like chips and project names.
- Fallbacks: `system-ui, -apple-system, sans-serif` and `ui-monospace, monospace`.

**Color tokens (light theme):**
- `--bg`: `#ffffff`
- `--surface`: `#f8fafc`
- `--text`: `#0f172a`
- `--text-muted`: `#475569`
- `--border`: `#e2e8f0`
- `--accent`: `#2563eb`
- `--accent-hover`: `#1d4ed8`

**Color tokens (dark theme):**
- `--bg`: `#0b1220`
- `--surface`: `#111827`
- `--text`: `#f1f5f9`
- `--text-muted`: `#94a3b8`
- `--border`: `#1f2937`
- `--accent`: `#60a5fa`
- `--accent-hover`: `#93c5fd`

**Motion:**
- Sections fade-up on enter via `IntersectionObserver` (translate 16px → 0,
  opacity 0 → 1, 400ms ease-out). Disabled when
  `prefers-reduced-motion: reduce`.
- Project cards lift 2px and gain subtle shadow on hover.
- Smooth scroll on nav anchors.

**Responsive:**
- Mobile-first, breakpoints at 640px and 1024px.
- Hamburger nav under 640px.
- Hero CTAs wrap to two rows on narrow screens.

## Technical Decisions

- **Static HTML/CSS/JS** — no framework, no build step.
- **Single CSS file** with CSS custom properties for theming.
- **Single JS file** for theme toggle, mobile nav, and scroll fade-in.
- **SEO / parsability:**
  - Semantic HTML5 (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`,
    `<footer>`).
  - `<meta>` description and Open Graph tags.
  - JSON-LD `schema.org/Person` block embedding name, email, alumniOf,
    knowsAbout, sameAs (GitHub, LinkedIn).
- **Accessibility:**
  - Skip-to-content link.
  - All interactive elements keyboard reachable; visible `:focus-visible` ring.
  - Color contrast ≥ WCAG AA in both themes.
  - `alt` text on the avatar, `aria-label` on icon-only buttons.
- **Performance:**
  - No external JS libraries.
  - Google Fonts preconnect + `display=swap`.
  - Self-hostable: structured so fonts could be moved local later without
    rewrites.
  - Total page weight target: < 200 KB excluding `resume.pdf`.

## File Layout

```
website/
├── index.html            single page, ~300 lines incl. JSON-LD
├── styles.css            ~400 lines, light + dark via custom properties
├── script.js             ~80 lines: theme toggle, nav, IntersectionObserver
├── resume.pdf            exported from "Jake's new resume (2).docx"
├── assets/
│   └── avatar.svg        initials placeholder ("JH")
└── README.md             one-paragraph repo note + how to serve locally
```

## Content Sources

- Resume content: `C:/Users/14jak/OneDrive/Desktop/Jake's new resume (2).docx`,
  extracted during the design phase.
- Project descriptions: drawn from each repo's `README.md` (FUSE-Web,
  arbitrage, trader, Workshop-Arcade, claude-usage-widget, crypto, money,
  youtube) and the resume.

## Placeholders That Need Real Values Before Going Live

- **LinkedIn URL** — placeholder `https://www.linkedin.com/in/jakethehoffer/`
  (matches the GitHub handle pattern). Marked with HTML comment
  `<!-- TODO: confirm LinkedIn slug -->`.
- **GitHub username** — confirmed `jakethehoffer` from local repo remotes
  (e.g. `github.com/jakethehoffer/trader`). Used directly, no TODO needed.
- **Avatar image** — initials-only SVG until Jake drops a headshot at
  `assets/avatar.jpg`.
- **resume.pdf** — generated from the `.docx` via LibreOffice during
  implementation; user can replace with a freshly exported version any time.

## Out of Scope (YAGNI)

- Multi-page routing.
- Project detail sub-pages (one card + GitHub link is enough).
- Per-project screenshots / animated previews.
- Contact form, captcha, mail server.
- Analytics, cookie banner, GDPR copy.
- CI / linting / Lighthouse automation (run manually if needed).

## Testing Approach

Manual smoke tests post-implementation:
1. Open `index.html` directly in Chrome and Firefox; confirm it renders.
2. Run `python -m http.server 8000` and open `http://localhost:8000`; confirm
   the same.
3. Test dark-mode toggle persists across reload.
4. Test hamburger nav on viewport widths 360, 768, 1280.
5. Tab through the page with keyboard only; confirm focus order and visible
   focus.
6. Run Lighthouse (Chrome devtools) — target ≥ 95 in Performance,
   Accessibility, Best Practices, SEO.

## Risks and Trade-offs

- **No framework** means we hand-write the responsive nav and theme system;
  cost is ~80 lines of JS. Benefit: zero build, zero dep updates, hosts
  anywhere.
- **Self-hosted fonts deferred** — Google Fonts is the fast path. If Jake
  later wants offline / privacy-first, fonts can be downloaded and the
  `<link>` swapped.
- **Single-page** loses URL-level deep linking into projects; mitigated by
  anchor links (`#projects`, `#experience`, etc.) in the nav.
