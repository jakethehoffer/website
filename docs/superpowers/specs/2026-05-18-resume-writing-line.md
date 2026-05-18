# v2.16 — resume PDF sync to mention writing section

Date: 2026-05-18

## Why

v2.15 shipped the writing section on the website. The resume PDF — the
artifact that actually gets attached to job applications — still
makes no mention of it. A recruiter who never clicks through to the
website never learns that there's a writing sample. A 16-word line in
the PDF closes that gap without inflating perceived scope (the section
has exactly one essay so far).

## What ships

One new italic-free, bullet-free, hyperlinked paragraph appended to the
end of the PERSONAL PROJECTS section in `resume-source.docx`,
regenerated to `resume.pdf` via LibreOffice. The script update is
idempotent.

The line:

> `Writing: jakethehoffer.github.io/website/#writing — short essays on engineering tradeoffs.`

The URL substring is a real `<w:hyperlink>` element pointing to
`https://jakethehoffer.github.io/website/#writing`.

## Where it goes

End of the document, which is also the end of the PERSONAL PROJECTS
section (PERSONAL PROJECTS is the last section as appended by the
existing `NEW_SECTION` step in `refresh-resume.py`).

The new paragraph sits at the same indent as the `trader (...)` and
`Odds Aggregator (...)` role lines — not nested under either of them.
It clones the role template (not the bullet template) so it inherits
the role-level indent and the un-bulleted paragraph style.

Visual ordering:

```
PERSONAL PROJECTS
  trader (Python · IBKR · Finnhub · pytest)
    24/7 AI swing-trading agent ...
    Paper-traded against SPY ...
  Odds Aggregator (Python · Playwright · SQLite/Alembic · FastAPI)
    Production arbitrage daemon ...
    Ingest → normalize → detect cross-book arbs ...
  Writing: jakethehoffer.github.io/website/#writing — short essays on engineering tradeoffs.   ← NEW
```

The leading `Writing:` label and the URL syntax do the visual work of
marking it as an addendum, not a third project.

## Script changes

`scripts/refresh-resume.py` gets two additions:

1. A `WRITING_LINE` constant defining the text and URL split into the
   three parts needed to build the mixed-content paragraph:
   - prefix text: `"Writing: "`
   - hyperlink: text=`"jakethehoffer.github.io/website/#writing"`, url=`"https://jakethehoffer.github.io/website/#writing"`
   - suffix text: `" — short essays on engineering tradeoffs."`

2. A new function `insert_writing_line(doc)` (~30 lines) that:
   - Checks idempotency: returns `False` if any existing paragraph
     starts with `"Writing:"`.
   - Locates the role template (`"trader (Python"` line, which exists
     after the existing main() has run NEW_SECTION).
   - Clones the role template's paragraph element to inherit indent
     and paragraph properties.
   - Strips all existing `<w:r>` and `<w:hyperlink>` children from
     the clone.
   - Copies the first run's `rPr` from the role template to use as
     formatting for the new runs.
   - Builds three children using existing helpers:
     `_make_text_run("Writing: ", rPr)`,
     `_make_hyperlink("jakethehoffer.github.io/website/#writing",
                     "https://jakethehoffer.github.io/website/#writing",
                     rPr, doc.part)`,
     `_make_text_run(" — short essays on engineering tradeoffs.", rPr)`.
   - Appends the clone to the document body after the current last
     paragraph using `.addnext(...)`.
   - Returns `True` on insertion.

3. A new call from `main()` after the existing PERSONAL PROJECTS
   construction step and before the metadata scrub, with the matching
   `[ok] / [same]` log pattern.

The hyperlink helper `_make_hyperlink` accepts its `header_part`
argument and just calls `.relate_to(url, RT.HYPERLINK,
is_external=True)`. Body hyperlinks register on `doc.part` instead of
`header.part` — the function is parameterized correctly, only the
name is header-centric.

## PDF regeneration

After the docx is rewritten, regenerate the PDF using the existing
documented command (from `README.md`):

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

The implementor should attempt this from the repo root. If LibreOffice
is not at that exact path, the conversion step fails cleanly and is
deferred to the user (the script edit and docx update are still useful
on their own and can land separately).

## What this does NOT do

- Does not add a new section to the resume.
- Does not change the SUMMARY OF QUALIFICATIONS or any other section.
- Does not add a second hyperlink in the contact header.
- Does not change the wording of any existing PERSONAL PROJECTS bullets.
- Does not promote the writing section in any way other than this
  16-word reference.
- Does not change `resume.pdf` formatting (margins, fonts, sizes).
- Does not introduce italic, bold, or color on the new line.

## Acceptance criteria

1. `scripts/refresh-resume.py` contains the `WRITING_LINE` constant
   (or equivalent inline string set) and the `insert_writing_line`
   function.
2. Running `python scripts/refresh-resume.py` on a fresh-from-original
   docx produces a docx with the writing line present, logging
   `[ok]   inserted Writing line`.
3. Running the script a second time on the resulting docx produces no
   net change, logging `[same] Writing line already present`.
4. The new line appears at the end of the docx body (after the last
   Odds Aggregator bullet), at the role-template indent (same as
   `trader (Python · ...)` and `Odds Aggregator (Python · ...)`).
5. The substring `jakethehoffer.github.io/website/#writing` in the
   regenerated PDF is a clickable hyperlink resolving to
   `https://jakethehoffer.github.io/website/#writing`.
6. `resume.pdf` is regenerated and committed; its SHA differs from the
   previous committed copy.
7. The regenerated PDF stays at 1 page.
8. `public-safety` CI passes on the commit (the writing URL is on-brand
   and triggers no banned-term hits).
9. Tag `v2.16` is pushed.

## Risks and mitigations

**Risk:** LibreOffice not installed at `C:/Program Files/LibreOffice/program/soffice.exe`. **Mitigation:** the implementor surfaces the failure and lands the docx + script edit anyway; the PDF regen is the user's manual step. Acceptance criterion 6 stays blocked until PDF is committed; v2.16 tag waits for it.

**Risk:** Page count tips to 2. **Mitigation:** verify by running the file through `soffice` and checking. If it tips, drop the lowest-signal existing line (a Lynx bullet) in a follow-up — but the new line is one short line of text, this is very unlikely.

**Risk:** Hyperlink doesn't render. The body-part hyperlink registration is a slight deviation from the existing header-part usage. **Mitigation:** `_make_hyperlink` is parameterized correctly; the only difference is which `part` object owns the relationship. Verifiable by opening the PDF and clicking, or by inspecting the docx zip's `word/_rels/document.xml.rels`.

**Risk:** Hyperlink color/style clashes with surrounding text. The
helper applies the `Hyperlink` style (blue underline). **Mitigation:**
this matches the existing email/LinkedIn/website hyperlinks in the
header, so visual consistency is maintained. If anything it's a
positive contrast — the URL is clearly clickable.

## Out of scope

- Rewriting the resume for a different audience.
- Adding case-study references to the resume.
- Changing the contact header layout.
- Converting the PDF generation to a CI workflow.
- Generating a `.tex` version or any non-docx source.
