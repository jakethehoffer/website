# Resume Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh `resume-source.docx` with the website URL, an updated skills line, and a new PERSONAL PROJECTS section (trader + Odds Aggregator). Regenerate `resume.pdf`.

**Architecture:** One Python script (`scripts/refresh-resume.py`) using `python-docx` to make scoped edits to `resume-source.docx`, then `soffice` to regenerate the PDF. The script is committed for reproducibility — re-running it produces the same docx (modulo timestamps).

**Tech Stack:** `python-docx` 1.2.0, raw XML manipulation via `docx.oxml` for cloning bullet paragraphs, LibreOffice headless for PDF conversion.

**Spec:** `docs/superpowers/specs/2026-05-12-resume-refresh.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── resume-source.docx                    MODIFIED (in-place edit via script)
├── resume.pdf                            REGENERATED
├── scripts/
│   └── refresh-resume.py                 NEW (committed for reproducibility)
└── docs/superpowers/plans/
    └── 2026-05-12-resume-refresh.md      THIS DOC
```

---

## Document structure (verified)

From `python-docx` + raw-XML inspection:

| Location | Content |
|---|---|
| `doc.sections[0].header.paragraphs[1]` | `3 Collinson Blvd, Toronto ON M3H 3B7\t14jakehoffman@gmail.com\tTel: 647-823-4504\tLinkedIn` — tab-separated contact line |
| `doc.paragraphs[2]` | `Proficient in Python, Java, C, C#, C++, SQL, Git, Word, Excel, JavaScript, Dart, Unity, and Monday.com.` — Summary skills line |
| `doc.paragraphs[13]` | `EXPERIENCE` — section heading style we mirror |
| Lynx bullets (e.g. `doc.paragraphs[16]`) | `Normal` style + `<w:numPr w:numId="2">` numbering + Garamond 11.5pt — what we clone for PERSONAL PROJECTS bullets |
| BMC last paragraph | last in body — anchor for inserting new section |

Section headings in this doc are styled `Normal` (not Heading 1) with bold + larger text via direct formatting. To match `EXPERIENCE` we clone that paragraph and rewrite text.

---

## Task 1: Write `scripts/refresh-resume.py`

**Files:**
- Create: `C:/Users/14jak/GitHub/website/scripts/refresh-resume.py`

- [ ] **Step 1: Write the script**

