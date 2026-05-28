# v2.22 — resume curation (priority + cap), the durable half of review #6

Date: 2026-05-28

## Why

Adversarial review #6 has two halves:
1. **Curation** — end the `PARAGRAPHS_TO_DROP` page-fit whack-a-mole.
   Every project added since v2.16 forced hand-tuned cuts elsewhere
   (SUMMARY, EXPERIENCE, EDUCATION bullets) to keep the resume on one
   page. The list is now ~75 lines of accumulated trim hacks.
2. **Reproducibility** — the resume's source is a gitignored binary
   (`resume-source.docx`); lose it and the resume can't be regenerated.

This cycle delivers **half 1 (curation)** — the higher-value half,
because it's the *recurring felt pain* and it *prevents* the problem
from recurring. Half 2 (reproducibility) is deferred with a clear
recommendation (see below): it involves a privacy tradeoff that's the
user's call, not the agent's.

## The curation model

Replace "include every project's bullets, then trim collateral
elsewhere to fit" with declarative selection:

- Each project gets a `resume_priority` (int; higher = more important).
- A `RESUME_MAX_PROJECTS` cap (= 4) limits how many projects reach the
  resume's PERSONAL PROJECTS section.
- `build_new_section()` selects the top-N candidates by priority, then
  emits them in `projects.yml` display order (so the resume's project
  order matches the website's).

Effect: adding a 5th resume-eligible project no longer forces cuts to
EXPERIENCE/EDUCATION — it competes with the other projects for the N
slots. The lowest-priority project drops out automatically. The static
sections (SUMMARY/EDUCATION/EXPERIENCE) become stable.

### Priorities

| project        | resume_priority | on resume? (cap 4) |
|----------------|-----------------|--------------------|
| trader         | 100             | yes                |
| arbitrage      | 90              | yes                |
| tax-rebalance  | 80              | yes                |
| equity-arbs    | 70              | yes                |
| trades-agency  | 65              | no (resume: null)  |
| mega-tictactoe | 40              | no (no resume blk) |
| smart-shoe     | 30              | no (no resume blk) |
| walking-jumping| 20              | no (no resume blk) |

Current candidates (projects with a `resume:` block): trader,
arbitrage, tax-rebalance, equity-arbs = exactly 4. With cap 4, all four
are selected, emitted in projects.yml order — **byte-identical to the
current resume. Zero regression.** The cap is preventive: it changes
nothing today and stops future whack-a-mole.

## Zero-regression guarantee

`RESUME_MAX_PROJECTS = 4` and there are exactly 4 candidates, so the
selected set and its order are unchanged. The regenerated docx/PDF must
match the current one (same 4 projects, same bullets, 1 page). Verified
by content + page-count check.

## Secondary changes

- `scrub_metadata`: also clear `created` / `modified` / `revision`
  (defensive — so the docx carries no edit-history dates if it is ever
  committed). Cheap; keeps the privacy posture strong either way.
- `PARAGRAPHS_TO_DROP`: frozen. A comment documents that it is a
  historical one-time-removal ledger (BMC Pharmacy, low-signal Lynx
  bullets) and that **page-fit cuts must NOT be added here anymore** —
  use `resume_priority` + the cap instead.
- README: document the curation model in the "Adding or editing
  projects" section.

## Reproducibility — deferred, with a recommendation (NOT done here)

The docx is gitignored for metadata privacy. Two ways to make the
resume reproducible, both the user's call:

- **Option A — commit a scrubbed docx.** Requires scrubbing all three
  metadata locations (core.xml ✓ already, app.xml, custom.xml) to be
  truly privacy-clean. The content itself is already public (it's the
  PDF). Lowest effort once scrubbing is complete; downside is a binary
  in git + per-run binary noise.
- **Option B — from-scratch builder.** Generate the docx from tracked
  text (extend projects.yml + a new `resume-static.yml` for
  contact/summary/education/experience) via python-docx. Fully clean
  and diffable; downside is real risk of regressing the tuned
  formatting (fonts, margins, spacing), so it needs careful
  parity verification.

Recommendation: **Option B** long-term (clean, diffable, no binary),
but it's a larger, higher-risk effort that deserves its own cycle and
explicit go-ahead. Not started here.

## Acceptance criteria

1. `projects.yml`: every project has a `resume_priority`.
2. `refresh-resume.py`: `RESUME_MAX_PROJECTS` constant;
   `build_new_section()` selects top-N by priority in display order.
3. The regenerated resume PDF is **unchanged**: trader, Odds
   Aggregator, tax-rebalance, equity-arbs present; trades-agency
   absent; 1 page; 4 hyperlinks.
4. `scrub_metadata` clears created/modified/revision (verified by
   reading them back as cleared/sentinel).
5. `PARAGRAPHS_TO_DROP` has a "frozen ledger" comment; no entries
   removed (avoids any risk on a non-curated docx).
6. README documents the priority/cap model.
7. Generators idempotent; `public-safety` CI passes; tag `v2.22`.

## Out of scope

- Committing the docx / from-scratch builder (reproducibility — user
  decision, deferred with recommendation above).
- Restoring the v2.19-trimmed EXPERIENCE bullets (needs the docx
  source work; minor content).
- #2 (ship a project for real — user action).
