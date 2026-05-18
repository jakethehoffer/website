# v2.17 tax-rebalance Project — Implementation Plan

> **For agentic workers:** Inline execution by the controller; sub-skill not used because edits are small, sequential, and need cross-file verification.

**Goal:** Add `tax-rebalance` as a 6th project card on the website and a 3rd entry in the resume's PERSONAL PROJECTS section. Regenerate `resume.pdf`, keep page count at 1.

**Architecture:** Three hand-edits (index.html, refresh-meta.mjs, refresh-resume.py), one idempotency refactor (per-entry NEW_SECTION check instead of all-or-nothing), one PDF regen via LibreOffice. One feature commit, tag `v2.17`.

**Spec:** `docs/superpowers/specs/2026-05-18-tax-rebalance-project.md`

---

## File map

- Modify: `index.html` — insert new `<article class="project">` between OA card (ends ~line 189) and Mega TTT card (starts ~line 191)
- Modify: `scripts/refresh-meta.mjs` — add 3rd entry to `REPOS` array
- Modify: `scripts/refresh-resume.py` — refactor NEW_SECTION idempotency (per-entry walk-anchor), add tax-rebalance entries, possibly add a `PARAGRAPHS_TO_DROP` entry for page fit
- Regenerate: `resume-source.docx` (untracked) and `resume.pdf` (tracked)

---

## Task 1: Refactor `refresh-resume.py` NEW_SECTION to walk-anchor idempotency

**Files:**
- Modify: `scripts/refresh-resume.py` — replace the `# --- 4. PERSONAL PROJECTS section ---` block in `main()` (currently lines ~295–326)

- [ ] **Step 1: Locate the current block**

The current block in `main()` looks like (around lines 295–326):

```python
    # --- 4. PERSONAL PROJECTS section ---
    body = doc.paragraphs  # re-read after trim
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

- [ ] **Step 2: Replace with walk-anchor logic**

Replace the entire block above with:

```python
    # --- 4. PERSONAL PROJECTS section (per-entry idempotent) ---
    body = doc.paragraphs  # re-read after trim
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

    # Walk-anchor idempotent insert: for each NEW_SECTION entry, find
    # a matching paragraph in the body. If present, advance the anchor;
    # if absent, clone the template, set text, insert after anchor.
    # Matching: heading uses exact text equality (after strip); role
    # and bullet use prefix match on the first 30 chars (enough to
    # disambiguate without being fragile to em-dash/punctuation drift).
    def _matches(p, kind, text):
        if kind == "heading":
            return p.text.strip() == text
        return p.text.strip().startswith(text[:30].strip())

    # Initial anchor: just before where the section should land. We
    # use the document's last paragraph when the section is absent
    # (matches old behavior). When the section is already partially
    # built, the heading's element is found and anchor walks from there.
    anchor_el = doc.paragraphs[-1]._element
    inserted = 0
    skipped = 0
    body = doc.paragraphs  # re-read; may have been mutated
    for kind, text in NEW_SECTION:
        existing = find_para(body, lambda p: _matches(p, kind, text))
        if existing is not None:
            anchor_el = existing._element
            skipped += 1
            continue
        template = templates[kind]
        new_el = clone_paragraph_element(template)
        anchor_el.addnext(new_el)
        anchor_el = new_el
        wrapper = Paragraph(new_el, None)
        set_paragraph_text(wrapper, text)
        inserted += 1
        body = doc.paragraphs  # re-read after mutation

    if inserted == 0:
        print(f"[same] PERSONAL PROJECTS section already present ({skipped} entries)")
    else:
        print(f"[ok]   PERSONAL PROJECTS: inserted {inserted} entry(ies), {skipped} already present")
