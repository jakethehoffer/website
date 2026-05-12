# Resume Website v2 — "Engineering Log" Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved direction, pending written-spec review
**Supersedes:** `2026-05-12-resume-website-design.md` (v1 — kept in repo as design history)

## Why v2 exists

v1 was a competent but generic developer-portfolio template — sticky nav,
chip rows, three-column card grid. It passes the recruiter 7-second test but
fails the *memorability* test. Per the research, "the best portfolios answer
one question convincingly: can this person build things that work?" and v1
buries that answer in template chrome.

v2 ditches the template look and leans into the *substance* of Jake's
portfolio. His work is overwhelmingly backend systems, daemons, automation,
and trading infrastructure — the terminal aesthetic isn't a costume, it
matches the work. The target audience is tech / quant / fintech recruiters
(Jane Street, Citadel, HRT, RBC Capital Markets, Optiver, plus standard
tech), where terminal-flavored portfolios read as a strong cultural signal.

## Goal

A single-page resume that:
1. Looks **distinctive in a recruiter's tab stack of 200** without being
   gimmicky or hard to read.
2. Spotlights the trading / arb / automation work that uniquely positions
   Jake for quant and fintech roles.
3. Stays mobile-first, fast, accessible, and ATS-friendly.
4. Keeps the "no build step required" promise — the freshness script is
   strictly opt-in.

## The "Engineering Log" concept

The site reads like a curated changelog from someone who actually runs
production systems. Mono type, dark default, warm-amber accent. Project
entries look like `git log` lines with status indicators. The hero opens
with a brief boot-sequence animation that types out the bio, then settles
into a static, readable state. One flagship project (`trader`) gets a
long-form case study with an ASCII architecture diagram.

Critically: the terminal vibe is **flavor, not literalism**. Body copy is
mono but rendered at 15–16px with generous line-height — comfortable to
read on a phone. There are no fake `>` prompts in front of every line of
content. The aesthetic is "engineer who has taste," not "1999 hacker."

## Information Architecture

Same sections as v1, in the same order. The redesign is visual + content,
not structural.

1. **Hero** — boot sequence + metrics strip + CTAs
2. **About** — 2–3 paragraphs (rewritten tighter, more voice)
3. **Skills** — three groups, mono chips
4. **Featured Projects** — six git-log-style entries
5. **Case study: trader** — flagship deep-dive with ASCII diagram (NEW)
6. **Experience** — git-log-style timeline
7. **Education** — Queen's, GPA, Dean's Scholar, key coursework
8. **Contact** — email, GitHub, LinkedIn
9. **Footer** — `$ _` prompt with timestamp

## Visual Design

### Type system — all mono

- **Family:** JetBrains Mono Variable (already loaded; switch to variable for
  finer weight control). Fallback chain: `ui-monospace, SFMono-Regular,
  Menlo, monospace`.
- **Weight-driven hierarchy:** no font mixing. Body 400, mid-emphasis 500,
  display 600–700.
- **Body size:** 15px at < 640px, 16px ≥ 640px. Line-height **1.7** for
  readability.
- **Display:** `clamp(2.5rem, 6vw, 4.5rem)` for the hero name. Hero metric
  values: 1.5rem 700.

### Color — dark default

```
--bg:        #0a0e14   /* terminal near-black */
--bg-elev:   #11161e   /* card surface */
--bg-grid:   #1c2330   /* hairline dividers */
--text:      #d6dee6   /* warm off-white body */
--text-dim:  #8a96a3   /* muted */
--text-mute: #5a6573   /* dates, meta */
--accent:    #f5b342   /* warm amber — primary */
--accent-2:  #7fbf7f   /* sage green — "SHIPPED" status */
--accent-3:  #e07a7a   /* warm red — reserved for errors / 404 only */
--cursor:    #f5b342   /* blinking caret */
```

### Light mode — "parchment"

A second theme is available but secondary. Cream paper (`#f5efe4`),
near-black text (`#1a1f26`), same amber accent but darkened (`#a86a14`)
for AA contrast. Same toggle behavior as v1 (`localStorage` key
`jh-theme`).

