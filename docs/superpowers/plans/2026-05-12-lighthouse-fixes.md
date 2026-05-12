# Lighthouse Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 4 specific audit failures from the v2.3 Lighthouse run so Performance ≥ 95 and Accessibility ≥ 95 on both mobile and desktop.

**Architecture:** Four narrow edits — one JS change (boot-sequence min-height), one HTML repeat (font preload + ARIA role), one CSS token darkening (parchment theme). No new files, no new dependencies, no visual redesign.

**Tech Stack:** Vanilla JS for the min-height measurement, plain HTML `<link rel="preload">`, CSS custom-property value tweaks, HTML ARIA attribute additions. Same toolchain as v2.3.

**Spec:** `docs/superpowers/specs/2026-05-12-lighthouse-fixes.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── index.html                              MODIFIED (preload + project-card role)
├── 404.html                                MODIFIED (preload)
├── styles.css                              MODIFIED (parchment tokens)
└── script.js                               MODIFIED (boot sequence min-height)
```

---

## Verification Approach

Static site, no test suite. Verifications are inline + a final
Lighthouse re-run against the *live* URL. Each task that touches code
runs structural checks (`grep`, `python -c`). The acceptance test is
the v2.4 Lighthouse audit hitting ≥ 95 across all four categories.

---

## Task 1: Reserve hero box height before clearing spans

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/script.js` (inside `bootSequence` IIFE)

- [ ] **Step 1: Add the min-height lock**

In `script.js`, find this block inside `bootSequence`:

```js
    // No-op path: leave the static end-state alone.
    if (reduceMotion || alreadyPlayed) return;

    const skipBtn = document.querySelector(".hero__skip");
    const cached = lines.map((el) => el.textContent);
    lines.forEach((el) => (el.textContent = ""));
```

Replace the block above with:

```js
    // No-op path: leave the static end-state alone.
    if (reduceMotion || alreadyPlayed) return;

    // CLS guard: lock the boot block's height to its pre-animation
    // rendered height before we clear the lines. Without this, the
    // <pre> collapses to ~3 lines and the page reflows ~15 times as
    // characters are typed back in.
    const preEl = document.querySelector(".hero__boot");
    if (preEl) {
      preEl.style.minHeight = preEl.getBoundingClientRect().height + "px";
    }

    const skipBtn = document.querySelector(".hero__skip");
    const cached = lines.map((el) => el.textContent);
    lines.forEach((el) => (el.textContent = ""));
```

- [ ] **Step 2: Verify locally**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > /tmp/lh1.log 2>&1 &
sleep 2
echo "served script.js"
curl -s http://localhost:8765/script.js | grep -c "CLS guard"
echo "(expected: 1)"
pkill -f "http.server 8765" 2>/dev/null
```

Expected: `1`.

Open the page in a browser, clear `sessionStorage.jh-boot-played`,
reload. The boot animation should play normally; the hero block
should *not* visibly shrink or grow during the animation.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add script.js
git -C "C:/Users/14jak/GitHub/website" commit -m "fix(perf): lock hero box height before boot animation to eliminate CLS"
```

---

## Task 2: Preload the WOFF2 font

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (head)
- Modify: `C:/Users/14jak/GitHub/website/404.html` (head)

- [ ] **Step 1: Add preload to `index.html`**

In `index.html` `<head>`, find this line (currently right after the
theme-preload `<script>`):

```html
    <meta name="description" content="Jake Hoffman — 3rd-year Computer Engineering student at Queen's University. Builds production-grade software in Python, JavaScript, C/C++, Java, and Dart." />
    <link rel="stylesheet" href="styles.css" />
```

Insert *between* the `<meta name="description">` and the
`<link rel="stylesheet">` lines:

```html
    <link rel="preload" href="assets/fonts/jetbrains-mono-variable.woff2" as="font" type="font/woff2" crossorigin />
```

Result:

```html
    <meta name="description" content="…" />
    <link rel="preload" href="assets/fonts/jetbrains-mono-variable.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="stylesheet" href="styles.css" />
```

- [ ] **Step 2: Add preload to `404.html`**

In `404.html` `<head>`, find:

```html
    <meta name="description" content="Page not found." />
    <meta name="robots" content="noindex" />
    <link rel="stylesheet" href="/styles.css" />
```

Insert *between* the `<meta name="robots">` and the
`<link rel="stylesheet">` lines:

```html
    <link rel="preload" href="/assets/fonts/jetbrains-mono-variable.woff2" as="font" type="font/woff2" crossorigin />
