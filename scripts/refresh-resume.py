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
from docx.text.paragraph import Paragraph

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

# Structured as (paragraph_type, text). Templates are cloned from
# existing EXPERIENCE paragraphs:
#   - heading -> "EXPERIENCE" paragraph
#   - role    -> "IT Intern" paragraph (bold + dates)
#   - org     -> "Lynx Equity Limited" paragraph
#   - bullet  -> any Lynx Equity bullet (numbered list)
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
    ("bullet",  "Ingest → normalize → detect cross-book arbs → push "
                "alerts to Telegram and Discord. Runs 24/7 with replay "
                "tooling for postmortems."),
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


def set_paragraph_text(p: Paragraph, new_text: str) -> None:
    """Replace text in `p` while keeping the formatting of its first run."""
    runs = p.runs
    if not runs:
        p.add_run(new_text)
        return
    runs[0].text = new_text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def clone_paragraph_element(template_p: Paragraph):
    return copy.deepcopy(template_p._element)


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
        print("[ok] contact line updated")
    else:
        print("[same] contact line already has website URL")

    # --- 2. Skills line in Summary of Qualifications ---
    body = doc.paragraphs
    skills_p = find_para(body, lambda p: p.text.startswith("Proficient in "))
    if skills_p is None:
        raise RuntimeError("Could not find skills paragraph.")
    if skills_p.text != NEW_SKILLS_LINE:
        set_paragraph_text(skills_p, NEW_SKILLS_LINE)
        print("[ok] skills line updated")
    else:
        print("[same] skills line already updated")

    # --- 3. PERSONAL PROJECTS section ---
    experience_heading = find_para(body, lambda p: p.text.strip() == "EXPERIENCE")
    if experience_heading is None:
        raise RuntimeError("Could not find EXPERIENCE heading.")

    role_template = find_para(body, lambda p: p.text.strip().startswith("IT Intern"))
    org_template = find_para(body, lambda p: p.text.strip() == "Lynx Equity Limited")
    bullet_template = find_para(body, lambda p: p.text.startswith("Developed a task management system"))
    if not all([role_template, org_template, bullet_template]):
        raise RuntimeError("Could not find template paragraphs.")

    templates = {
        "heading": experience_heading,
        "role":    role_template,
        "org":     org_template,
        "bullet":  bullet_template,
    }

    already = find_para(body, lambda p: p.text.strip() == "PERSONAL PROJECTS")
    if already is not None:
        print("[same] PERSONAL PROJECTS section already present")
    else:
        # Insert after the last body paragraph.
        anchor = body[-1]._element
        for kind, text in NEW_SECTION:
            template = templates[kind]
            new_el = clone_paragraph_element(template)
            anchor.addnext(new_el)
            anchor = new_el
            wrapper = Paragraph(new_el, None)
            set_paragraph_text(wrapper, text)
        print(f"[ok] inserted PERSONAL PROJECTS section ({len(NEW_SECTION)} paragraphs)")

    # --- save ---
    doc.save(str(DOCX))
    print(f"wrote {DOCX}")


if __name__ == "__main__":
    main()