### Motion

- **Boot sequence:** types out 3 lines over ~1.4 seconds total, then
  settles. Plays once per `sessionStorage` flag. Skippable via "skip" link
  shown for the first 800ms. Disabled entirely under
  `prefers-reduced-motion: reduce` — end state shown immediately.
- **Cursor blink:** the `_` in the footer and the closing caret after the
  hero boot use a 1.06s opacity blink (CSS keyframes).
- **Section reveals:** kept from v1 (IntersectionObserver fade-up). Tuned
  shorter (300ms instead of 450ms) so it doesn't feel theatrical alongside
  the boot sequence.
- **Project card hover:** 1px lift + amber left-border accent slide-in.

### Layout

- **Max content width:** 920px (down from 1080px). Tighter column reads
  more like a long-form essay.
- **Section vertical rhythm:** 6rem top/bottom on ≥ 768px (up from v1's
  4rem). Generous whitespace is doing real work here.
- **Section dividers:** thin `--bg-grid` hairline plus a small mono label
  in the top-left of each section (`# about`, `# skills`, etc.).
- **Grid:** Projects 2 columns at ≥ 640px (was 3 at ≥ 1024px in v1 —
  larger cards, less wall-of-text feel). 1 column on mobile.

## Component specs

### Hero

**Layout:** single column, left-aligned. No avatar (v1's initials avatar
telegraphed "unfinished").

**Boot sequence — 3 typed lines:**

```
$ whoami
> jake hoffman · computer engineering @ queen's · class of 2027

$ summary
> i build production-grade software — trading agents, arbitrage daemons,
> web platforms, and ml pipelines. paper-trading the s&p 500 on real
> infrastructure; running a 24/7 odds daemon across ten bookmakers.

$ contact_
```

The `$ whoami` prompt and the response are pre-rendered (visible
immediately for accessibility and `prefers-reduced-motion`). The
typewriter effect animates **only the response text** of lines 1 and 2,
then types out the literal string `contact` on line 3. After line 3, a
**static** CTA row replaces the blinking cursor:

```
[ email ]  [ github ]  [ linkedin ]  [ resume.pdf ↓ ]
```

**Metrics strip** (below the CTAs, one row, mono):

```
//  4 production systems    10 bookmakers ingested    6 scheduled agents    dean's scholar
```

The strip uses `--text-dim` and a `//` comment-prefix. Values are
hard-coded; this isn't live data.

**Skip affordance:** A small `skip ▸` link in the top-right of the hero,
visible only while the boot animation is active.

### Project cards

Each card is a single column with:

1. **Status row** — colored dot + `STATUS` label + `last commit: 3d ago`
   on the right (mono, dim, real data from refresh script).
2. **Title row** — project name (700 weight) + small inline link icon to
   GitHub.
3. **One-line what** — 1 sentence, body weight.
4. **Body** — 2–3 sentences of why / impact.
5. **Metrics row** (where applicable) — `//  10 books · 6 sports · 24/7`
6. **Tech chips** — small mono, no border, just dim text separated by `·`.
7. **Optional screenshot** — full-width below the chips. FUSE-Web has
   real screenshots in the repo (`worksheet-overview.png`,
   `screenshot-comments-tasks.png`, `screenshot-workflow-toggles.png`);
   copy one into `assets/projects/`. Projects without a screenshot show a
   small mono "output sample" code block instead (e.g. a redacted Telegram
   alert payload for Odds Aggregator, a tiny terminal log for trader).

**Status assignment:**
- ●amber `ACTIVE` — `trader`, `Odds Aggregator`, `FUSE-Web`
- ●green `SHIPPED` — `Mega Tic-Tac-Toe`, `Smart Shoe`, `Walking/Jumping Classifier`

### Case study — trader (NEW)

A full-width section between Projects and Experience, ~300 words. Subhead:

```
# case study: trader

  a 24/7 ai swing-trading agent for the s&p 500, driven by six
  scheduled claude code routines on ibkr paper + finnhub news.
```

