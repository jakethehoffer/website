# Resume Polish (page-count + hyperlinks) — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation (v2.10)

## Why

Two specific issues with the v2.8 resume:
1. Resume grew from 1 → 2 pages. For tech/quant audiences 2 pages is
   acceptable, but page 2 has substantial whitespace and the 1-page
   convention still wins close calls.
2. Email and LinkedIn lost their hyperlinks in the v2.8 docx rewrite.
   Plain text URLs *can* auto-link in some PDF viewers, but
   recruiter-facing PDFs should ship with explicit hyperlinks for
   reliability.

## Goal

A 1-page `resume.pdf` where the contact header has three clickable
hyperlinks (email, LinkedIn, website URL).

## Non-Goals

- Restructuring the resume layout / fonts / margins.
- Removing any other entries (Education, BMC Pharmacy, QMIND, etc.).
- Changing any non-Lynx Experience bullets.
- Adding more hyperlinks beyond the three in the contact line.

## Concrete Changes

### Part A — trim Lynx Equity bullets

Current 5 bullets in `resume-source.docx`:

1. Developed a task management system on Monday.com... *(keep)*
2. Built an On/Off-Boarding workflow in Monday.com... *(keep)*
3. **Designed Monday.com form that prefills user data via URL
   parameters, reducing setup time for new processes.** *(DROP)*
4. Developed Google Apps Script solutions in JavaScript... *(keep)*
5. **Conducted DNS lookups to gather information on subsidiary
   company websites, including email providers, SSL status, and
   other domain-related data.** *(DROP)*

Bullets 3 and 5 are the lower-signal ones. Bullet 3 is a feature
refinement (the broader Monday.com work is already in bullet 1).
Bullet 5 is operational sysadmin work (less differentiating than the
software-engineering content of bullets 1, 2, 4).

Result: Lynx Equity goes from 5 bullets to 3. Roughly 4–5 fewer lines
in the rendered PDF — enough to bring PERSONAL PROJECTS back to
page 1.

### Part B — restore hyperlinks in the contact header

Target paragraph (in `doc.sections[0].header.paragraphs[1]`):

> `3 [removed-street] Blvd, Toronto ON M3H 3B7\t14jakehoffman@gmail.com\tTel: 647-823-4504\tLinkedIn\tjakethehoffer.github.io/website`

Three substrings become hyperlinks:

| Display text | URL |
|---|---|
| `14jakehoffman@gmail.com` | `mailto:14jakehoffman@gmail.com` |
| `LinkedIn` | `https://www.linkedin.com/in/jake-hoffman-7117692a5/` |
| `jakethehoffer.github.io/website` | `https://jakethehoffer.github.io/website/` |

Implementation: direct OOXML manipulation. The header paragraph is
rebuilt as a sequence of `<w:r>` plain-text runs interleaved with
`<w:hyperlink>` wrapper elements. The hyperlink elements reference
`r:id` values that point into `word/_rels/header1.xml.rels`. We add
three new `<Relationship>` entries to that rels file.

The display-text style for each hyperlink: Word's built-in `Hyperlink`
character style (blue, underlined). Preserves Word's default link
appearance and stays consistent with how the original LinkedIn link
was styled before v2.8 broke it.

### Updates to `scripts/refresh-resume.py`

The script becomes the source of truth for the resume content. Two
new responsibilities:

1. **`build_contact_line(p, doc_section)`** — rebuild the contact
   paragraph from scratch with the three hyperlinks. Adds rels to the
   header part's rels file. Idempotent (re-runs produce the same
   structure).
2. **`trim_lynx_bullets(doc)`** — identify bullets 3 and 5 by exact
   text-prefix and remove them. Idempotent (re-runs leave the trimmed
   state alone since the bullets are no longer present).

The existing `set_paragraph_text` stays for the skills line. The
contact line uses the new `build_contact_line` instead.

## File Layout Delta

```
website/
├── resume-source.docx                    MODIFIED (in-place via script)
├── resume.pdf                            REGENERATED (target: 1 page)
├── scripts/refresh-resume.py             MODIFIED (+ hyperlink + trim logic)
└── docs/superpowers/specs/
    └── 2026-05-12-resume-polish.md       THIS DOC
```

## Implementation: hyperlinks (technical detail)

A `<w:hyperlink>` in OOXML wraps text runs and points at an external
URL via the relationships file:

```xml
<w:hyperlink r:id="rIdHL1" w:history="1">
  <w:r>
    <w:rPr>
      <w:rStyle w:val="Hyperlink"/>
      <w:rFonts w:ascii="Garamond" .../>
      <w:sz w:val="23"/>
    </w:rPr>
    <w:t xml:space="preserve">14jakehoffman@gmail.com</w:t>
  </w:r>
</w:hyperlink>
```

And in `word/_rels/header1.xml.rels`:

```xml
<Relationship Id="rIdHL1"
              Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
              Target="mailto:14jakehoffman@gmail.com"
              TargetMode="External"/>
```

python-docx exposes the header part via
`doc.sections[0].header.part`. Its `.rels` attribute is a dict of
`Relationship` objects. We add new ones via `header.part.relate_to(url, REL_TYPE_HYPERLINK, is_external=True)`, which returns the new rId and writes the rels file when the doc saves. That's the official path; it avoids us hand-editing XML for the rels.

For the paragraph rebuild, we use the OOXML manipulation already in
`set_paragraph_text` (remove all `<w:r>` and `<w:hyperlink>` children),
then build the new structure piece by piece.

## Verification

After running the script:
- `python -c` extraction:
  - Contact line text matches the v2.8 form (plain-text fallback if
    PDF viewer can't render hyperlinks)
  - Header rels file has 3 new hyperlink relationships
  - Lynx Equity paragraph count: was 5 bullets, now 3
- Regenerated PDF:
  - 1 page
  - Email, LinkedIn, website URL are clickable (visible as blue
    underlined text in most viewers)
  - No layout artifacts

## Risks

- **rId collisions.** python-docx's `relate_to` API auto-generates
  rIds and avoids collisions, so this should be safe.
- **Word's `Hyperlink` style not present in the docx.** If the
  template doesn't define the `Hyperlink` character style, the new
  hyperlinks will render as plain text (still clickable, but
  unstyled). Mitigation: check if the style exists at script start;
  fall back to inline rPr with blue color + underline if not.
- **Page count still 2 even after trimming.** If so, we drop one
  more bullet from Mega TTT or QMIND, or shrink the contact-line
  spacing. Easy follow-up — but unlikely needed.
- **Idempotency edge cases.** Re-running must not duplicate
  hyperlinks or re-add already-trimmed bullets. Both are handled by
  the rebuild-from-scratch approach (`build_contact_line` always
  produces the same output for the same input) and the trim function
  checking for the bullets' existence before removing.

## Success Criteria

- `resume.pdf` is 1 page (≤ 1.0 in pypdf page count).
- Email, LinkedIn, website URL render as clickable hyperlinks in a
  PDF viewer.
- Lynx Equity entry shows exactly 3 bullets.
- `scripts/refresh-resume.py` re-running shows `[same]` for all
  sections it manages (idempotency holds).
- No visual layout regressions on the rest of the resume.
