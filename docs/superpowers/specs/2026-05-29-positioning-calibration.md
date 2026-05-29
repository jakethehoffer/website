# v2.24 — positioning calibration: lead with engineering (review #4 + #7)

Date: 2026-05-29

## Why

Two remaining adversarial-review items, both about how the portfolio
*reads* rather than what it does:

- **#4 (AI-orchestration framing).** Project copy foregrounds the AI
  tooling — "six scheduled **Claude Code** routines", "**subagent**
  review", `claude code` as a skill chip. In 2026 this volunteers the
  exact doubt a reviewer already has about a new grad: *does he
  engineer, or just prompt?* The work is strong engineering; the
  framing undersells it.
- **#7 (overclaim).** The hero metric "**3 production systems**" doesn't
  survive an interview probe — none of the three serve real users or
  money (trader is paper-only, the arbitrage daemon has no stated
  outcome, tax-rebalance is read-only).

This is re-emphasis and calibration toward what's defensible — not
erasure. Mentions that describe the *product* ("AI swing-trading
agent", "LLM-driven SDR") stay; those are legitimately impressive and
distinct from "built with Claude".

## Changes

In `projects.yml` (cards + résumé bullets regenerate from it):

- trader `what` + résumé bullet: "six scheduled Claude Code routines"
  → "six scheduled, idempotent routines" (foreground the architecture).
- trader `chips`: drop trailing "claude code" (a tool, not a stack
  skill).
- tax-rebalance `body` + résumé bullet: "fresh-context subagent
  review" / "two-stage subagent review" → "two-stage independent
  review" (keeps the process-rigor signal; drops the AI specificity).

In `index.html` (static, not generated):

- hero metric "3 production systems" → "3 unattended systems"
  (true — all three run unattended; doesn't claim users/revenue).
- trader case-study lede "Six scheduled Claude Code routines…" →
  "Six scheduled, idempotent routines…" (matches the case-study body,
  which already says "six small, idempotent routines").

## Explicitly NOT done

- **Skills TypeScript / Next.js** (unsupported by any portfolio work):
  flagged to the user, not edited — deleting claimed skills requires
  knowing whether the user has them off-site. User decision.
- **#5 (narrowness):** the About section deliberately commits to the
  finance/infra/trading niche, so the Python-heavy focus is intentional
  positioning, not a defect. No change.
- **#2 (ship for real):** user action.

## Acceptance criteria

1. No "Claude Code" / "claude code" / "subagent" remains in
   `projects.yml` or the generated `index.html` cards, nor in the
   case-study lede. ("AI swing-trading agent" and "LLM-driven SDR"
   remain — product descriptions, intentionally kept.)
2. Hero metric reads "3 unattended systems".
3. Résumé regenerates: trader + tax-rebalance bullets updated; still
   1 page, 4 hyperlinks.
4. Generators idempotent; `public-safety` CI passes; tag `v2.24`.

## Out of scope

- TS/Next.js skills decision (user), #5, #2.
- Any layout/design change.