```

- [ ] **Step 3: Verify the script still parses**

```bash
python -c "import ast; ast.parse(open('scripts/refresh-resume.py').read()); print('syntax OK')"
```

Expected: `syntax OK`

Do **not** commit yet.

---

## Task 2: Add tax-rebalance entries to NEW_SECTION

**Files:**
- Modify: `scripts/refresh-resume.py` — extend the `NEW_SECTION` list (currently ending at line ~89)

- [ ] **Step 1: Verify the existing NEW_SECTION**

```bash
grep -A2 'NEW_SECTION = \[' scripts/refresh-resume.py | head -3
```

Expected: shows the list opening with `("heading", "PERSONAL PROJECTS")`.

- [ ] **Step 2: Add the three new entries**

In `scripts/refresh-resume.py`, find the closing `]` of `NEW_SECTION` (currently at line 89, right after the second OA bullet). Replace this:

```python
    ("bullet",  "Ingest → normalize → detect cross-book arbs → push "
                "alerts to Telegram and Discord. Runs 24/7 with replay "
                "tooling for postmortems."),
]
```

with:

```python
    ("bullet",  "Ingest → normalize → detect cross-book arbs → push "
                "alerts to Telegram and Discord. Runs 24/7 with replay "
                "tooling for postmortems."),
    ("role",    "tax-rebalance (Python · async SQLAlchemy 2 · httpx · pytest)"),
    ("bullet",  "Canadian TFSA + RRSP portfolio drift monitor — emails "
                "weekly digests with cost-aware rebalance verdicts. "
                "Read-only; never places trades."),
    ("bullet",  "Spec-driven TDD: 21-task plan executed task-by-task "
                "with two-stage subagent review. 117 tests, zero ruff "
                "violations, CI on Python 3.11 + 3.13. Questrade IQ "
                "API with OAuth refresh-token rotation."),
]
```

Do **not** commit yet.

---

## Task 3: Add the tax-rebalance project card to `index.html`

**Files:**
- Modify: `index.html` — insert between OA card (`</article>` ending ~line 189) and Mega TTT card (`<article ...>` starting ~line 191)

- [ ] **Step 1: Confirm insertion point**

```bash
grep -n 'NHL · Edmonton @ Vegas\|Mega Tic-Tac-Toe' index.html
```

Expected: first match is the OA card's sample (around line 185), second is the Mega TTT card heading (around line 197). The `</article>` immediately after the first is the OA card's closing tag.

- [ ] **Step 2: Insert the new card**

Find this block in `index.html` (the OA card ending and the start of Mega TTT):

```html
<span class="sample__hi">[ARB]</span> NHL &middot; Edmonton @ Vegas
  pinnacle  EDM -132   &rarr;  stake 0.567
  betmgm    VGK +145   &rarr;  stake 0.433
  edge      <span class="sample__ok">+0.84%</span>      ttl 4m12s</pre>
            </article>

            <article class="project">
              <header class="project__head">
                <span class="status status--shipped" role="img" aria-label="Status: shipped"></span>
                <span class="project__status-label">SHIPPED</span>
                <span class="project__last-commit">mar 2024</span>
              </header>
              <h3 class="project__name"><a href="https://jakethehoffer.itch.io/mega-tictactoe" target="_blank" rel="noopener">Mega Tic-Tac-Toe</a></h3>
```

Insert the new tax-rebalance card between the OA card's `</article>` and the Mega TTT `<article class="project">`. The replacement is:

```html
<span class="sample__hi">[ARB]</span> NHL &middot; Edmonton @ Vegas
  pinnacle  EDM -132   &rarr;  stake 0.567
  betmgm    VGK +145   &rarr;  stake 0.433
  edge      <span class="sample__ok">+0.84%</span>      ttl 4m12s</pre>
            </article>

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

            <article class="project">
              <header class="project__head">
                <span class="status status--shipped" role="img" aria-label="Status: shipped"></span>
                <span class="project__status-label">SHIPPED</span>
                <span class="project__last-commit">mar 2024</span>
              </header>
              <h3 class="project__name"><a href="https://jakethehoffer.itch.io/mega-tictactoe" target="_blank" rel="noopener">Mega Tic-Tac-Toe</a></h3>