```python
"""Refresh resume-source.docx with the website URL, updated skills line,
and a new PERSONAL PROJECTS section (trader + Odds Aggregator).

Idempotent: re-running produces the same docx output. Committed for
reproducibility.

Usage:
    python scripts/refresh-resume.py

In-place rewrites:
    resume-source.docx
"""

from __future__ import annotations

import copy
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "resume-source.docx"

# ------------- desired content -------------

NEW_CONTACT_LINE = (
    "3 Collinson Blvd, Toronto ON M3H 3B7"
    "\t14jakehoffman@gmail.com"
    "\tTel: 647-823-4504"
    "\tLinkedIn"
    "\tjakethehoffer.github.io/website"
)

NEW_SKILLS_LINE = (
    "Proficient in Python, Java, C, C#, C++, SQL, Git, Word, Excel, "
    "JavaScript, Dart, Unity, FastAPI, Playwright, Monday.com, and "
    "Google Apps Script."
)

# New section, structured as (paragraph_type, text). 'heading' clones
# the EXPERIENCE paragraph (section header style); 'role' clones the
# bold-tab-line paragraph used for job titles ("IT Intern \t\t Dates");
# 'org' clones the company/title-detail line; 'bullet' clones a
# Lynx Equity bullet (numbered list).
NEW_SECTION = [
    ("heading", "PERSONAL PROJECTS"),
    ("role",    "trader (Python · IBKR · Finnhub · pytest)"),
    ("org",     "AI swing-trading agent"),
    ("bullet",  "24/7 AI swing-trading agent for S&P 500 equities, "
                "driven by six scheduled Claude Code routines."),
    ("bullet",  "Paper-traded against SPY with kill-switch, risk gates, "
                "and committed JSON journaling; graduates to live "
                "trading after 30 days of documented outperformance."),
    ("bullet",  "Designed broker abstraction so the live cutover is a "
                "one-line config change (IBKR active, Alpaca preserved)."),
    ("role",    "Odds Aggregator (Python · Playwright · SQLite/Alembic · FastAPI)"),
    ("org",     "Production cross-book arbitrage daemon"),
    ("bullet",  "Production arbitrage daemon covering 10 bookmakers "
                "across 6 sports."),
    ("bullet",  "Ingest → normalize → detect cross-book arbs "
                "→ push alerts to Telegram and Discord. Runs 24/7 "
                "with replay tooling for postmortems."),
    ("bullet",  "Built defensive ingestion: per-book health scoring, "
                "automatic backoff on bot-detection, and ten Alembic "
                "migrations from iterating on real production traffic."),
]


# ------------- helpers -------------

def find_para(paragraphs, predicate):
    for p in paragraphs:
        if predicate(p):
            return p
    return None


def set_paragraph_text(p, new_text: str) -> None:
    """Replace the text of `p` while keeping its formatting.

    The strategy: keep the first run, set its text to `new_text`, and
    remove any additional runs. The first run's rPr (formatting)
    survives.
    """
    runs = p.runs
    if not runs:
        # Edge case: paragraph with no runs (rare). Just add one.
        p.add_run(new_text)
        return
    runs[0].text = new_text
    # Remove the remaining runs from the XML.
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def clone_paragraph(template_p):
    """Return a deep copy of the paragraph's XML element."""
    return copy.deepcopy(template_p._element)


def insert_after(reference_element, new_element) -> None:
    reference_element.addnext(new_element)


# ------------- main -------------

def main() -> None:
    doc = Document(str(DOCX))

    # --- 1. Contact line in header ---
    hdr_paragraphs = doc.sections[0].header.paragraphs
    contact_p = find_para(hdr_paragraphs, lambda p: "@gmail.com" in p.text)
    if contact_p is None:
        raise RuntimeError("Could not find contact line in document header.")
    if "jakethehoffer.github.io/website" not in contact_p.text:
        set_paragraph_text(contact_p, NEW_CONTACT_LINE)
        print(f"[ok] contact line updated")
    else:
        print(f"[same] contact line already has website URL")

    # --- 2. Skills line in Summary of Qualifications ---
    body = doc.paragraphs
    skills_p = find_para(body, lambda p: p.text.startswith("Proficient in "))
    if skills_p is None:
        raise RuntimeError("Could not find skills paragraph.")
    if skills_p.text != NEW_SKILLS_LINE:
        set_paragraph_text(skills_p, NEW_SKILLS_LINE)
        print(f"[ok] skills line updated")
    else:
        print(f"[same] skills line already updated")

    # --- 3. PERSONAL PROJECTS section ---
    # Find templates from existing EXPERIENCE section.
    experience_heading = find_para(body, lambda p: p.text.strip() == "EXPERIENCE")
    if experience_heading is None:
        raise RuntimeError("Could not find EXPERIENCE heading.")

    role_template   = find_para(body, lambda p: p.text.strip().startswith("IT Intern"))
    org_template    = find_para(body, lambda p: p.text.strip() == "Lynx Equity Limited")
    bullet_template = find_para(body, lambda p: p.text.startswith("Developed a task management system"))
    if not all([role_template, org_template, bullet_template]):
        raise RuntimeError("Could not find template paragraphs.")

    templates = {
        "heading": experience_heading,
        "role":    role_template,
        "org":     org_template,
        "bullet":  bullet_template,
    }

    # Idempotency: if "PERSONAL PROJECTS" heading already exists, don't add again.
    already = find_para(body, lambda p: p.text.strip() == "PERSONAL PROJECTS")
    if already is not None:
        print("[same] PERSONAL PROJECTS section already present")
    else:
        # Find the last body paragraph (anchor after BMC bullets).
        # We insert after `doc.paragraphs[-1]`, walking the XML.
        anchor = body[-1]._element

        for kind, text in NEW_SECTION:
            template = templates[kind]
            new_p = clone_paragraph(template)
            insert_after(anchor, new_p)
            # Now anchor advances so subsequent paragraphs go after this one.
            anchor = new_p
            # Replace the text content of the cloned paragraph.
            # We need to find the first <w:r><w:t>...</w:t></w:r> and rewrite it,
            # removing any sibling runs. Easiest: use the python-docx Paragraph
            # wrapper which can be constructed from the element.
            from docx.text.paragraph import Paragraph
            wrapper = Paragraph(new_p, None)
            set_paragraph_text(wrapper, text)

        print(f"[ok] inserted PERSONAL PROJECTS section ({len(NEW_SECTION)} paragraphs)")

    # --- save ---
    doc.save(str(DOCX))
    print(f"wrote {DOCX}")


if __name__ == "__main__":
    main()
```

