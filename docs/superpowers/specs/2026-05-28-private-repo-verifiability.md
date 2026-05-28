# v2.20 — fix the verifiability inversion for private repos

Date: 2026-05-28

## Why

Adversarial review finding #1 (the biggest issue): the three flagship
ACTIVE projects — trader, arbitrage, tax-rebalance — are all **private
on GitHub**, so the project-card name links 404 for any cold visitor.
The only repos that resolve are the two **abandoned** projects
(equity-arbs, trades-agency). A recruiter clicking the impressive work
hits dead ends; the work they *can* see is the abandoned experiments.
This actively subtracts trust.

Making the repos public is the user's decision (needs secret-scrubbing)
and is out of scope here. This cycle does the honest code-side fix:
stop promising a click the site can't honor, and route those cards to
the proof that survives privacy — the on-page case studies.

## What ships

A `private` treatment in the project-card generator:

1. **No 404 link.** A private project's `<h3>` renders as plain text
   (like the already-URL-less Smart Shoe / Walking-Jumping cards),
   not an `<a>` to a private repo.
2. **A `private` pill** next to the name, so the absence of a link is
   explained ("the code exists, it's just not public") rather than
   looking like an oversight.
3. **A case-study CTA** (`[ read case study ↓ ]`) on cards that have an
   on-page case study (trader → `#case-study`, arbitrage →
   `#case-study-arb`). This converts a dead end into a path to the
   deepest proof on the site.
4. The `last commit: …` auto-meta signal **stays** — the PAT can read
   private repos, so the card still shows active development.

Public projects (equity-arbs, trades-agency, Mega TTT) are unchanged.

## Schema additions to projects.yml

Two new optional fields:

- `private: true` — marks a repo as private. Generator renders no link
  on the name and shows the `private` pill. Defaults to absent/false.
- `case_study: "#anchor"` — if set, the card renders a
  `[ read case study ↓ ]` CTA linking to that on-page anchor.
  Defaults to absent/null.

Applied:
- `trader`: `private: true`, `case_study: "#case-study"`
- `arbitrage`: `private: true`, `case_study: "#case-study-arb"`
- `tax-rebalance`: `private: true` (no case study → no CTA)

## generate-cards.py changes

- `render_name(project)`: if `project.get("private")`, render plain
  text name + `<span class="project__private">private</span>`. Else
  keep existing behavior (link when `url`, plain text otherwise).
- New `render_case_study_cta(project)`: returns the CTA `<p>` when
  `case_study` is set, else None. Appended after sample/media/cta in
  `render_card`.

## CSS

Add `.project__private` — a small muted pill (reuses existing border /
radius / color tokens). No other CSS changes; the case-study CTA reuses
`.project__cta` + `.btn`.

## Acceptance criteria

1. `projects.yml` has `private: true` on trader, arbitrage,
   tax-rebalance; `case_study` on trader + arbitrage.
2. After `generate-cards.py`, none of the three private projects render
   an `<a href="https://github.com/...">` on the name.
3. trader and arbitrage cards render a `[ read case study ↓ ]` CTA
   pointing to `#case-study` / `#case-study-arb`.
4. Each private card shows a `private` pill.
5. The `data-meta` last-commit span is unchanged (auto-meta still works).
6. Public projects (equity-arbs, trades-agency, Mega TTT, etc.) are
   byte-unchanged except where intentionally edited.
7. Generator stays idempotent.
8. `public-safety` CI passes; tag `v2.20`.

## Out of scope

- Making the repos public (user decision + secret-scrubbing).
- Demo GIFs / screenshots (need user-recorded assets).
- The resume side — no resume change this cycle; the PDF doesn't link
  repos, so the 404 problem is web-only.
- Curation refactor (#6) and shipping-for-real (#2/#3) from the review.
