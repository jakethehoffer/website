# v2.21 — curate the resume to one negative-result project

Date: 2026-05-28

## Why

Adversarial review finding #3: two abandoned projects in the resume's
top five (equity-arbs + trades-agency) reads as a *pattern* ("starts
things, talks himself out of finishing") rather than as maturity. One
well-told negative result signals judgment; two dilute each other —
and the effect is sharpest on the resume, where the ratio is 2-of-5
and the format is scannable.

## What ships

Drop **trades-agency** from the resume. Keep **equity-arbs** as the
single negative-result story.

- equity-arbs is the stronger keep: quantified ceiling (~0.6%/yr),
  76 tests, six analysis arcs — a rigorous, engineering-dense negative
  result that's on-target for the stated roles (trading / infra /
  financial systems).
- trades-agency **stays on the website** in full (card #4 of 8). The
  website's browsable grid carries the range/product-judgment story;
  the resume just won't double up on abandonments.

Result: resume PERSONAL PROJECTS goes 5 → 4 (trader, Odds Aggregator,
tax-rebalance, equity-arbs) — three ACTIVE + one rigorous negative
result.

## How

- `projects.yml`: set `resume: null` on the trades-agency entry. The
  `build_new_section()` reader already skips entries without a
  `resume:` block, so it drops out of NEW_SECTION automatically.
- `scripts/refresh-resume.py` `PARAGRAPHS_TO_DROP`: the trades-agency
  role + bullet were inserted into the docx in v2.19 and the
  walk-anchor only *inserts*, never removes — so they must be trimmed:
  - add `"trades-agency (Python"` (role line)
  - widen the existing `"Toronto AI-receptionist + lead-gen venture:"`
    entry to `"Toronto AI-receptionist + lead-gen venture"` (no colon)
    so it matches the current tightened bullet form.

## Known limitation (defer to #6)

The two bullets cut in v2.19 to *make room* for trades-agency (QMIND
Deep-Q detail, Mega TTT Minimax) were trimmed out of the gitignored
`resume-source.docx` and cannot be cleanly restored by the current
script (it trims + appends; it can't re-insert original body text).
Restoring them needs the review's #6 work: make `resume.pdf`
reproducible from a tracked template instead of mutating a gitignored
binary. Out of scope here. The freed vertical space from dropping
trades-agency simply becomes breathing room (a less-crammed page).

## Acceptance criteria

1. `projects.yml` trades-agency has `resume: null`; its website card
   fields (what/body/metrics/chips/sample) are unchanged.
2. The regenerated resume PDF contains trader, Odds Aggregator,
   tax-rebalance, equity-arbs in PERSONAL PROJECTS — and **not**
   trades-agency.
3. equity-arbs is present (sole negative-result project).
4. PDF stays 1 page; 4 hyperlinks intact.
5. The website still shows the trades-agency card (8 cards total).
6. Generators idempotent; `public-safety` CI passes; tag `v2.21`.

## Out of scope

- The #6 curation/reproducibility refactor (resume_priority, max-N
  cap, template-based docx). Flagged as the natural follow-up.
- Any change to the website's project grid.
- #2 (ship a project for real) — user action.
