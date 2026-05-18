# v2.18 — projects.yml + three generators (auto-handling)

Date: 2026-05-18

## Why

Adding a new project today means three coordinated hand-edits
(`index.html` card, `refresh-resume.py NEW_SECTION`, `refresh-meta.mjs
REPOS`) plus a PDF regen. The failure mode is silent drift: resume
mentions a project the site doesn't, or vice versa. At the user's
actual project cadence (more than 2-3/year), the manual pattern is
fragile.

This cycle introduces a single source of truth (`projects.yml`) plus
three generators that read it. After this lands, adding a project
becomes: edit one entry in `projects.yml`, run `python scripts/build-site.py`,
commit. The three downstream files (`index.html` projects block,
`resume.pdf`, last-commit timestamps) stay in lockstep automatically.

Concurrent with the migration, this cycle adds a 7th project:
`equity-arbs` (SHIPPED, retired at v1.0 with documented negative
result).

## Architecture

```
projects.yml                  ← single source of truth
    │
    ├──→ scripts/generate-cards.py   ──→ index.html (projects block)
    ├──→ scripts/refresh-resume.py   ──→ resume-source.docx → resume.pdf
    └──→ scripts/refresh-meta.py     ──→ index.html (last-commit data-meta sentinels)
                                          (replaces refresh-meta.mjs)

scripts/build-site.py        ← orchestrator that calls all three
```

Decision rationale:

- **YAML** for the config format. Human-readable, supports multi-line
  strings cleanly, parses via Python's `yaml` library (already a likely
  dep via `python-docx` ecosystem; if not, add `pyyaml`).
- **Python** for all three generators. Eliminates the Node dependency
  the old `refresh-meta.mjs` introduced (no js-yaml, no package.json),
  unifies the toolchain, lets refresh-meta share parsing code with the
  others.
- **Markers around the projects block** in `index.html` so
  `generate-cards.py` knows exactly what region to replace without
  parsing the whole HTML.

## projects.yml schema

One YAML list. Each entry:

```yaml
- key: trader                    # short id, also used in data-meta="<key>.last_commit"
  name: trader                   # displayed name
  status: active                 # active | shipped | archived
  url: https://github.com/jakethehoffer/trader   # public link; may 404 if private/unpublished
  meta_key: trader.last_commit   # data-meta sentinel key; usually "{key}.last_commit"
  auto_meta: true                # if true, refresh-meta.py auto-updates last-commit; if false, use hardcoded_date
  hardcoded_date: null           # fallback string when auto_meta is false (e.g. "mar 2024", "2024")
  what: |                        # 1-2 sentence project lede
    24/7 AI swing-trading agent for S&P 500 equities, driven by six scheduled Claude Code routines.
  body: |                        # longer description (~80-120w)
    Paper-traded on IBKR + Finnhub news; graduates to live only after 30 paper days of documented outperformance. Designed the risk model, journaling, and kill-switch from day one.
  metrics: "s&p 500 · 6 scheduled agents · ibkr paper"   # terse stats line; HTML entities pre-encoded
  chips: "python · pytest · ib_async · finnhub · claude code"
  sample:                        # optional code-block sample
    label: "Example daemon log"  # aria-label
    html: |                      # raw HTML body; supports <span class="sample__dim|ok|hi"> for color
      <span class="sample__dim">// example daemon log</span>
      <span class="sample__dim">[2026-05-12 09:31:02]</span> <span class="sample__ok">scan_premarket</span>: ...
  media: null                    # OR a {src, alt, width, height} object for image
  cta: null                      # OR a {label, url} object for an external CTA button
  resume:                        # optional resume entry
    role: "trader (Python · IBKR · Finnhub · pytest)"
    bullets:
      - "24/7 AI swing-trading agent for S&P 500 equities, driven by six scheduled Claude Code routines."
```

Cards are rendered in the order they appear in the YAML. Position in
`projects.yml` controls position on the page.

For a project without a `resume:` block (e.g., a project too small for
the resume), the resume generator skips it.

## generate-cards.py contract

- Reads `projects.yml` and `index.html`.
- Locates the `<div class="projects">` block by HTML markers (begin/end
  comments).
- Renders each project entry as the existing `<article class="project">`
  template.
- Replaces the block in `index.html` atomically (read full file →
  modify → write full file).
- Idempotent: running twice with no `projects.yml` changes produces no
  diff in `index.html`.
- Order: matches `projects.yml` order exactly.

## refresh-resume.py changes

The current `NEW_SECTION` constant (10 hardcoded tuples) gets removed.
A new function `build_resume_section(projects_yaml)` walks the YAML
and produces an equivalent list of `(kind, text)` tuples for the
walk-anchor logic to consume. The first tuple is always `("heading",
"PERSONAL PROJECTS")`. Each project with a `resume:` block produces
`("role", role_text)` followed by `("bullet", bullet_text)` for each
bullet.

The walk-anchor logic from v2.17 stays untouched.

`PARAGRAPHS_TO_DROP` stays as-is (it's about trimming existing
content, orthogonal to the YAML source).

## refresh-meta.py (replaces refresh-meta.mjs)

Port refresh-meta.mjs to Python. Reads `projects.yml`, filters for
entries where `auto_meta: true`, runs `gh api repos/<owner>/<repo>`
for each, humanizes the `pushed_at` value, rewrites the
`data-meta="<meta_key>"` span in `index.html`. Also stamps the
footer `data-meta="last_deployed"`.

