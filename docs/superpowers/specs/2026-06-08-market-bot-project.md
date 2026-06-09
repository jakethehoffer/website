# v2.26 — add market-bot (website-only SHIPPED negative result)

Date: 2026-06-08

## Why

`market-bot` (C:\Users\14jak\GitHub\market-bot) is a new finished
project: a telemetry-first market-making feasibility bot for NDAX
(OSC-registered Canadian crypto exchange). It collects real 24/7 venue
data, runs it through a 9-criterion pre-trade synthesizer, and produces
a `READY`/`NOT_READY`/`BLOCKED` verdict per pair. After 7 covered days
of gap-free data, the verdict came back **`NOT_READY` across all 75
NDAX CAD pairs** — a rigorous, data-backed refutation of retail-passive
market making at this venue/capital tier (flat 0.20%/fill = 40 bps
round-trip; break-even needs 80–100 bps of captured spread). The
project's own framing: a negative verdict is a *valid, complete
deliverable*, not a failure.

It's the best-engineered of the three negative results (vs equity-arbs'
offline backtest and trades-agency's market test): real REST+WebSocket
data infrastructure, SQLite WAL store, queue-aware paper-fill model,
bootstrap validation of the one surviving candidate (HYPE/CAD, rejected
as a thin-sample artifact), 254 unit + 4 integration tests, systemd
24/7 cloud deployment.

## Decisions

**Website: add as a SHIPPED card.** Real, recent, rigorous work belongs
in the portfolio. Not on GitHub yet (404), so it uses the `private`
treatment (no 404 link, `private` pill) like trader/arbitrage/
tax-rebalance. URL points at github.com/jakethehoffer/market-bot and
resolves once pushed. No on-page case study → no case-study CTA.

**Resume: website-only (`resume: null`).** Keep equity-arbs as the
resume's single negative-result slot (review #3). Rationale: equity-arbs
is publicly clickable (review #1 verifiability) and market-bot is not
pushed yet. market-bot gets `resume_priority: 72` (above equity-arbs'
70) so it is *documented* as the stronger negative result and a future
resume swap is a one-line change (add a `resume:` block → it
auto-displaces equity-arbs in the top-4 cap). Until then, `resume: null`
keeps it off the resume and the resume PDF is unchanged this cycle.

## Strategic flag (recorded, not blocking)

This is the **third** rigorous negative result (equity-arbs, trades-
agency, market-bot) and the portfolio still has **zero** projects with a
real positive outcome (real users / real money / real results). Framed
right, three disciplined "I did the analysis and walked away rather than
deploy capital on a losing strategy" projects is a genuine strength for
quant/risk/trading roles. But it is also a pattern, and it widens the
gap that the #2 review lever (ship one thing for real) exists to close.
Recommendation to the user: do not add a *fourth* refutation before
there is a shipped win to balance them; the highest-value next move
remains taking one existing system to a real outcome.

## Card content

- key: `market-bot`, name: `market-bot`, status: `shipped`,
  `private: true`, url: github.com/jakethehoffer/market-bot
- `hardcoded_date: "verdict delivered · 2026"` (on-brand: the verdict
  IS the deliverable)
- `resume_priority: 72`, `resume: null`
- Placed at the FRONT of the shipped group in projects.yml (most recent,
  June 2026) — i.e. immediately after tax-rebalance, before
  trades-agency.
- `what` / `body` / `metrics` (75 pairs · 7 days 24/7 data · 254 tests)
  / `chips` (python · sqlite/wal · websocket · structlog · pydantic ·
  typer) / `sample` (a synth verdict excerpt).

## Acceptance criteria

1. `projects.yml` has a market-bot entry: shipped, private:true,
   resume:null, resume_priority 72, placed first in the shipped group.
2. After `generate-cards.py`, index.html has 9 project cards; market-bot
   renders with a `private` pill and NO github 404 link.
3. The resume PDF is **byte-identical** to before (market-bot is
   resume:null; equity-arbs remains the single negative result). 1 page,
   4 hyperlinks.
4. Generators idempotent; `public-safety` CI passes; tag `v2.26`.

## Out of scope

- Putting market-bot on the resume (one-line swap available on request).
- A market-bot case study.
- #2 (ship a project for real — user action).