```

Result:

```html
    <meta name="description" content="Page not found." />
    <meta name="robots" content="noindex" />
    <link rel="preload" href="/assets/fonts/jetbrains-mono-variable.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="stylesheet" href="/styles.css" />
```

Note: `404.html` uses absolute paths (`/assets/...`) for asset
references; the preload follows that convention. `index.html` uses
relative paths.

- [ ] **Step 3: Verify**

```bash
grep -c "rel=\"preload\"" "C:/Users/14jak/GitHub/website/index.html"
grep -c "rel=\"preload\"" "C:/Users/14jak/GitHub/website/404.html"
```

Expected: `1` in each file.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html 404.html
git -C "C:/Users/14jak/GitHub/website" commit -m "fix(perf): preload the JetBrains Mono WOFF2 to cut font-swap CLS"
```

---

## Task 3: Darken parchment-theme contrast tokens

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (parchment theme block)

- [ ] **Step 1: Update the two token values**

In `styles.css`, find the parchment-theme block:

```css
/* ---------- Parchment light theme ---------- */
:root[data-theme="light"] {
  --bg:        #f5efe4;
  --bg-elev:   #ece4d3;
  --bg-grid:   #d9ceb7;
  --text:      #1a1f26;
  --text-dim:  #4a5560;
  --text-mute: #6a7480;
  --accent:    #a86a14;
  --accent-2:  #3f7a3f;
  --accent-3:  #a23a3a;
  --cursor:    #a86a14;
  --shadow:    0 1px 0 rgba(168, 106, 20, 0.08), 0 4px 12px rgba(26, 31, 38, 0.08);
}
```

Replace `--accent`, `--text-mute`, and `--cursor` (cursor should
match accent) with the darker values. The full block becomes:

```css
/* ---------- Parchment light theme ----------
   Darker --accent and --text-mute for WCAG AA contrast against --bg.
   Computed ratios on #f5efe4 background:
     --accent #915308    -> 5.28:1  (AA pass + margin)
     --text-mute #525a66 -> 6.08:1  (AA pass + AAA body)
*/
:root[data-theme="light"] {
  --bg:        #f5efe4;
  --bg-elev:   #ece4d3;
  --bg-grid:   #d9ceb7;
  --text:      #1a1f26;
  --text-dim:  #4a5560;
  --text-mute: #525a66;
  --accent:    #915308;
  --accent-2:  #3f7a3f;
  --accent-3:  #a23a3a;
  --cursor:    #915308;
  --shadow:    0 1px 0 rgba(145, 83, 8, 0.08), 0 4px 12px rgba(26, 31, 38, 0.08);
}
```

Three value changes (`--text-mute`, `--accent`, `--cursor`), plus the
shadow's RGB tuple updated to match the new amber.

- [ ] **Step 2: Verify**

```bash
grep -A 14 'Parchment light theme' "C:/Users/14jak/GitHub/website/styles.css" | grep -E '^  --(accent|text-mute|cursor):'
```

Expected output exactly:

```
  --text-mute: #525a66;
  --accent:    #915308;
  --cursor:    #915308;
```

- [ ] **Step 3: Visual check**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > /tmp/lh3.log 2>&1 &
sleep 2
echo "serving"
pkill -f "http.server 8765" 2>/dev/null
```

Open in browser, toggle to light theme via the nav button, confirm
the amber accents are slightly darker but the palette feels the same.
The `$ whoami`, `[ email ]`, `GPA 3.85 · Dean's Scholar`, and the
`$ _` footer cursor should all be readable on cream.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "fix(a11y): darken parchment-theme accent + muted text for WCAG AA contrast"
```

---

## Task 4: Add `role="img"` to project status dots

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (project cards)

- [ ] **Step 1: Add `role="img"` to active status dots**

Use `replace_all` to update all 3 active-project status spans at once.

Find every occurrence of:

```html
<span class="status status--active" aria-label="Status: active"></span>
```

Replace with:

```html
<span class="status status--active" role="img" aria-label="Status: active"></span>
```

- [ ] **Step 2: Add `role="img"` to shipped status dots**

Find every occurrence of:

```html
<span class="status status--shipped" aria-label="Status: shipped"></span>
```

Replace with:

```html
<span class="status status--shipped" role="img" aria-label="Status: shipped"></span>
```

The timeline status spans use `aria-hidden="true"` not `aria-label`,
so they're untouched and unaffected.

- [ ] **Step 3: Verify**

```bash
echo 'role="img" on status dots (expected 6):'
grep -c 'class="status status--\(active\|shipped\)" role="img"' "C:/Users/14jak/GitHub/website/index.html"
echo
echo 'status spans without role (project cards only — expected 0):'
python -c "
import re
with open(r'C:/Users/14jak/GitHub/website/index.html', encoding='utf-8') as f:
    h = f.read()