Then an **ASCII architecture diagram** showing the 6 routines and their
data flow:

```
   ┌──────────────────┐    ┌──────────────────┐
   │  scan_premarket  │───▶│      gate        │
   └──────────────────┘    └────────┬─────────┘
                                    │
                                    ▼
   ┌──────────────────┐    ┌──────────────────┐
   │     monitor      │◀───│   place_orders   │
   └────────┬─────────┘    └──────────────────┘
            │
            ▼
   ┌──────────────────┐    ┌──────────────────┐
   │       eod        │───▶│     journal      │
   └──────────────────┘    └──────────────────┘
```

Followed by 3 paragraphs:
- **The problem** — why scheduled agents instead of a monolith
- **The risk model** — kill switch, paper-mode default, 30-day gate
- **What's next** — graduation to live, broker abstraction (IBKR /
  Alpaca), backtester replay

Sources: `docs/superpowers/specs/2026-04-20-ai-trading-agent-design.md`
in the `trader` repo.

### Experience — git-log timeline

```
  ●  IT Intern · Lynx Equity Limited                  jun 2024 – aug 2025
     │  Monday.com workflow automation, Google Apps Script ingest
     │  delivered an on/off-boarding workflow shipped to stakeholders
     │  DNS / SSL inventory across subsidiary domains

  ●  Independent Game Developer · Mega Tic-Tac-Toe    jan – mar 2024
     │  Unity, C#, Minimax AI, local + online multiplayer

  ●  Design Team · QMIND — Queen's AI Hub             oct 2023 – mar 2024
     │  reinforcement-learning blackjack agent (tabular Q → Deep Q)

  ●  Financial Analyst · BMC Pharmacy                 oct 2021 – jun 2023
     │  market scoping in SW Ontario, profitability / margin tracking
```

The leading `●` and the `│` continuation bars are real `border-left` CSS,
not text characters, so they scale crisply at any zoom.

### Skills, Education, Contact

Same content as v1, restyled to mono + the v2 hierarchy. Skills groups get
section labels styled like `# languages`, `# tools & frameworks`,
`# domains`. Contact buttons match the hero CTAs.

### Footer

```
$ _    last_deployed: 2026-05-12T03:37:00Z         © jake hoffman
```

The `_` blinks. `last_deployed` is filled in by the refresh script (and
otherwise stays as a frozen string).

## Technical Decisions

- **Same stack as v1:** static HTML/CSS/JS. No framework, no bundler. One
  `index.html`, one `styles.css`, one `script.js`.
- **New: `scripts/refresh-meta.mjs`** — optional Node script that:
  1. Calls `gh api repos/jakethehoffer/<repo>` for each featured project.
  2. Reads `pushed_at` and converts to a human-readable "Nd ago" / date.
  3. Search-and-replaces sentinel markers in `index.html` like
     `<!-- META:trader.last_commit -->`. Markers carry a default value so
     un-refreshed builds still render sensibly.
  Also updates the footer's `last_deployed` timestamp.
- **No new external dependencies.** Boot sequence is hand-written
  vanilla JS (CSS-only typing animations are brittle for multi-line).
- **Performance budget:** same as v1 — total page weight < 200 KB
  excluding `resume.pdf`. Project screenshots are the only new weight;
  compress + serve as WebP with PNG fallback. Target Lighthouse ≥ 95 on
  Performance / Accessibility / Best Practices / SEO.
- **Accessibility:** the boot animation must not be the only way to access
  hero content. Pre-render the static end-state in HTML; the JS *replaces*
  it with the empty animated state on `DOMContentLoaded` only if motion is
  allowed. Screen readers see the full bio immediately. Skip-to-content
  link kept. All status dots have `aria-label`s.
- **SEO:** JSON-LD Person schema, OG tags, meta description all kept from
  v1.

## File Layout (v2)

