# v2.23 — reproducible resume: from-scratch builder (review #6, Option B)

Date: 2026-05-28

## Why

The other half of adversarial review #6. The resume's source was a
gitignored binary (`resume-source.docx`) that the old
`refresh-resume.py` mutated in place — lose it and the resume couldn't
be regenerated; CI couldn't build it; the content lived only in a
binary. The user chose **Option B**: a from-scratch builder from
tracked text (clean, diffable, no binary), accepting the risk of
regressing the tuned formatting and committing to careful parity
verification.

## What ships

- `resume-static.yml` (tracked) — the resume's static content: contact
  header, summary, education, experience.
- `scripts/build-resume.py` — builds `resume-source.docx` from scratch
  out of `resume-static.yml` + `projects.yml` (PERSONAL PROJECTS via
  `resume_priority` + cap; Writing line appended). Replicates the
  inventoried formatting.
- `scripts/build-site.py` — now calls `build-resume.py` instead of
  `refresh-resume.py`.
- `scripts/refresh-resume.py` — **removed** (superseded). With it goes
  the entire `PARAGRAPHS_TO_DROP` trim mechanism (~75 lines): building
  from text means there's nothing to trim.
- README + `.gitignore` comment updated: the docx is now a derived
  artifact, fully reproducible from tracked text.

## Formatting fidelity (inventoried from the original docx)

`scripts/inspect-docx.py` (one-shot, not kept) dumped the original's
formatting; `build-resume.py` replicates it:

- Font: Garamond throughout.
- Margins: 0.3in L/R, 0.17in top, 0.2in bottom.
- Name: 20pt bold, centered.
- Contact line: items tab-distributed across the width; email /
  LinkedIn / website are clickable `<w:hyperlink>`s that render as
  plain text (no blue/underline) — matching the original.
- Section headers: 12pt bold, centered.
- Role lines: 12pt bold; dates right-aligned via a right tab stop at
  the usable-width edge (cleaner than the original's many-tabs hack).
- Org lines: 12pt italic.
- Bullets: '●' + tab + text, 11.5pt, with a 0.27in hanging indent so
  wrapped lines align under the text.
- Writing line: 12pt bold with an embedded clickable link.

## Parity verification (the gate before wiring in)

Built `build-resume.py` as a *separate* script first; the old pipeline
stayed intact as a fallback until parity was confirmed:

1. **Text:** extracted text of the from-scratch PDF vs the current
   resume.pdf — identical content (only tab-span extraction artifacts
   and trivial wrap differences).
2. **Hyperlinks:** 4 URI annotations present (mailto, LinkedIn,
   website, writing).
3. **Page count:** 1.
4. **Visual:** rendered both PDFs to PNG at 150dpi and compared
   side-by-side, plus a zoom on the multi-line bullets. The
   from-scratch version is visually equivalent — and slightly cleaner
   (proper hanging indent on wrapped bullets; cleanly right-aligned
   dates). No regression.

Only after all four passed was `build-site.py` switched over and
`refresh-resume.py` removed.

## Not byte-identical (expected, accepted)

Option B trades byte/pixel-identity for clean text reproducibility.
The new docx uses a different (cleaner) bullet/date mechanism than the
original's numbering + many-tabs hacks, so line wraps differ slightly.
Verified equivalent-or-better visually; that's the Option B bargain the
user accepted.

## Headroom note

The from-scratch layout is marginally more compact, leaving more
bottom-of-page whitespace. `RESUME_MAX_PROJECTS` stays 4 (parity with
the current curation decision), but there is now clear room for a 5th
project if desired later.

## Acceptance criteria

1. `resume-static.yml` tracked; captures contact/summary/education/
   experience verbatim.
2. `build-resume.py` builds the docx from the two YAMLs; no dependency
   on a pre-existing docx.
3. `build-site.py` calls `build-resume.py`; `refresh-resume.py` removed.
4. Regenerated resume.pdf: 1 page, 4 hyperlinks, content matches,
   visually equivalent-or-better.
5. README + gitignore updated.
6. `public-safety` CI passes; tag `v2.23`.

## Out of scope

- Restoring the v2.19-trimmed EXPERIENCE bullets (they're simply not in
  `resume-static.yml`; can be added there now if wanted — that's the
  point of the tracked source).
- #2 (ship a project for real — user action).
- Other review items (#4 AI-framing, #5 narrowness, #7 overclaims).