GitHub Action workflow (`.github/workflows/refresh-meta.yml`) updates
to call `python scripts/refresh-meta.py` instead of `node scripts/refresh-meta.mjs`.

After conversion, delete `refresh-meta.mjs`.

## build-site.py orchestrator

A simple wrapper:

```python
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(name, *args):
    print(f"\n=== {name} ===")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / name), *args])
    if result.returncode != 0:
        raise SystemExit(f"{name} failed with exit {result.returncode}")

if __name__ == "__main__":
    run("generate-cards.py")
    run("refresh-resume.py")
    run("refresh-meta.py")
```

Running `python scripts/build-site.py` from the repo root regenerates
everything from `projects.yml`. The user then runs the existing
LibreOffice conversion to refresh the PDF.

## equity-arbs entry

Status: SHIPPED (retired at v1.0). The content is from the project's
own `docs/resume/equity-arbs-project-summary.md` doc, condensed:

- Position in projects.yml: between Mega Tic-Tac-Toe and Smart Shoe
  Navigation (chronologically newer than 2024 shipped projects, but
  most recently retired). Actually: position 4 in the ACTIVE+SHIPPED
  ordering — after the 3 ACTIVES, before the older SHIPPED projects.
- `auto_meta: true`, with hardcoded fallback "v1.0 · 2026" until the
  user pushes to `github.com/jakethehoffer/equity-arbs`.
- Resume bullets: 2 (role + 2 bullets), placed after Odds Aggregator
  but before tax-rebalance? Or alphabetical? Spec choice: keep
  trader → OA → tax-rebalance order (chronological/activity-based)
  and add equity-arbs at the end of PERSONAL PROJECTS, marked as
  retired. The "shipped a correct negative" framing is the headline.

Resume bullets:

- role: `equity-arbs (Python · asyncio · SQLAlchemy 2 · statsmodels · pydantic)`
- bullet 1: *"Stat-arb research toolkit for TSX pair trading. Spec-first, TDD, 76 unit tests."*
- bullet 2: *"Decision-grade backtest demonstrated a ~0.6%/yr ceiling on retail capital (below passive index); retired at v1.0 with the toolkit as a reusable research asset and a documented negative result."*

## Migration verification

Before declaring v2.18 done:

1. Run `generate-cards.py`. Diff `index.html`'s projects block before
   vs after the run. For the 6 existing projects, the diff must be
   only whitespace (the new card for equity-arbs is the only material
   change). The new card uses the same HTML structure as the others.
2. Run `refresh-resume.py`. Verify that the regenerated docx has the
   same PERSONAL PROJECTS entries as before, plus the new
   equity-arbs role + 2 bullets.
3. Run `refresh-meta.py` (or its equivalent invocation). Verify the
   data-meta spans get updated with current timestamps.
4. Regenerate the PDF. Verify 1 page (likely tight; may require an
   additional `PARAGRAPHS_TO_DROP` entry — see Risks).
5. Visual check of the rendered site (live or local).

## Page-fit risk (resume)

Adding equity-arbs is a 4th PERSONAL PROJECTS entry. v2.17 already
cut SUMMARY bullet 4, trader bullet 2, and OA bullet 2 to fit
tax-rebalance. Adding another role + 2 bullets is ~3 more lines.
Likely cuts (in order of preference):

1. Combine trader's remaining bullet with the role line by adding a
   parenthetical "(paper-traded; 30-day live gate)". Probably saves
   ~1 line.
2. Trim equity-arbs bullets — combine into one dense bullet.
3. Drop another EDUCATION bullet (the Walking/Jumping line is
   duplicated in the website's PROJECTS section).

The script needs to converge to 1 page; iterate fallbacks as in
v2.16/v2.17.

## Acceptance criteria

1. `projects.yml` exists in the repo root, contains 7 entries with
   the schema above, byte-equivalent representation of the existing 6
   projects' on-page content plus the new equity-arbs entry.
2. `scripts/generate-cards.py` exists and produces an `index.html`
   that matches the current file's projects block (modulo the new
   equity-arbs card and the order chosen).
3. `scripts/refresh-resume.py` no longer contains a hardcoded
   `NEW_SECTION` constant; it builds the section from `projects.yml`.
4. `scripts/refresh-meta.py` exists and works (calls `gh api`, parses
   YAML, updates index.html). `refresh-meta.mjs` is deleted.
5. `.github/workflows/refresh-meta.yml` updated to call the Python
   script.
6. `scripts/build-site.py` exists and runs all three generators in
   order.
7. README updated: documents how to add a project (edit `projects.yml`,
   run `build-site.py`, regenerate PDF, commit).
8. All scripts pass their idempotency check (running twice produces
   no diff).
9. `resume.pdf` regenerated, stays at 1 page, includes equity-arbs.
10. `public-safety` CI passes.
11. Tag `v2.18` pushed.

## Out of scope

- `equity-arbs` case study (separate cycle if/when wanted).
- Per-project OG share images.
- Auto-discovery of all GitHub repos (the YAML allow-list is the
  point).
- Pre-commit hook to auto-run `build-site.py` (manual is fine; can
  add later).
