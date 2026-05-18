# v2.17 — add tax-rebalance project to website + resume

Date: 2026-05-18

## Why

`tax-rebalance` (github.com/jakethehoffer/tax-rebalance, private) is a
new portfolio project: a Python async CLI that monitors Canadian
TFSA + RRSP portfolio drift and emails weekly digests. Spec-driven
TDD development with two-stage subagent review, 117 tests, ruff-clean,
CI on Py 3.11 + 3.13.

It belongs on the site alongside `trader` and `Odds Aggregator` as an
ACTIVE personal project, and on the resume under PERSONAL PROJECTS.

## Scope

Three hand-edits in this cycle:

1. New `<article class="project">` card in `index.html` (position 3,
   after Odds Aggregator).
2. New REPOS entry in `scripts/refresh-meta.mjs` so the weekly cron
   updates the last-commit timestamp going forward.
3. New `("role", ...)` + 2 bullet entries in `scripts/refresh-resume.py`
   `NEW_SECTION`, plus whatever cut(s) are needed to keep the PDF at
   1 page.

Plus: regenerate `resume.pdf`.

## Website card content

Position: between Odds Aggregator (ends around index.html line 189)
and Mega Tic-Tac-Toe (starts around line 191).

Structure mirrors the existing ACTIVE-status cards:

```
<article class="project">
  <header class="project__head">
    <span class="status status--active" role="img" aria-label="Status: active"></span>
    <span class="project__status-label">ACTIVE</span>
    <span class="project__last-commit" data-meta="tax-rebalance.last_commit">last commit: today</span>
  </header>
  <h3 class="project__name"><a href="https://github.com/jakethehoffer/tax-rebalance" target="_blank" rel="noopener">tax-rebalance</a></h3>
  <p class="project__what">Python CLI that monitors a Canadian TFSA + RRSP portfolio for allocation drift and emails weekly digests with cost-aware rebalance verdicts.</p>
  <p class="project__body">Read-only &mdash; never places trades; the user takes the action in their broker. Async end-to-end: SQLAlchemy 2.0 + aiosqlite, httpx, aiosmtplib, jinja2, structlog. Spec-driven development &mdash; every feature traces to a written design spec and a 21-task TDD implementation plan executed task-by-task with fresh-context subagent review (spec compliance, then code quality).</p>
  <p class="project__metrics"><span class="metrics__prefix">//</span> 117 tests &middot; ruff-clean &middot; ci on py 3.11 + 3.13</p>
  <p class="project__chips">python &middot; async sqlalchemy 2 &middot; httpx &middot; aiosmtplib &middot; jinja2 &middot; pytest</p>
  <pre class="project__sample" aria-label="Example weekly digest"><span class="sample__dim">// example weekly digest excerpt</span>
<span class="sample__dim">[TFSA]</span> VEQT 60.2% vs target 60.0%  &rarr; <span class="sample__ok">hold</span> (drift &lt;2%)
<span class="sample__dim">[TFSA]</span> XBB  19.4% vs target 20.0%  &rarr; <span class="sample__hi">buy $312</span> (cost-aware)
<span class="sample__dim">[RRSP]</span> VTI  39.8% vs target 40.0%  &rarr; <span class="sample__dim">hold</span> (cost &gt; expected benefit)</pre>
</article>
```

Notes on the sample:
- The numbers/tickers are illustrative, not pulled from a real run.
  Labelled as `// example weekly digest excerpt` to be consistent with
  the v2.13 example-labelling convention on `trader` and `Odds
  Aggregator` cards.
- The three rows demonstrate three verdicts: hold (within drift band),
  buy (rebalance needed), hold-cost-aware (the project's
  distinguishing feature — cost-aware verdicts that decline trades
  whose commission > expected benefit).

## refresh-meta.mjs change

Add one entry to the `REPOS` array:

```javascript
const REPOS = [
  { owner: "jakethehoffer", name: "trader",        key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage",     key: "arbitrage.last_commit" },
  { owner: "jakethehoffer", name: "tax-rebalance", key: "tax-rebalance.last_commit" },   // NEW
];
```

**PAT scope note:** The `META_REFRESH_TOKEN` PAT was set up with read
access on `trader` and `arbitrage` only. Until the PAT is extended to
include `tax-rebalance`, the script will log `[skip] jakethehoffer/tax-rebalance: ...`
and the timestamp stays at the hardcoded `last commit: today` value.
This is a one-time GitHub Settings edit the user needs to perform
post-merge.

## Resume change

Add four new items to `NEW_SECTION` in `refresh-resume.py`, after the
existing Odds Aggregator entries:

```python
("role",    "tax-rebalance (Python · async SQLAlchemy 2 · httpx · pytest)"),
("bullet",  "Canadian TFSA + RRSP portfolio drift monitor — "
            "emails weekly digests with cost-aware rebalance verdicts. "
            "Read-only; never places trades."),
("bullet",  "Spec-driven TDD: 21-task plan executed task-by-task with "
            "two-stage subagent review. 117 tests, zero ruff violations, "
            "CI on Python 3.11 + 3.13. Questrade IQ API with OAuth "
            "refresh-token rotation."),
```

These insert via the existing `NEW_SECTION` machinery in `main()`. The
section is already idempotent (`already = find_para(... PERSONAL PROJECTS)`
shortcut), so adding entries to the list requires extending the
shortcut's behavior: if PERSONAL PROJECTS exists but a `tax-rebalance`
role line does not, append the missing entries. See "idempotency
strategy" below.

## Idempotency strategy

The existing PERSONAL PROJECTS construction is "all-or-nothing":
it either inserts the whole section or skips entirely (when the
heading is found). This breaks down when adding new entries.

Fix: change the idempotency check from "section exists" to "each entry
exists." Walk through NEW_SECTION; for each entry, check if it's
already present in the doc (by exact text match for role/bullet/heading);
if missing, insert. This generalizes the current behavior so future
adds work the same way.

This is a structural improvement to `refresh-resume.py` — within scope
because adding tax-rebalance is the trigger.

## Page-fit strategy

Adding a role + 2 bullets adds ~3 lines to PERSONAL PROJECTS. The PDF
was at 1 page after v2.16's QMIND-bullet cut. The new content will
probably tip to 2 pages.

Compensating cut, in order of preference:

1. **SUMMARY bullet 4** ("Collaborates with non-technical teammates...")
   — generic soft-skill line, lowest signal on the page.
2. **trader resume bullet 2** ("Paper-traded against SPY with kill-switch...")
   — the website case study tells this story in full; the resume
   reader can click through.
3. **OA resume bullet 2** ("Ingest → normalize → detect cross-book arbs...")
   — same reasoning.

If cut #1 is enough, stop. If not, take cut #2.

Cuts are encoded by adding prefixes to `PARAGRAPHS_TO_DROP` in
`refresh-resume.py`, same as v2.16's QMIND bullet drop.

## Acceptance criteria

1. `index.html` contains a 6th `<article class="project">` block with
   `data-meta="tax-rebalance.last_commit"`, ACTIVE status, link to the
   GitHub repo, the project__what / __body / __metrics / __chips /
   __sample structure, inserted between Odds Aggregator and Mega TTT.
2. `scripts/refresh-meta.mjs` has 3 entries in REPOS (trader,
   arbitrage, tax-rebalance).
3. `scripts/refresh-resume.py` `NEW_SECTION` contains the tax-rebalance
   role + 2 bullets after Odds Aggregator.
4. Running the refresh script is idempotent: a second run on a
   freshly-updated docx produces no net change (no duplicates, no
   missing entries).
5. The regenerated `resume.pdf` is 1 page.
6. The tax-rebalance role line appears at role-template indent in the
   PDF, matching trader and Odds Aggregator.
7. `public-safety` CI passes.
8. Tag `v2.17` pushed.

## What this does NOT do

- Build a config-driven generator that auto-adds new projects from a
  YAML/JSON file. (Possible v3.x; not needed at current cadence.)
- Add a "Selected Projects" one-line row format. The site uses full
  cards.
- Update the `Selected Projects` row mentioned in the user's content
  drop (no such row exists on the site).
- Extend the META_REFRESH_TOKEN PAT scope. That's a user-side GitHub
  Settings action.

## Risks and mitigations

**Risk:** Page-fit tipping to 2 pages requires more cuts than
expected. **Mitigation:** the strategy lists three candidate cuts in
preference order; if all three together aren't enough, surface to the
user before proceeding — but they should be more than enough.

**Risk:** The idempotency refactor in `refresh-resume.py` could break
the existing all-or-nothing behavior for prior NEW_SECTION entries.
**Mitigation:** the new logic is "for each entry, check if present,
insert if missing" — equivalent to the old logic when the section is
fully present (no work) or fully absent (insert everything). The
incremental case is the new addition. Verify by running the script
twice and confirming `[same]` on the second run.

**Risk:** META_REFRESH_TOKEN PAT doesn't have access to tax-rebalance.
**Mitigation:** the script gracefully `[skip]`s. The user extends the
PAT scope once, after which the weekly cron handles it automatically.
Surface this in the commit message and AI sync notes.

## Out of scope

- Changes to `trader` or `Odds Aggregator` cards or case studies.
- Updates to the OG image, JSON-LD, or anything beyond the project
  list.
- A case study for tax-rebalance. (Possible future cycle; let the
  project mature.)
