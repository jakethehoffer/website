# v2.16 Resume Writing Line — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Append a 16-word hyperlinked line referencing the website's writing section to the end of PERSONAL PROJECTS in `resume.pdf`. Idempotent script update, then regenerate the PDF via LibreOffice headless.

**Architecture:** One Python-script extension (`scripts/refresh-resume.py`) reusing existing `_make_text_run` / `_make_hyperlink` helpers with `doc.part` (body) instead of `header.part` (header). One LibreOffice headless docx→pdf conversion. One feature commit, tag `v2.16`.

**Tech Stack:** Python 3 + `python-docx`. LibreOffice (Windows install at `C:/Program Files/LibreOffice/program/soffice.exe`) for PDF conversion.

**Spec:** `docs/superpowers/specs/2026-05-18-resume-writing-line.md`

---

## File map

- Modify: `scripts/refresh-resume.py` — add `WRITING_LINE` constant, `insert_writing_line` function, and a call in `main()`
- Regenerate: `resume-source.docx` (untracked, local-only)
- Regenerate: `resume.pdf` (tracked, will change SHA)

---

## Task 1: Add the `WRITING_LINE` constant

**Files:**
- Modify: `scripts/refresh-resume.py` — insert near the other content constants (after `NEW_SECTION`, around current line 89)

- [ ] **Step 1: Verify constant doesn't exist**

```bash
grep -c 'WRITING_LINE' scripts/refresh-resume.py
```

Expected: `0`

- [ ] **Step 2: Add the constant**

Open `scripts/refresh-resume.py`. Find the end of the `NEW_SECTION` list (which currently ends with the closing `]` after the last tuple). Immediately after that closing `]` and the blank line that follows, insert:

```python
# Writing-section pointer appended at the end of PERSONAL PROJECTS.
# Built as text + hyperlink + text so the URL is clickable in the PDF.
WRITING_LINE = {
    "prefix": "Writing: ",
    "link_text": "jakethehoffer.github.io/website/#writing",
    "link_url":  "https://jakethehoffer.github.io/website/#writing",
    "suffix":    " — short essays on engineering tradeoffs.",
}
```

The `—` is an em dash; using the escape avoids any source-encoding ambiguity.

- [ ] **Step 3: Verify the constant is present**

```bash
grep -n 'WRITING_LINE' scripts/refresh-resume.py
```

Expected: one match (the assignment).

Do **not** commit yet.

---

## Task 2: Add the `insert_writing_line` function

**Files:**
- Modify: `scripts/refresh-resume.py` — insert after `trim_dropped_paragraphs` (currently ending around line 227), before the `# ------------- main -------------` comment (currently around line 230)

- [ ] **Step 1: Verify function doesn't exist**

```bash
grep -c 'def insert_writing_line' scripts/refresh-resume.py
```

Expected: `0`

- [ ] **Step 2: Add the function**

Insert this function in `scripts/refresh-resume.py` immediately after the `trim_dropped_paragraphs` function (which ends with `return len(to_remove)` and a blank line) and before the `# ------------- main -------------` comment block:

```python
def insert_writing_line(doc) -> bool:
    """Append a one-line Writing reference at the end of the document.

    The line lives at the same indent as the role-template paragraphs
    (e.g. 'trader (Python ...)') so it sits as an addendum to PERSONAL
    PROJECTS rather than as a bullet under any specific project.
    Idempotent: returns False if a paragraph starting with 'Writing:'
    is already present."""
    body = doc.paragraphs
    if any(p.text.strip().startswith("Writing:") for p in body):
        return False

    role_template = find_para(
        body, lambda p: p.text.strip().startswith("trader (Python"))
    if role_template is None:
        raise RuntimeError(
            "Could not find role template ('trader (Python...') "
            "— PERSONAL PROJECTS step must run first.")

    # Clone the role template element so we inherit its indent and
    # paragraph properties, then strip its runs so we can rebuild.
    new_el = clone_paragraph_element(role_template)
    for child in list(new_el):
        tag = child.tag.split("}", 1)[-1]
        if tag in ("r", "hyperlink"):
            new_el.remove(child)

    # Capture the role template's first-run formatting (font, size).
    first_run = role_template._element.find(qn("w:r"))
    template_rPr = _copy_text_rpr(first_run)

    # Build prefix text + hyperlink + suffix text.
    new_el.append(_make_text_run(WRITING_LINE["prefix"], template_rPr))
    new_el.append(_make_hyperlink(
        WRITING_LINE["link_text"],
        WRITING_LINE["link_url"],
        template_rPr,
        doc.part,
    ))
    new_el.append(_make_text_run(WRITING_LINE["suffix"], template_rPr))

    # Append after the current last paragraph (which is the last
    # Odds Aggregator bullet after the PERSONAL PROJECTS step has run).
    doc.paragraphs[-1]._element.addnext(new_el)
    return True
```

