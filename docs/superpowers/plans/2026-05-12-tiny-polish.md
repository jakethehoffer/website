# Tiny Polish v2.6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land three small polish items: a weekly GitHub Action for `refresh-meta.mjs`, one ad-hoc refresh, and two `<meta>` hygiene additions.

**Architecture:** One new YAML workflow, one ad-hoc script run, two narrow HTML edits. No CSS, no JS, no new assets.

**Tech Stack:** GitHub Actions, Node (existing `refresh-meta.mjs`), HTML edits, `gh` CLI for workflow dispatch.

**Spec:** `docs/superpowers/specs/2026-05-12-tiny-polish.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── .github/workflows/
│   └── refresh-meta.yml                  NEW
├── index.html                             MODIFIED (head + possibly fresh dates)
├── 404.html                               MODIFIED (head)
└── docs/superpowers/plans/
    └── 2026-05-12-tiny-polish.md          THIS DOC
```

---

## Verification Approach

Static site, no test suite. Per-task verification:
- Workflow file: linted by GitHub on push; manual `gh workflow run` confirms it parses and executes
- Meta tags: `grep` checks in served HTML
- Final: Lighthouse spot-check confirms no regression

---

## Task 1: Run `refresh-meta.mjs` once (ad-hoc refresh)

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (potentially — only if dates changed)

- [ ] **Step 1: Run the script**

```bash
node "C:/Users/14jak/GitHub/website/scripts/refresh-meta.mjs"
```

Expected output: `[ok]` lines for `trader.last_commit`,
`arbitrage.last_commit`, and `[removed].last_commit` (the local `gh`
login has access to all three), plus a `last_deployed` update. If
any repo returns `[skip]`, the corresponding default string stays.

- [ ] **Step 2: Check whether anything actually changed**

```bash
git -C "C:/Users/14jak/GitHub/website" status --porcelain index.html
```

If the output is empty, nothing changed (the previous run's dates
are still current); skip the commit and move on. If it shows a
modification, continue.

- [ ] **Step 3: Commit if changed**

```bash
git -C "C:/Users/14jak/GitHub/website" diff --stat index.html
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "chore: refresh project last-commit metadata"
```

If Step 2 was empty, this whole step is a no-op.

---

## Task 2: Add the GitHub Actions workflow

**Files:**
- Create: `C:/Users/14jak/GitHub/website/.github/workflows/refresh-meta.yml`

- [ ] **Step 1: Create the workflow file**

```yaml
name: refresh-meta

on:
  schedule:
    # Monday 12:00 UTC weekly.
    - cron: "0 12 * * 1"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run refresh-meta.mjs
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: node scripts/refresh-meta.mjs

      - name: Commit if changed
        run: |
          if [ -n "$(git status --porcelain index.html)" ]; then
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add index.html
            git commit -m "chore: refresh project last-commit metadata [auto]"
            git push
          else
            echo "No metadata changes; nothing to commit."
          fi
```

- [ ] **Step 2: Commit and push the workflow**

```bash
git -C "C:/Users/14jak/GitHub/website" add .github/workflows/refresh-meta.yml
git -C "C:/Users/14jak/GitHub/website" commit -m "feat(ops): add weekly refresh-meta GitHub Action"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

- [ ] **Step 3: Verify GitHub registers the workflow**

```bash
sleep 10
gh workflow list -R jakethehoffer/website 2>&1 | head -10
```

Expected: a `refresh-meta` entry with state `active`. If GitHub
hasn't picked it up yet, wait another 30 seconds and retry — the
indexer can lag briefly after a push.

- [ ] **Step 4: Dispatch the workflow manually as a smoke test**

```bash
gh workflow run refresh-meta.yml -R jakethehoffer/website
echo "dispatched; polling for completion..."
for i in 1 2 3 4 5 6 7 8; do
  sleep 15
  status=$(gh run list -R jakethehoffer/website --workflow=refresh-meta.yml --limit 1 --json status,conclusion --jq '.[0]')
  echo "  attempt $i: $status"
  echo "$status" | grep -q '"status":"completed"' && break
done
```

Expected: the run completes within ~2 minutes. If `conclusion` is
`"failure"`, fetch logs with `gh run view --log` and stop —
investigate before continuing.

- [ ] **Step 5: Confirm the workflow either committed or correctly no-op'd**

```bash
git -C "C:/Users/14jak/GitHub/website" fetch origin main
git -C "C:/Users/14jak/GitHub/website" log origin/main --oneline -3
```

If the action found new dates and committed, you'll see a
`chore: refresh project last-commit metadata [auto]` commit by
`github-actions[bot]`. Pull it down:

```bash
git -C "C:/Users/14jak/GitHub/website" pull --ff-only
```

If the action found nothing to commit, no extra commit appears.
Either outcome is healthy.

---

## Task 3: Add the `<meta>` hygiene tags

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html`
- Modify: `C:/Users/14jak/GitHub/website/404.html`

- [ ] **Step 1: Add canonical + author to `index.html`**

Find the existing OG/Twitter/icon block in `index.html` `<head>`.
Currently it ends with the apple-touch-icon link. Immediately
after that line and before the closing `</head>`, add:

```html
    <link rel="canonical" href="https://jakethehoffer.github.io/website/" />
    <meta name="author" content="Jake Hoffman" />
```

The cleanest insertion point is right before the JSON-LD `<script>`
block. The resulting fragment looks like:

```html
    <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180" />
    <link rel="canonical" href="https://jakethehoffer.github.io/website/" />
    <meta name="author" content="Jake Hoffman" />
    <script type="application/ld+json">
```

- [ ] **Step 2: Add author to `404.html`**

In `404.html` `<head>`, find:

```html
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180" />
```

Add right after it:

```html
    <meta name="author" content="Jake Hoffman" />
```

No canonical on 404 — standard practice; the page doesn't represent
the canonical content of any URL.

- [ ] **Step 3: Verify structurally**

```bash
echo "index.html canonical (expected 1):"
grep -c 'rel="canonical"' "C:/Users/14jak/GitHub/website/index.html"
echo "index.html author    (expected 1):"
grep -c 'name="author"'    "C:/Users/14jak/GitHub/website/index.html"
echo "404.html author      (expected 1):"
grep -c 'name="author"'    "C:/Users/14jak/GitHub/website/404.html"
echo "404.html canonical   (expected 0):"
grep -c 'rel="canonical"' "C:/Users/14jak/GitHub/website/404.html"
```

Expected: 1 / 1 / 1 / 0.

- [ ] **Step 4: Commit and push**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html 404.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add canonical URL and author meta tags"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

---

## Task 4: Live verification + Lighthouse spot-check

**Files:** none modified (verification only).

- [ ] **Step 1: Wait for Pages redeploy + verify served HTML**

```bash
echo "polling for live deploy with new meta tags..."
for i in 1 2 3 4 5 6; do
  sleep 25
  c=$(curl -s https://jakethehoffer.github.io/website/ | grep -c 'rel="canonical"')
  a=$(curl -s https://jakethehoffer.github.io/website/ | grep -c 'name="author"')
  echo "  attempt $i: canonical=$c author=$a"
  if [ "$c" -ge 1 ] && [ "$a" -ge 1 ]; then echo "  deployed"; break; fi
done
echo ""
echo "=== 404 page author meta ==="
curl -s https://jakethehoffer.github.io/website/404.html | grep -c 'name="author"'
echo "(expected: 1)"
```

- [ ] **Step 2: Lighthouse spot-check (mobile only)**

We re-audited the full perf in v2.5; this is a confirmation that
the three new lines didn't regress anything. Mobile is the more
demanding strategy and the one most worth spot-checking.

```bash
mkdir -p "C:/Users/14jak/GitHub/website/.tmp"
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v26.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3
```

- [ ] **Step 3: Summarize**

```bash
PYTHONIOENCODING=utf-8 python <<'PY'
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r"C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v26.json", encoding="utf-8") as f:
    data = json.load(f)
print("=== v2.6 mobile spot-check ===")
for k in ("performance","accessibility","best-practices","seo"):
    s = (data["categories"][k].get("score") or 0) * 100
    flag = "PASS" if s >= 95 else "FAIL"
    print(f"  {data['categories'][k]['title']:25s} {s:5.1f}  {flag}")
print(f"  CLS: {data['audits']['cumulative-layout-shift']['displayValue']}")
PY
```

Expected: all 4 categories at 100, CLS 0.

- [ ] **Step 4: Cleanup, plan commit, handoff**

```bash
rm -rf "C:/Users/14jak/GitHub/website/.tmp" 2>&1 || true
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-tiny-polish.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add tiny-polish implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3

powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.ai-sync/ai-sync.ps1" -Action handoff -Agent claude -Summary "Tiny polish v2.6: GitHub Action auto-refreshes project metadata every Monday, ad-hoc refresh ran before tagging, canonical + author meta tags added. Mobile Lighthouse spot-check confirms no regression from v2.5's 100/100/100/100." -FilesChanged ".github/workflows/refresh-meta.yml (NEW), index.html (head: canonical + author; possibly fresh dates), 404.html (head: author), docs/superpowers/specs/2026-05-12-tiny-polish.md, docs/superpowers/plans/2026-05-12-tiny-polish.md" -TestsRun "Manual workflow dispatch via gh workflow run confirms the Action executes end-to-end. Live HTML serves the new meta tags. Mobile Lighthouse 100/100/100/100." -Blockers "none" -NextSteps "1) Submit sitemap to Google Search Console manually: search.google.com/search-console -> add property -> verify (HTML file or DNS) -> submit /sitemap.xml. 2) Consider custom domain (jakehoffman.dev) for the biggest brand uplift left. 3) Share the live URL with reviewers for real human feedback."
```

---

## Closing checklist

After Task 4:
- [ ] All 4 tasks checked off
- [ ] `.github/workflows/refresh-meta.yml` exists and the smoke-test dispatch completed successfully
- [ ] `<link rel="canonical">` and `<meta name="author">` live on `index.html`; `<meta name="author">` live on `404.html`
- [ ] Mobile Lighthouse spot-check still 100/100/100/100
- [ ] Everything pushed to `origin/main`
- [ ] Handoff updated