```
website/
├── index.html                         rewritten
├── styles.css                         rewritten (mono-only system)
├── script.js                          rewritten (adds boot sequence)
├── scripts/
│   └── refresh-meta.mjs               NEW: optional pre-deploy metadata
├── resume.pdf                         unchanged
├── resume-source.docx                 unchanged
├── assets/
│   ├── projects/
│   │   ├── fuse-web.png               NEW: from FUSE-Web/screenshot-*.png
│   │   └── (others added later)
│   └── (no avatar.svg — removed)
├── docs/superpowers/
│   ├── specs/
│   │   ├── 2026-05-12-resume-website-design.md       v1 (history)
│   │   └── 2026-05-12-resume-website-v2-design.md    THIS DOC
│   └── plans/
│       ├── 2026-05-12-resume-website.md              v1 (history)
│       └── 2026-05-12-resume-website-v2.md           pending
└── README.md                          updated for refresh-meta script
```

## Content Updates

### About — rewritten with voice

```
Computer engineering at Queen's. I'm most at home building systems
that run unattended — trading agents that paper-trade the S&P 500,
an arbitrage daemon ingesting ten bookmakers every minute, web
platforms with their tests wired up before the first commit.

What I'm best at: turning a messy real-world domain (insurance
catastrophe management, sports-book pricing, broker order flow)
into clean abstractions and a service that doesn't wake me up at
3am.

Looking for an internship / co-op where I can ship production
code, ideally somewhere with hard correctness requirements:
trading, infrastructure, financial systems, dev tools.
```

This signals: target audience, what I actually like building, what
I'm best at. More voice than v1's anodyne summary.

### Project copy — quick refresh

The v1 copy is mostly fine; just tighten and add metrics rows. The
project bodies don't change much — the *presentation* is the upgrade.

## Out of Scope (YAGNI)

- Per-project sub-pages or routing (one flagship case study inline is
  enough).
- Sound effects (no boot beep — terminal-cosplay territory).
- ASCII-art project logos for cards without screenshots (overruled in
  favor of "small output sample" code blocks — faster to author,
  no per-project asset to maintain).
- Live GitHub-API fetch on every pageload (the optional refresh script
  bakes data in; rate-limits and runtime fetches not worth the
  complexity).
- A second light theme beyond "parchment" — one is enough.
- Custom 404 / Easter eggs — out of scope for v2, can layer in v3.

## Risks and Trade-offs

- **Boot animation reads as gimmicky if too long.** Mitigated by capping
  at ~1.4s total, providing skip, and disabling under reduced-motion.
  Static end-state is the source of truth.
- **All-mono body could fatigue readers on a long page.** Mitigated by
  the 1.7 line-height, 16px size, and conservative content length.
- **Amber-on-near-black has been done.** True — but pairing it with
  parchment light mode and `git log` content patterns is the
  differentiator. The aesthetic is the medium, not the message.
- **Quant/tech bias.** If Jake applies to a Big Four accounting firm,
  this site won't help. Acceptable — the resume.pdf still does that work.
- **Refresh script depends on `gh` CLI.** Acceptable — `gh` is already
  authenticated in this environment, and the script is optional.

## Success Criteria

A recruiter at a trading firm scanning this in 7 seconds:
- Sees the amber `●ACTIVE trader` line within the first viewport.
- Reads "24/7 ai swing-trading agent" and "ibkr paper" in their
  scanning glance.
- Drops out of "filter mode" into "consider mode."

A senior engineer reading the site for 90 seconds:
- Reads the `trader` case study.
- Sees the architecture diagram and infers that Jake has thought about
  scheduling, risk gates, and journaling.
- Forms a real opinion of his technical judgment, not just his
  credentials.

Lighthouse:
- Performance ≥ 95
- Accessibility ≥ 95 (boot animation correctly accessible)
- Best Practices ≥ 95
- SEO ≥ 95

## Placeholders That Need Real Values Before Going Live

- `last_commit` strings on project cards: rendered with defaults; refresh
  via `scripts/refresh-meta.mjs` whenever Jake wants fresh dates.
- Real screenshots for projects beyond FUSE-Web: optional, can be added
  one at a time as Jake takes them.
- Headshot: still no real one. v2 removes the avatar entirely from the
  hero, so this is no longer a blocker.