- [ ] **Step 3: Verify the function is present**

```bash
grep -n 'def insert_writing_line' scripts/refresh-resume.py
```

Expected: one match.

Do **not** commit yet.

---

## Task 3: Call `insert_writing_line` from `main()`

**Files:**
- Modify: `scripts/refresh-resume.py` — insert call after the PERSONAL PROJECTS step (currently ending around line 326) and before the metadata-scrub step (currently around line 328)

- [ ] **Step 1: Verify call doesn't exist**

```bash
grep -c 'insert_writing_line(doc)' scripts/refresh-resume.py
```

Expected: `0`

- [ ] **Step 2: Locate the insertion point**

Find this block in `main()` (currently around lines 314–326):

```python
    already = find_para(body, lambda p: p.text.strip() == "PERSONAL PROJECTS")
    if already is not None:
        print("[same] PERSONAL PROJECTS section already present")
    else:
        anchor = body[-1]._element
        for kind, text in NEW_SECTION:
            template = templates[kind]
            new_el = clone_paragraph_element(template)
            anchor.addnext(new_el)
            anchor = new_el
            wrapper = Paragraph(new_el, None)
            set_paragraph_text(wrapper, text)
        print(f"[ok]   inserted PERSONAL PROJECTS section ({len(NEW_SECTION)} paragraphs)")
```

Immediately after this `if/else` block (after the `print(f"[ok]   inserted PERSONAL PROJECTS section ({len(NEW_SECTION)} paragraphs)")` line, outside the `else:`), insert a new step:

```python

    # --- 5. Writing-section reference appended to PERSONAL PROJECTS ---
    if insert_writing_line(doc):
        print("[ok]   inserted Writing line at end of PERSONAL PROJECTS")
    else:
        print("[same] Writing line already present")
```

The blank line at the start of the block matches the existing spacing convention between numbered steps.

- [ ] **Step 3: Verify call is present**

```bash
grep -n 'insert_writing_line(doc)' scripts/refresh-resume.py
```

Expected: one match (the call inside `main()`).

- [ ] **Step 4: Run a syntax check**

```bash
python -c "import ast; ast.parse(open('scripts/refresh-resume.py').read())"
```

Expected: exits cleanly (no output, exit code 0). Any `SyntaxError` traceback means stop and fix.

Do **not** commit yet.

---

## Task 4: Run the script and verify idempotency

**Files:** none modified (this task runs the script, which modifies the local-only `resume-source.docx`)

- [ ] **Step 1: Verify the source docx exists**

```bash
ls -la resume-source.docx
```

Expected: file exists. If not (the file is .gitignored and lives only locally), this task is **blocked** — surface to the user and stop. The script can't run without a source docx.

- [ ] **Step 2: Run the script first time**

From the repo root:

```bash
python scripts/refresh-resume.py
```

Expected output (order matters; messages depend on prior state):

```
[same] or [ok] contact line ...
[same] or [ok] skills line ...
[same] or [ok] no paragraphs to trim / trimmed N paragraph(s)
[same] PERSONAL PROJECTS section already present
[ok]   inserted Writing line at end of PERSONAL PROJECTS    ← key line
[ok]   scrubbed Office metadata (author, comments, etc.)
wrote .../resume-source.docx
```

If the `[ok]   inserted Writing line` message isn't present, something went wrong in Task 2 or 3. Stop and diagnose.

- [ ] **Step 3: Run the script a second time (idempotency check)**

```bash
python scripts/refresh-resume.py
```

