# Odds Aggregator Case Study — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

The case-study section is the strongest signal the site has —
"this person thinks about systems, not just builds them." Right now
that signal is one entry deep (`trader`). Adding a second case study
on Odds Aggregator doubles that signal and showcases the project
that is arguably the most recruiter-relevant in the portfolio:
genuinely in production, 24/7 traffic, 10 bookmakers, real arbitrage
edges. Especially valuable for quant / trading-firm recruiters.

## Goal

Add a second case-study section, structurally identical to the
existing `trader` case study, covering Odds Aggregator. ~300 words of
prose plus one ASCII data-flow diagram. Reuses every existing CSS
class. No JS, no new assets.

## Non-Goals

- Reshaping the existing trader case study.
- Adding a new nav entry. The existing `case_study` anchor still
  scrolls to the first one; readers scroll naturally to the second.
- Per-section deep dive linking to other pages.
- Live data widgets (alert counts, uptime, etc.).
- A third case study or any other section change.

## Concrete Change

A single new `<section>` inserted into `index.html` between the
existing `<section id="case-study">` and `<section id="experience">`.

```html
<section id="case-study-arb" class="section">
  <div class="container">
    <p class="section__label"># case study</p>
    <h2>odds aggregator — a 24/7 cross-book arbitrage daemon</h2>
    <p class="case-study__lede">…lede…</p>
    <pre class="diagram" aria-label="…">…ascii diagram…</pre>
    <div class="case-study__prose">
      <h3>The problem</h3>
      <p>…</p>
      <h3>The system</h3>
      <p>…</p>
      <h3>What I learned / what's next</h3>
      <p>…</p>
    </div>
  </div>
</section>
```

### Content

**Lede:**

> Ten bookmakers, six sports, polled every minute. When prices on the
> same outcome diverge enough to clear the vig and transaction
> friction, an alert fires to Telegram and Discord within seconds of
> the gap opening. Runs unattended on a Windows host with
> replay-tooling for postmortems.

**Diagram** (uses the same HTML-entity box-drawing characters as the
trader diagram so the v2 CSS `.diagram` class renders it identically):

```
   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
   │  scraper pool   │──▶│   normalize     │──▶│   arb detector  │
   │  (10 books)     │   │  (canonical     │   │   (cross-book,  │
   │                 │   │   markets)      │   │    per-event)   │
   └────────┬────────┘   └─────────────────┘   └────────┬────────┘
            │                                            │
            ▼                                            ▼
   ┌─────────────────┐                          ┌─────────────────┐
   │  SQLite +       │◀─────────────────────────│ alert pipeline  │
   │  Alembic        │                          │ (Telegram /     │
   │  (journal)      │                          │  Discord)       │
   └─────────────────┘                          └─────────────────┘
```

**Subsection 1 — The problem:**

> A real-time cross-book ingester sounds simple and isn't. Each book
> formats markets differently, prices go stale within seconds, and
> books vary wildly in scrape-friendliness — FanDuel removed itself
> with bot detection; Pinnacle requires auth. An arb that's real on
> paper is often gone by the time you see it; an arb that looks
> "available" is often a stale price. The hard part isn't math, it's
> *fresh* math.

**Subsection 2 — The system:**

> Per-book ingest workers feed a normalization layer that
> canonicalizes markets (so "Moneyline" on BetMGM resolves to the
> same key as "h2h" on Pinnacle). The arb detector walks canonical
> odds for each event, converts to implied probabilities, and flags
> any cross-book combination where Σ implied < 1 minus a configurable
> edge floor. SQLite with Alembic handles schema evolution — over ten
> migrations so far. A separate journal table records every raw
> scrape, which means failures and false-positives are replayable
> against the exact inputs that produced them.

**Subsection 3 — What I learned / what's next:**

> Production scrapers fail in interesting ways. The most
> underestimated work was *defensive ingestion* — per-book health
> scoring, automatic backoff on bot-detection, intermittent-cluster
> tolerance. The math layer was small; the operations layer was most
> of it. Next step: a paper-trading recorder that attributes realized
> P&L to historical alerts without actually placing bets, so the
> alert pipeline can be calibrated against real outcomes.

### Fact-checks

Verified against the repo at `C:/Users/14jak/GitHub/arbitrage/`:
- 10 bookmakers, 6 sports — confirmed in `README.md`.
- SQLite + Alembic — confirmed (`alembic/versions/` has 10+ files
  including `20260123_0006_presets_table.py`,
  `20260124_0007_alerts_tables.py`,
  `20260227_0008_alert_hit_notify_fields.py`).
- Per-book health scoring — confirmed by Alembic migration
  `15f257daafcc_add_health_score_and_temporarily_*.py`.
- FanDuel removed for bot detection, Pinnacle requires auth —
  confirmed in `README.md` ("FanDuel was removed March 23, 2026 …").
- Telegram + Discord alert sink — confirmed in `README.md` ("push to
  Telegram/Discord").
- "10+ migrations" claim — currently 10 migration files; safe.

## File Layout Delta

```
website/
├── index.html                            MODIFIED (one new section, ~55 lines)
└── docs/superpowers/specs/
    └── 2026-05-12-odds-aggregator-case-study.md   THIS DOC
```

No CSS changes, no JS changes, no new assets. The new section
reuses `.section`, `.section__label`, `.case-study__lede`,
`.diagram`, `.case-study__prose`, and the `<code>` styling within
`.case-study__prose code` for inline keywords.

## Page weight projection

+3–4 KB of HTML in `index.html`. Live page weight 162 KB → ~166 KB.
Comfortable under the 200 KB budget.

## Verification

- Confirm the new section renders cleanly between the trader case
  study and Experience on both desktop and mobile breakpoints.
- Confirm ASCII diagram alignment stays correct in both dark and
  parchment themes.
- Confirm the page still passes the v2.4 Lighthouse score on a
  fresh post-deploy audit (target: 100/100/100/100, no regression).

## Risks

- **Two consecutive case-study sections might feel like a long
  content block.** Mitigated by the natural `.section` padding rhythm
  and clear `<h2>` differentiation. If it reads as slog, the spec for
  v2.6 can trim one or both.
- **All technical claims need to be true.** Fact-checks above confirm
  each claim is grounded in the actual repo state.
- **Diagram spacing may render slightly differently if the font
  metrics shift.** Mitigated because the page uses the same
  JetBrains Mono variable WOFF2 already verified on the trader
  diagram.

## Out of scope (YAGNI restatement)

- Nav menu changes
- Per-bookmaker logos / per-sport icons
- Live alert feed widget
- Linking to the arbitrage repo's `CLAUDE.md` or other docs (the
  repo is private and not directly relevant to a portfolio reader)
- Reformatting the existing trader case study

## Success Criteria

After deployment:
- A reader scrolling past the trader case study lands on a second,
  structurally-mirrored case study with the same quality of detail.
- All technical claims are accurate and verifiable.
- Lighthouse re-audit shows no regression from v2.4's 100/100/100/100.
- Page weight stays under 200 KB live.