```

- [ ] **Step 3: Verify the card landed**

```bash
grep -n 'tax-rebalance' index.html
```

Expected: 3 matches (data-meta sentinel, href, project name in title).

```bash
grep -c '<article class="project">' index.html
```

Expected: `6` (was 5, now 6).

Do **not** commit yet.

---

## Task 4: Add tax-rebalance to refresh-meta.mjs

**Files:**
- Modify: `scripts/refresh-meta.mjs` — extend the REPOS array (currently line 20–23)

- [ ] **Step 1: Verify current REPOS**

```bash
grep -A4 'const REPOS = ' scripts/refresh-meta.mjs
```

Expected:

```javascript
const REPOS = [
  { owner: "jakethehoffer", name: "trader",    key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage", key: "arbitrage.last_commit" },
];
```

- [ ] **Step 2: Add the new entry**

Replace the REPOS block above with:

```javascript
const REPOS = [
  { owner: "jakethehoffer", name: "trader",        key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage",     key: "arbitrage.last_commit" },
  { owner: "jakethehoffer", name: "tax-rebalance", key: "tax-rebalance.last_commit" },
];
```

(Field alignment is purely cosmetic; the JS parser doesn't care.)

- [ ] **Step 3: Verify**

```bash
grep -c 'tax-rebalance' scripts/refresh-meta.mjs
```

Expected: `2` (both `name:` and `key:` references).

Do **not** commit yet.

---

## Task 5: Run refresh-resume + verify idempotency

**Files:** runs the script, modifies the local-only `resume-source.docx`

- [ ] **Step 1: First run**

```bash
python scripts/refresh-resume.py
```

Expected output (idempotent for everything except the new tax-rebalance entries and the Writing line if not present):

```
[same] contact line already has 3 hyperlinks and matching text
[same] skills line already updated
[ok]   trimmed 1 paragraph(s)      # QMIND bullet 3 (already in PARAGRAPHS_TO_DROP)
[ok]   PERSONAL PROJECTS: inserted 3 entry(ies), 7 already present
[same] Writing line already present
[ok]   scrubbed Office metadata (author, comments, etc.)
wrote ...
```

If `[ok] PERSONAL PROJECTS: inserted 3 entry(ies)` doesn't appear, the walk-anchor refactor has a bug — stop and diagnose.

- [ ] **Step 2: Second run (idempotency)**

```bash
python scripts/refresh-resume.py
```

Expected: same except `[same] PERSONAL PROJECTS section already present (10 entries)`. If `[ok] inserted` reappears, the idempotency check on the new entries is broken.

---

## Task 6: Regenerate PDF and check page fit

- [ ] **Step 1: Convert to PDF**

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
```

- [ ] **Step 2: Replace tracked PDF**

```bash
mv resume-source.pdf resume.pdf
```

- [ ] **Step 3: Verify page count and content**

```bash
python -c "
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pypdf import PdfReader
r = PdfReader('resume.pdf')
print(f'pages: {len(r.pages)}')
t1 = r.pages[0].extract_text()
print('tax-rebalance role on page 1:', 'tax-rebalance (Python' in t1)
print('Writing line on page 1:', 'Writing:' in t1)
"
```

Expected:
- `pages: 1`
- `tax-rebalance role on page 1: True`
- `Writing line on page 1: True`

- [ ] **Step 4: If 2 pages — drop SUMMARY bullet 4**

If page count is 2, add `"Collaborates with non-technical teammates"` to `PARAGRAPHS_TO_DROP` in `scripts/refresh-resume.py`:

```python
PARAGRAPHS_TO_DROP = [
    # Lynx Equity bullets (lower-signal items)
    "Designed Monday.com form that prefills",
    "Conducted DNS lookups",
    # BMC Pharmacy entry — ...
    ...
    # SUMMARY bullet 4 — generic soft-skill line, dropped in v2.17
    # to make room for tax-rebalance.
    "Collaborates with non-technical teammates",
]
```

Re-run script (Step 1 of Task 5), regenerate PDF (Steps 1–2 of this Task), recheck page count.

- [ ] **Step 5: If still 2 pages — drop trader's resume bullet 2**

If page count is still 2 after Step 4, add:

```python
    # trader bullet 2 — kill-switch/risk-gate story is told in full
    # in the website case study; resume can stay terse.
    "Paper-traded against SPY with kill-switch",
```

Re-run, regenerate, recheck. If still 2 at this point, surface to user.

---

## Task 7: Commit, push, tag v2.17

- [ ] **Step 1: Review diff**

```bash
git status
git diff --stat
```

Expected: 3-4 files modified (index.html, scripts/refresh-meta.mjs, scripts/refresh-resume.py, resume.pdf) plus this plan doc to add. No deletions.

- [ ] **Step 2: Commit**

```bash
git add index.html scripts/refresh-meta.mjs scripts/refresh-resume.py resume.pdf docs/superpowers/plans/2026-05-18-tax-rebalance-project.md
git commit -m "$(cat <<'EOF'
feat: add tax-rebalance project to website + resume

Three additions:
- New ACTIVE project card on the website between Odds Aggregator and
  Mega Tic-Tac-Toe. Python async CLI that monitors Canadian TFSA+RRSP
  portfolio drift and emails weekly digests with cost-aware rebalance
  verdicts. Read-only — never places trades. Spec-driven TDD, 117
  tests, ruff-clean, CI on Py 3.11 + 3.13.
- New REPOS entry in refresh-meta.mjs so the weekly cron auto-updates
  the last-commit timestamp. Note: META_REFRESH_TOKEN PAT must be
  extended to include tax-rebalance read access; script gracefully
  [skip]s until that's done.
- New role + 2 bullets in resume PERSONAL PROJECTS. Refactored
  NEW_SECTION idempotency from all-or-nothing to per-entry
  walk-anchor so future project adds work the same way.

[NOTE: implementor — replace this line with the actual page-fit
mitigation taken. Either "PDF stayed at 1 page on first try" or
"Dropped SUMMARY bullet 4 to fit" or "Dropped SUMMARY bullet 4 +
trader bullet 2 to fit", per Task 6 outcome.]

Spec: docs/superpowers/specs/2026-05-18-tax-rebalance-project.md
Plan: docs/superpowers/plans/2026-05-18-tax-rebalance-project.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Push + wait for CI**

```bash
git push
until gh run list --workflow=public-safety.yml --limit 1 | grep -q "completed"; do sleep 3; done
gh run list --workflow=public-safety.yml --limit 1
```

Expected: `completed success` within ~15s.

- [ ] **Step 4: Tag and push tag**

```bash
git tag v2.17
git push --tags
```

- [ ] **Step 5: AI sync handoff**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "v2.17: added tax-rebalance project to website (6th card, ACTIVE) and resume (3rd PERSONAL PROJECTS entry). Refactored refresh-resume.py NEW_SECTION idempotency to per-entry walk-anchor so future adds work." -FilesChanged "index.html, scripts/refresh-meta.mjs, scripts/refresh-resume.py, resume.pdf, spec + plan docs" -TestsRun "refresh-resume idempotency [ok] then [same]; PDF 1 page; tax-rebalance + Writing both on page 1; public-safety CI green" -Blockers "User needs to extend META_REFRESH_TOKEN PAT to include jakethehoffer/tax-rebalance read access (one-time GitHub Settings edit) so weekly cron auto-updates the timestamp" -NextSteps "Site has 3 ACTIVE projects + 3 SHIPPED. Resume reflects all 3 active. If more projects added (e.g., 4th, 5th), the walk-anchor idempotency handles it automatically. Honest diminishing-returns ceiling remains for autonomous site improvements."
```

---

## Acceptance criteria (from spec)

After Task 7, all must hold:

1. `index.html` has 6 project cards. **(Task 3 Step 3)**
2. `refresh-meta.mjs` REPOS has 3 entries. **(Task 4 Step 3)**
3. `refresh-resume.py` NEW_SECTION has tax-rebalance role + 2 bullets. **(Task 2 Step 2 + Task 5 verification)**
4. Script idempotency: re-run produces no change. **(Task 5 Step 2)**
5. `resume.pdf` is 1 page. **(Task 6 Step 3, or after Step 4/5 fallbacks)**
6. tax-rebalance role line at role-template indent in PDF. **(implicit; visible in PDF)**
7. `public-safety` CI passes. **(Task 7 Step 3)**
8. Tag `v2.17` pushed. **(Task 7 Step 4)**

---

## Plan self-review

**Spec coverage:** All 8 AC mapped. ✓

**Placeholder scan:** No TBDs in actionable steps. The commit-message has a marked `[NOTE: implementor — replace ...]` placeholder, which is intentional and explicit. The implementor (me) fills it in when committing.

**Type consistency:** `find_para`, `clone_paragraph_element`, `set_paragraph_text`, `Paragraph` are all existing in the script. The new `_matches` helper is a local closure inside the walk-anchor block, scoped correctly. The `body = doc.paragraphs` re-reads after mutation are necessary because `body` is a list snapshot.

**Failure paths:**
- 2-page tip: Task 6 Steps 4 + 5 cascade with clear stopping points.
- Walk-anchor regression on existing entries: Task 5 Step 2 catches by checking idempotency on a re-run.
- META_REFRESH_TOKEN PAT scope: surfaced in commit message + sync handoff (user-side action).

**Out-of-scope creep:** Stays in 3 specified files + PDF. No changes to other sections.