Expected: same output, except the Writing line message becomes:

```
[same] Writing line already present
```

If it inserts a duplicate, the idempotency check is broken — stop and fix the `any(p.text.strip().startswith("Writing:"))` predicate.

---

## Task 5: Regenerate the PDF and verify page count

**Files:**
- Regenerate: `resume.pdf` (tracked)

- [ ] **Step 1: Run LibreOffice headless conversion**

From the repo root:

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
```

Expected output:

```
convert .../resume-source.docx -> .../resume-source.pdf using filter : writer_pdf_Export
```

If the command isn't found (LibreOffice not installed at that path), this task is **partially blocked**:
- The docx changes from Tasks 1–4 are still useful and can be committed.
- The PDF regeneration is deferred to the user. Surface this clearly and continue to Task 6 with the script-only commit, flagging that resume.pdf was not regenerated.

- [ ] **Step 2: Replace the tracked resume.pdf**

```bash
mv resume-source.pdf resume.pdf
```

(Windows note: if `mv` is unavailable, use `move resume-source.pdf resume.pdf` or the Bash tool's equivalent.)

- [ ] **Step 3: Verify page count is 1**

Use a PDF page-count check. One option:

```bash
python -c "from pypdf import PdfReader; print(len(PdfReader('resume.pdf').pages))"
```

Expected: `1`

If `pypdf` is not installed:

```bash
pip install pypdf
```

then re-run. (`pypdf` is a single-file pure-Python install, fast.)

If the page count is 2:
- **Stop.** Don't commit a 2-page PDF.
- Diagnose: the line is short, so either margins were already razor-thin or something else changed unexpectedly. Inspect the docx for clues.
- Mitigation per spec: drop the lowest-signal Lynx bullet in a follow-up. Surface this to the user before continuing.

- [ ] **Step 4: Verify the Writing line is in the PDF**

```bash
python -c "from pypdf import PdfReader; print('Writing:' in PdfReader('resume.pdf').pages[0].extract_text())"
```

Expected: `True`

- [ ] **Step 5: (Optional) Verify the hyperlink is real**

```bash
python -c "
from pypdf import PdfReader
r = PdfReader('resume.pdf')
links = []
for page in r.pages:
    annots = page.get('/Annots')
    if annots:
        for a in annots:
            obj = a.get_object()
            if obj.get('/A') and obj['/A'].get('/URI'):
                links.append(obj['/A']['/URI'])
for l in links:
    print(l)
"
```

Expected: among the URIs, `https://jakethehoffer.github.io/website/#writing` is present (alongside the existing mailto:, linkedin, and website URIs from the contact header).

---

## Task 6: Commit, push, tag `v2.16`

**Files:** all changes from Tasks 1–5.

- [ ] **Step 1: Review the full diff**

```bash
git diff --stat
git diff scripts/refresh-resume.py | head -100
```

Expected: at minimum `scripts/refresh-resume.py` modified (~50 lines added). If Task 5 succeeded, `resume.pdf` also modified (binary, shows as `Bin <old>->_<new>`). The spec file from this cycle was already committed separately.

- [ ] **Step 2: Stage and commit**

```bash
git add scripts/refresh-resume.py docs/superpowers/plans/2026-05-18-resume-writing-line.md resume.pdf
git commit -m "$(cat <<'EOF'
feat(resume): add writing-section pointer to PERSONAL PROJECTS

One italic-free 16-word line at the end of the resume's PERSONAL
PROJECTS section: "Writing: jakethehoffer.github.io/website/#writing
— short essays on engineering tradeoffs." The URL substring is a real
clickable <w:hyperlink> registered on doc.part, mirroring how the
header lines (email/LinkedIn/website) are built. Idempotent: a
second run logs [same].

The PDF gets refreshed via the documented LibreOffice headless
command. The committed resume.pdf is the only public-facing artifact;
resume-source.docx stays gitignored after v2.12.

Spec: docs/superpowers/specs/2026-05-18-resume-writing-line.md
Plan: docs/superpowers/plans/2026-05-18-resume-writing-line.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

If `resume.pdf` was **not** regenerated (LibreOffice missing in Task 5), drop `resume.pdf` from `git add`, and adjust the commit message body to flag that the PDF regen is deferred to the user.

- [ ] **Step 3: Push to `main`**

```bash
git push
```

- [ ] **Step 4: Wait for public-safety CI**

```bash
gh run list --workflow=public-safety.yml --limit 1
```

Expected: status reads `completed success` within ~15 seconds.

If `failure`:

```bash
gh run view --log-failed
```

Most likely cause for this cycle: a banned term somehow landed in the script or plan. Check the URL substring carefully — `jakethehoffer.github.io/website/#writing` does not match any of the banned-term prefixes.

