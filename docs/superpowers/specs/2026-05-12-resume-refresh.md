# Resume Refresh — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

The committed `resume-source.docx` predates Jake's two most-active
personal projects (`trader`, `Odds Aggregator`). Deploying a PDF
without them undersells the portfolio. This cycle adds those
projects, refreshes the skills line, and stamps the live website URL
on the contact header. Regenerated `resume.pdf` ships in the same
release.

## Goal

A `resume-source.docx` that:
1. Includes a `PERSONAL PROJECTS` section with `trader` and `Odds
   Aggregator`, matching the existing typography / style of the
   `EXPERIENCE` section.
2. Has an updated `Proficient in …` line in the Summary of
   Qualifications.
3. Shows `jakethehoffer.github.io/website` in the contact area at
   the top of the page.
4. Regenerated PDF reflects all of the above with no layout
   regressions.

## Non-Goals

- Rewriting any existing section (Summary tone, Education projects,
  current Experience bullets). Your voice stays.
- Reordering sections. Adding PERSONAL PROJECTS at the *end*
  (after EXPERIENCE) is the lowest-risk insertion point and
  preserves the existing flow.
- Changing fonts, margins, line spacing, or any layout property.
  The only allowed edits are content insertions in existing styles.
- Dropping the BMC Pharmacy entry (or any other historical role).
- Adding dates to the PERSONAL PROJECTS entries. I don't have
  ground-truth start dates, and "2026 – Present" is vague enough
  that "Active project" framing is more honest. Each entry's first
  bullet already conveys recency ("Paper-traded the S&P 500 …",
  "Production daemon … 24/7").

## Concrete Changes

### 1. Contact header — add website URL

The top of the resume currently shows name + email (and possibly
LinkedIn). Add the website URL `jakethehoffer.github.io/website`
adjacent to or below the email line, matching the existing contact
typography. Exact placement is determined at implementation time
based on what python-docx reports for the first paragraph(s).

### 2. Skills line in Summary of Qualifications

**Before:**
> Proficient in Python, Java, C, C#, C++, SQL, Git, Word, Excel,
> JavaScript, Dart, Unity, and Monday.com.

**After:**
> Proficient in Python, Java, C, C#, C++, SQL, Git, Word, Excel,
> JavaScript, Dart, Unity, FastAPI, Playwright, Monday.com, and
> Google Apps Script.

Three additions (FastAPI, Playwright, Google Apps Script). FastAPI
and Playwright are both used in `Odds Aggregator`; Google Apps Script
is already in the Lynx Equity bullets but wasn't reflected in the
proficiency line.

### 3. New PERSONAL PROJECTS section

Inserted after the last bullet of the BMC Pharmacy entry. Section
heading matches the styling of `EXPERIENCE` (the existing section
heading style — likely Heading 1 or a custom resume-section style;
will be detected at implementation time from the document's existing
styles).

Two entries:

**trader** *(Python · IBKR · Finnhub · pytest)*
- 24/7 AI swing-trading agent for S&P 500 equities, driven by six
  scheduled Claude Code routines.
- Paper-traded against SPY with kill-switch, risk gates, and
  committed JSON journaling; graduates to live trading after 30 days
  of documented outperformance.
- Designed broker abstraction so the live cutover is a one-line
  config change (IBKR active, Alpaca preserved).

**Odds Aggregator** *(Python · Playwright · SQLite / Alembic · FastAPI)*
- Production arbitrage daemon covering 10 bookmakers across 6 sports.
- Ingest &rarr; normalize &rarr; detect cross-book arbs &rarr; push
  alerts to Telegram and Discord. Runs 24/7 with replay tooling for
  postmortems.
- Built defensive ingestion: per-book health scoring, automatic
  backoff on bot-detection, and ten Alembic migrations from iterating
  on real production traffic.

### 4. Regenerate `resume.pdf`

Same command path already documented in the README:

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

## Implementation Approach

Use `python-docx` (installed, v1.2.0) to:
1. Open `resume-source.docx`.
2. Walk paragraphs to identify:
   - The contact area at the top (first few paragraphs)
   - The skills line in Summary of Qualifications (look for "Proficient in")
   - The last paragraph of the BMC Pharmacy entry (the anchor for
     the new section insertion)
3. Modify the skills paragraph in place.
4. Insert the website URL into the contact area in place.
5. Insert the PERSONAL PROJECTS section after the BMC anchor by:
   - Capturing the style names of the existing `EXPERIENCE` heading
     and the existing bullet paragraphs
   - Using those same style names for the new heading and bullets so
     formatting matches
6. Save the modified docx.

`python-docx` preserves all formatting (fonts, spacing, indentation,
styles) for paragraphs we *don't* touch. Paragraphs we touch keep
their style as long as we use the `paragraph.style` of an existing
similar paragraph or modify text content via `paragraph.runs`.

## File Layout Delta

```
website/
├── resume-source.docx                    MODIFIED (3 content additions)
├── resume.pdf                            REGENERATED
└── docs/superpowers/specs/
    └── 2026-05-12-resume-refresh.md      THIS DOC
```

## Verification

After running the edit script:
- `extract-text` (or our `python -c` zipfile extractor) the resulting
  docx and confirm:
  - The new skills line contains "FastAPI, Playwright, ..., and Google
    Apps Script"
  - "PERSONAL PROJECTS" appears as a section header
  - "trader" and "Odds Aggregator" appear with their bullets
  - The website URL appears in the contact area
- Regenerate PDF with LibreOffice; open in a viewer and visually
  confirm:
  - No layout corruption (margins, fonts, alignment intact)
  - New section sits below EXPERIENCE
  - PDF is still 1 page (resumes shouldn't grow to 2 pages from this
    addition — if it does, we tighten an existing bullet or accept
    the 2-page state and re-discuss next cycle)
- Page weight delta on the live site: `resume.pdf` will grow slightly
  (~5–10 KB likely). Not on the critical render path; visitors only
  fetch it on click of the Download Resume button.

## Risks

- **`python-docx` not finding the right anchor paragraphs.**
  Mitigated by inspecting the document before edits — the script
  prints its planned insertion points and the user (me) confirms
  they're sensible before committing.
- **Style mismatch on the new section.** Mitigated by copying the
  style name from the existing EXPERIENCE heading rather than using
  hardcoded style names.
- **Resume growing to 2 pages.** Probable but acceptable. If it
  happens and feels wrong, we trim an existing bullet in a follow-up
  micro-cycle.
- **LibreOffice PDF render differs from Word's render.** This is
  pre-existing — Jake already uses the LibreOffice path. No new
  risk introduced.
- **A typo / formatting glitch in the new content.** Mitigated by
  inspecting the rendered PDF before committing.

## Success Criteria

- `resume-source.docx` is committed with the three additions in
  styles matching their neighbors.
- `resume.pdf` regenerated and committed; opens cleanly in any PDF
  viewer; no missing fonts / smart-quote artifacts.
- The site's `Download Resume (PDF)` button serves the updated PDF.
- Visual review by Jake confirms voice and tone are preserved.

## Out of Scope (Restated YAGNI)

- A second draft / structural redesign of the resume.
- Adding a "Now" status block in the resume.
- A separate "Open Source" section. Both projects ARE arguably
  open-source-shaped, but they're private repos; "Personal Projects"
  is the more honest framing.
- Adding the goon-maps / claude-usage-widget / crypto / money /
  youtube projects. We're picking the two highest-impact for
  trading-aligned recruiters; the rest stay on GitHub.
- A LinkedIn URL refresh in the docx (presumed already present /
  correct; will not touch it unless an obvious typo surfaces).