Key design choices:
- **`set_paragraph_text`** preserves the first run's formatting by editing
  `runs[0].text` and dropping any extra runs. This keeps the bullet
  character, font, size, color, indent — everything that came from the
  cloned template.
- **Idempotency:** each section checks whether the change is already
  present before applying it. Safe to re-run.
- **No layout edits:** the script never touches `<w:pPr>` (paragraph
  properties) of templates — it just deep-copies them.
- **Templates picked from `EXPERIENCE`:** heading style, role line,
  org/title line, bullet style. We assume the rest of the resume follows
  these patterns, which the inspection confirmed.

- [ ] **Step 2: Commit the script**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/refresh-resume.py
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add refresh-resume.py (resume.docx content updater)"
```

---

## Task 2: Run the script and verify the docx

**Files:**
- Modified by script: `C:/Users/14jak/GitHub/website/resume-source.docx`

- [ ] **Step 1: Run the script**

```bash
python "C:/Users/14jak/GitHub/website/scripts/refresh-resume.py"
```

Expected output (first run):
```
[ok] contact line updated
[ok] skills line updated
[ok] inserted PERSONAL PROJECTS section (12 paragraphs)
wrote C:/Users/14jak/GitHub/website/resume-source.docx
```

A second run should show `[same]` for all three sections — idempotency.

- [ ] **Step 2: Extract text and verify**

```bash
PYTHONIOENCODING=utf-8 python <<'PY'
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
doc = Document(r"C:/Users/14jak/GitHub/website/resume-source.docx")

# Contact line check
hdr = doc.sections[0].header.paragraphs
contact = next((p for p in hdr if "@gmail.com" in p.text), None)
print("contact line:", contact.text if contact else "NOT FOUND")

# Skills line check
skills = next((p for p in doc.paragraphs if p.text.startswith("Proficient in")), None)
print("skills line:", skills.text if skills else "NOT FOUND")

# PERSONAL PROJECTS section
print()
print("=== body paragraphs after PERSONAL PROJECTS heading ===")
found = False
for p in doc.paragraphs:
    if p.text.strip() == "PERSONAL PROJECTS":
        found = True
    if found:
        print(f"  style={p.style.name!r}  text={p.text[:100]!r}")
print("found PERSONAL PROJECTS:", found)
PY
```

Expected:
- Contact line ends with `\tjakethehoffer.github.io/website`
- Skills line includes `FastAPI, Playwright` and `Google Apps Script`
- `PERSONAL PROJECTS` heading + `trader` role + 3 bullets + `Odds Aggregator` role + 3 bullets

If any check fails, debug before continuing. Don't regenerate the PDF
from a docx that's structurally wrong.

- [ ] **Step 3: Commit the modified docx**

```bash
git -C "C:/Users/14jak/GitHub/website" add resume-source.docx
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: refresh resume content (trader + Odds Aggregator, skills, URL)"
```

---

## Task 3: Regenerate `resume.pdf`

**Files:**
- Regenerate: `C:/Users/14jak/GitHub/website/resume.pdf`

- [ ] **Step 1: Convert via LibreOffice headless**

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir "C:/Users/14jak/GitHub/website" "C:/Users/14jak/GitHub/website/resume-source.docx" 2>&1 | tail -3
mv "C:/Users/14jak/GitHub/website/resume-source.pdf" "C:/Users/14jak/GitHub/website/resume.pdf"
ls -la "C:/Users/14jak/GitHub/website/resume.pdf"
```