- [ ] **Step 5: Tag and push tag**

```bash
git tag v2.16
git push --tags
```

- [ ] **Step 6: Update AI sync state**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "v2.16: resume PDF now references writing section (one-line italic-free hyperlinked addendum at end of PERSONAL PROJECTS)" -FilesChanged "scripts/refresh-resume.py, resume.pdf, docs/superpowers/specs/2026-05-18-resume-writing-line.md, docs/superpowers/plans/2026-05-18-resume-writing-line.md" -TestsRun "script idempotency: [ok] then [same]; PDF page count: 1; Writing line present in PDF text; hyperlink registered to https://jakethehoffer.github.io/website/#writing; public-safety CI: green" -Blockers "none (or note: PDF regen deferred to user if LibreOffice unavailable)" -NextSteps "Site + resume now aligned with v2.15 writing section. Genuine diminishing-returns ceiling for autonomous improvements; next valuable moves are external (apply to jobs, share the essay) or wait for a portfolio milestone before next iteration."
```

---

## Acceptance criteria (from spec)

After Task 6, all of these must hold:

1. `WRITING_LINE` constant + `insert_writing_line` function present in script. **(Task 1, 2)**
2. First script run inserts the line, logs `[ok]   inserted Writing line at end of PERSONAL PROJECTS`. **(Task 4 Step 2)**
3. Second run logs `[same] Writing line already present`. **(Task 4 Step 3)**
4. Line appears at end of docx, at role-template indent. **(implicit; verified visually if PDF regen succeeds)**
5. PDF contains the hyperlink resolving to the absolute URL. **(Task 5 Step 5)**
6. `resume.pdf` SHA differs from the v2.15 baseline. **(implicit from regeneration)**
7. PDF is 1 page. **(Task 5 Step 3)**
8. `public-safety` CI passes. **(Task 6 Step 4)**
9. Tag `v2.16` pushed. **(Task 6 Step 5)**

---

## Plan self-review

**Spec coverage:** Each of the 9 acceptance criteria maps to a verification step in this plan:
- AC1 → Tasks 1+2 grep checks
- AC2 → Task 4 Step 2
- AC3 → Task 4 Step 3
- AC4 → Task 5 Step 4 (text-presence check) + visual via PDF
- AC5 → Task 5 Step 5
- AC6 → implicit (binary file in commit)
- AC7 → Task 5 Step 3
- AC8 → Task 6 Step 4
- AC9 → Task 6 Step 5

**Placeholder scan:** No TBDs, no "implement later". Every code block is exact. The optional hyperlink-verification Python script in Task 5 Step 5 is complete and runnable.

**Type consistency:** `WRITING_LINE` is a dict with keys `prefix`, `link_text`, `link_url`, `suffix` (Task 1) — used by name in `insert_writing_line` (Task 2). `find_para`, `clone_paragraph_element`, `_copy_text_rpr`, `_make_text_run`, `_make_hyperlink` are all existing functions in the script (verified via prior reads). `doc.part` is a real attribute on `docx.Document` objects.

**Failure-path coverage:**
- Missing `resume-source.docx`: handled in Task 4 Step 1 (BLOCKED, surface to user).
- Missing LibreOffice: handled in Task 5 Step 1 (script commit proceeds; PDF regen deferred).
- 2-page PDF: handled in Task 5 Step 3 (STOP, don't commit; surface for follow-up).
- CI banned-term hit: handled in Task 6 Step 4 (read log, fix, re-commit).

**Out-of-scope creep check:** No changes to the website. No changes to other resume sections. No new sections. No new fonts. Stays inside `scripts/refresh-resume.py` and `resume.pdf`.