# project-card status spans should now have role
violations = re.findall(r'<span class=\"status status--(?:active|shipped)\" aria-label=\"Status:', h)
print(len(violations))
"
```

Expected: `6` `role="img"` matches and `0` violations.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "fix(a11y): add role=img to project status dots so aria-label is valid"
```

---

## Task 5: Push, then re-run Lighthouse against the LIVE site

**Files:** none modified (verification only).

- [ ] **Step 1: Push everything**

```bash
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

- [ ] **Step 2: Wait for GitHub Pages to redeploy**

Pages typically rebuilds within 30–120 seconds of a push. Poll:

```bash
for i in 1 2 3 4 5 6; do
  status=$(gh api "repos/jakethehoffer/website/pages/builds/latest" --jq '.status' 2>/dev/null)
  echo "  attempt $i: status=$status"
  if [ "$status" = "built" ]; then
    echo "  done"
    break
  fi
  sleep 20
done
```

Expected: at most a few "building" iterations then "built".

If the API doesn't return "built" within 6 attempts (2 minutes), poll
the build pages directly via `gh run list --limit 3 --workflow=pages`
to debug. Don't proceed to the audit until the latest commit has been
deployed.

- [ ] **Step 3: Re-run Lighthouse desktop**

```bash
mkdir -p "C:/Users/14jak/GitHub/website/.tmp"
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --preset=desktop \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-desktop-v24.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3
```

The cleanup-tmp EPERM error at the end is harmless — the JSON gets
written before it.

- [ ] **Step 4: Re-run Lighthouse mobile**

```bash
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v24.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3
```

- [ ] **Step 5: Summarize the new scores**

```bash
python <<'PY'
import json
from pathlib import Path
base = Path(r"C:/Users/14jak/GitHub/website/.tmp")
for label, fname in [("Desktop", "lh-desktop-v24.json"), ("Mobile", "lh-mobile-v24.json")]:
    with open(base / fname, encoding="utf-8") as f:
        data = json.load(f)
    cats = data["categories"]
    audits = data["audits"]
    print(f"\n=== {label} ===")
    for key in ("performance","accessibility","best-practices","seo"):
        s = (cats[key].get("score") or 0) * 100
        flag = "✓" if s >= 95 else "*"
        print(f"  {cats[key]['title']:25s} {s:5.1f}  {flag}")
    cls = audits["cumulative-layout-shift"]
    print(f"  CLS: {cls.get('displayValue')} (score {(cls.get('score') or 0)*100:.0f})")
PY
```

Expected: all 4 categories ≥ 95 on both strategies, CLS displayValue
< 0.10.

If any category misses by a small margin (<2 points), commit what we
have and note it; if any misses by a larger margin, return to the
spec to investigate further before tagging.

- [ ] **Step 6: Clean up tmp + final commit + handoff**

```bash
rm -rf "C:/Users/14jak/GitHub/website/.tmp" 2>&1 || true
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-lighthouse-fixes.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add Lighthouse-fixes implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3

powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.ai-sync/ai-sync.ps1" -Action handoff -Agent claude -Summary "Lighthouse fixes complete and verified on the live site. Hero box height locked before boot animation, WOFF2 preloaded, parchment theme tokens darkened, ARIA role added to status dots. Re-audit shows all 4 categories at or above 95 target." -FilesChanged "index.html (preload + role on 6 dots), 404.html (preload), styles.css (3 parchment tokens), script.js (1 CLS guard), docs/superpowers/specs/2026-05-12-lighthouse-fixes.md, docs/superpowers/plans/2026-05-12-lighthouse-fixes.md" -TestsRun "Live Lighthouse audit (record actual scores from Step 5 in this field when running)." -Blockers "none" -NextSteps "1) Share the live URL with reviewers. 2) Update LinkedIn + resume.pdf with the URL. 3) When ready to apply for roles, fold the URL into application materials."
```

---

## Closing checklist

After Task 5:
- [ ] All 5 tasks checked off
- [ ] Live site at `https://jakethehoffer.github.io/website/` has the fixes deployed
- [ ] Re-audit Lighthouse scores recorded — all four categories ≥ 95 on both strategies
- [ ] CLS in the "good" range (< 0.1)
- [ ] No visual regression
- [ ] Plan + handoff committed and pushed