Expected: a new `resume.pdf` between 80–130 KB (current is 105 KB; new
content will push it slightly up — maybe 110–125 KB).

- [ ] **Step 2: Visual check via Read tool**

Read the first page of `resume.pdf`. Confirm:
- Header shows the new contact line including `jakethehoffer.github.io/website`
- Skills paragraph in Summary of Qualifications includes FastAPI, Playwright, Google Apps Script
- `PERSONAL PROJECTS` section appears after Experience with `trader` and `Odds Aggregator` entries

If the resume now spans 2 pages, note it. Trimming an existing bullet
to bring it back to 1 page would be a follow-up scope-discussion.

- [ ] **Step 3: Commit the regenerated PDF**

```bash
git -C "C:/Users/14jak/GitHub/website" add resume.pdf
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: regenerate resume.pdf with refreshed content"
```

---

## Task 4: Push + final live verify

**Files:** none modified.

- [ ] **Step 1: Push and wait for redeploy**

```bash
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
echo "polling for Pages redeploy..."
for i in 1 2 3 4 5 6; do
  sleep 25
  size=$(curl -sI "https://jakethehoffer.github.io/website/resume.pdf" 2>/dev/null | grep -i 'content-length' | awk '{print $2}' | tr -d '\r')
  echo "  attempt $i: live resume.pdf content-length: $size"
  if [ -n "$size" ] && [ "$size" -gt 100000 ]; then echo "  served"; break; fi
done
```

- [ ] **Step 2: Spot-check the live PDF**

```bash
curl -sI "https://jakethehoffer.github.io/website/resume.pdf" | head -10
```

Expected: `HTTP/1.1 200`, `content-type: application/pdf`, content-length
larger than the previous 105106 bytes (or comparable — depends on
content density).

- [ ] **Step 3: Commit the plan + handoff**

```bash
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-resume-refresh.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add resume-refresh implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3

powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.ai-sync/ai-sync.ps1" -Action handoff -Agent claude -Summary "v2.8: refreshed resume-source.docx and regenerated resume.pdf. Contact header now includes jakethehoffer.github.io/website. Skills line in Summary of Qualifications adds FastAPI, Playwright, Google Apps Script. New PERSONAL PROJECTS section after Experience with trader and Odds Aggregator (3 bullets each, formatting cloned from Lynx Equity entries so styling matches)." -FilesChanged "resume-source.docx (in-place updated by scripts/refresh-resume.py), resume.pdf (regenerated), scripts/refresh-resume.py (NEW, committed for reproducibility), docs/superpowers/specs/2026-05-12-resume-refresh.md, docs/superpowers/plans/2026-05-12-resume-refresh.md" -TestsRun "Script is idempotent (second run shows [same] for all three sections). Visual PDF check: trader/Odds Aggregator entries present, formatting matches Experience section, URL visible in header." -Blockers "Privacy note: full home address remains in the contact header and is publicly downloadable via resume.pdf — flagged for Jake to decide separately. Resume page-count: TBD at run time; may grow to 2 pages with the new section." -NextSteps "1) [miss] log fix in refresh-meta.mjs (v2.9). 2) Consider tightening contact header to 'Toronto, ON' for privacy. 3) Custom domain. 4) Share URL with reviewers."
```

---

## Closing checklist

- [ ] All 4 tasks checked off
- [ ] `scripts/refresh-resume.py` exists and re-running it is a no-op
- [ ] `resume-source.docx` has the three additions, all formatted consistently with neighbors
- [ ] `resume.pdf` regenerated; visual check passed
- [ ] Both files pushed to `origin/main` and served from the live URL
- [ ] Plan + handoff committed
