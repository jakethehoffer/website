# Remove FUSE-Web from the Site — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

FUSE-Web is a hidden project that should not be publicly attributed
to Jake on the site. Every direct and indirect reference needs to be
removed cleanly: project card, screenshot asset, hero metrics that
count it, About/boot/OG copy that gestures at it, related skill chips
that only existed because of FUSE-Web, and the refresh-meta script
that polls its GitHub repo.

## Goal

A site that looks like FUSE-Web was never on it, with internally
consistent copy and metrics, while preserving every other recent
improvement (v2.0 through v2.6).

## Non-Goals

- Removing FUSE-Web from any commit message, spec, plan, or other
  historical document under `docs/superpowers/`. Those are durable
  design artifacts; rewriting history would invalidate the narrative.
- Changing the v2 visual aesthetic.
- Adding a replacement project card. We go from 6 cards to 5; the
  layout breathes a little. No filler.
- Changing case studies. Neither case study (trader, Odds Aggregator)
  references FUSE-Web.

## Concrete Changes

### 1. `index.html` — content surgery

**Drop the FUSE-Web project card.** Remove the entire `<article class="project">…</article>` block that wraps the FUSE-Web entry.

**Hero metrics:** `4 production systems` → `3 production systems`.
The 3 are `trader` (paper, runs daily), `Odds Aggregator` (24/7
production), and the operational stack around them (refresh-meta
workflow, OG image renderer, etc.).

**Boot sequence body line 2:**
> i build production-grade software — trading agents, arbitrage
> daemons, web platforms, and ml pipelines.

becomes:

> i build production-grade software — trading agents, arbitrage
> daemons, and ML pipelines.

**About section first paragraph:**
> …trading agents that paper-trade the S&P 500, an arbitrage daemon
> ingesting ten bookmakers every minute, web platforms with their
> tests wired up before the first commit.

becomes:

> …trading agents that paper-trade the S&P 500, an arbitrage daemon
> ingesting ten bookmakers every minute, and the automation glue that
> keeps both running unattended.

The phrase "automation glue" is honest — it covers the refresh-meta
workflow, the OG renderer, the daemon orchestration on the host, the
journaling layer. It's not made up.

**Skills section — Tools & Frameworks line:**
> git · next.js · supabase · fastapi · playwright · unity · sqlite · alembic · monday.com · google apps script

becomes:

> git · next.js · fastapi · playwright · unity · sqlite · alembic · monday.com · google apps script

(Remove Supabase — only used in FUSE-Web. Keep Next.js — also in
goon-maps. Keep Playwright — also in arbitrage.)

**JSON-LD `knowsAbout`:** remove `"Supabase"`.

### 2. Asset deletion

`assets/projects/fuse-web.webp` — delete (~70 KB).

### 3. `scripts/refresh-meta.mjs`

Remove the `FUSE-Web` entry from the `REPOS` array:

```js
const REPOS = [
  { owner: "jakethehoffer", name: "trader",    key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage", key: "arbitrage.last_commit" },
];
```

This also stops the workflow from trying to hit FUSE-Web every
Monday and logging a confusing `[skip]` for an org repo the PAT
doesn't need access to.

### 4. `scripts/render-og-image.py`

Update the body_lines:

```python
body_lines = [
    "> i build production-grade software — trading",
    "> agents, arbitrage daemons, and ML",
    "> pipelines.",
]
```

After updating, re-run the script to regenerate `assets/og-image.png`.

### 5. `README.md`

The PAT setup section currently lists FUSE-Web as a repo to grant
access to. Update it to list only `trader` and `arbitrage` (matches
what Jake actually configured).

## File Layout Delta

```
website/
├── index.html                            MODIFIED (card removed, copy edits, JSON-LD)
├── assets/projects/
│   └── fuse-web.webp                     DELETED
├── assets/og-image.png                   REGENERATED (new body copy)
├── scripts/
│   ├── refresh-meta.mjs                  MODIFIED (drop FUSE-Web entry)
│   └── render-og-image.py                MODIFIED (drop "web platforms" line)
├── README.md                             MODIFIED (PAT setup)
└── docs/superpowers/specs/
    └── 2026-05-12-remove-fuse-web.md     THIS DOC
```

## Page weight impact

Before (v2.6): live page weight ~202 KB.
After (v2.7):

- Remove `fuse-web.webp` (was on live path via FUSE-Web `<img>`):
  −70 KB
- Minor HTML reduction from removing the card markup: −1 KB
- Net: live page weight ~131 KB. Comfortably under 200 KB target.

## Verification

- `grep` checks: zero matches for `FUSE-Web`, `fuse-web`,
  `Supabase`, `Vitest` (case-insensitive) in `index.html`,
  `scripts/refresh-meta.mjs`, `scripts/render-og-image.py`,
  `README.md`. (Spec / plan files keep the references because
  they're historical.)
- Live HTML: 5 project cards (not 6).
- Hero metrics line: "3 production systems".
- About section reads naturally without "web platforms".
- Refresh OG image: matches the new boot copy.
- Lighthouse mobile spot-check: still 100/100/100/100; ideally
  Performance score holds and weight savings show up in Speed
  Index / LCP.

## Risks

- **"Automation glue" might read vague.** Trade-off: more vague
  than a concrete project name, but defensible and accurate. Worth
  it to avoid leaving the third clause empty or replacing it with
  something less honest.
- **Bumping a skill from the list could feel like I'm hiding work.**
  Supabase/Vitest only existed on this site because of FUSE-Web. If
  Jake works in them elsewhere later, easy to add back.
- **OG image regen creates a binary diff that needs to land in the
  same release.** Plan calls this out as one of the tasks.
- **Skill cards in the JSON-LD don't render visually but affect SEO
  / structured-data parsers.** Removing Supabase from `knowsAbout`
  is consistent with the visible Skills section. No risk.

## Out of Scope (YAGNI)

- Adding a sixth project to replace FUSE-Web in the grid. The 5-card
  grid (3 columns at ≥ 640px → 2-and-3 or 3-and-2 layout) reads
  cleanly. No filler.
- Modifying the timeline experience entries (FUSE-Web wasn't a job;
  it was a project — and nothing in the timeline mentions it).
- Touching the case studies (already FUSE-free).
- Adding a placeholder image / "private project" badge. Cleaner to
  just remove it entirely.

## Success Criteria

- Live site shows no reference to FUSE-Web by any spelling.
- Metrics, About, boot sequence, OG card all read consistently with
  3 (not 4) production systems.
- Refresh-meta workflow runs without trying to hit FUSE-Web.
- Lighthouse stays at 100/100/100/100 (mobile spot-check).
- Page weight drops by the expected ~70 KB.
