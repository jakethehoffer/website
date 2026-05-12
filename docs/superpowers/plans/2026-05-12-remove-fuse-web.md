# Remove FUSE-Web from the Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove every public-facing reference to FUSE-Web from the site, with internally consistent copy and metrics.

**Architecture:** A series of narrow edits across `index.html`, `scripts/refresh-meta.mjs`, `scripts/render-og-image.py`, and `README.md`, plus deletion of one image asset and regeneration of the OG image. No CSS, no JS, no design changes.

**Tech Stack:** HTML/CSS edits via Edit; Python (Pillow) to regenerate OG image; final grep-based verification + Lighthouse spot-check.

**Spec:** `docs/superpowers/specs/2026-05-12-remove-fuse-web.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── index.html                            MODIFIED (card, metrics, copy, JSON-LD)
├── assets/projects/fuse-web.webp         DELETED
├── assets/og-image.png                   REGENERATED
├── scripts/refresh-meta.mjs              MODIFIED (drop FUSE-Web)
├── scripts/render-og-image.py            MODIFIED (drop "web platforms")
└── README.md                             MODIFIED (PAT-setup repo list)
```

---

## Verification Approach

After each task, narrow `grep` confirming the change. After all tasks,
final grep sweep proving zero references remain (case-insensitive) in
runtime files. Lighthouse spot-check on the live URL after deploy.

---

## Task 1: Remove the FUSE-Web project card

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (remove one `<article>`)

- [ ] **Step 1: Find the FUSE-Web `<article>` block**

```bash
grep -n 'FUSE-Web\|fuse-web' "C:/Users/14jak/GitHub/website/index.html"
```

Expected output: line numbers for the project card's status sentinel,
project name, body text mentioning FUSE-Web, the `<img>` referencing
`fuse-web.webp`, and the screenshot card itself.

- [ ] **Step 2: Delete the entire `<article>` block**

The FUSE-Web card is an `<article class="project">…</article>`
spanning the card from its `<header class="project__head">` through
its closing `</article>` tag. Remove the whole block, including the
preceding indentation. Result: the Mega TTT card now sits immediately
after the Odds Aggregator card in the markup.

Use Edit with `old_string` = the full `<article>` block (including a
trailing newline-and-indentation so adjacent cards stay tidy) and
`new_string` = empty.

- [ ] **Step 3: Verify card count**

```bash
grep -c '<article class="project">' "C:/Users/14jak/GitHub/website/index.html"
```

Expected: `5`.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: remove FUSE-Web project card"
```

---

## Task 2: Update hero metrics + boot sequence + About + skills + JSON-LD

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (multiple small edits in the head and body)

- [ ] **Step 1: Hero metrics strip**

Find:

```html
<span>4 production systems</span>
```

Replace with:

```html
<span>3 production systems</span>
```

- [ ] **Step 2: Boot sequence body line**

Find:

```html
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> <span data-boot-line>i build production-grade software &mdash; trading agents, arbitrage daemons, web platforms, and ml pipelines. paper-trading the s&amp;p 500 on real infrastructure; running a 24/7 odds daemon across ten bookmakers.</span></span>
```

Replace with:

```html
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> <span data-boot-line>i build production-grade software &mdash; trading agents, arbitrage daemons, and ML pipelines. paper-trading the s&amp;p 500 on real infrastructure; running a 24/7 odds daemon across ten bookmakers.</span></span>
```

The only change: `web platforms, and ml pipelines` → `and ML pipelines`.

- [ ] **Step 3: About section paragraph 1**

Find:

```html
<p>Computer engineering at Queen&rsquo;s. I&rsquo;m most at home building systems that run unattended &mdash; trading agents that paper-trade the S&amp;P 500, an arbitrage daemon ingesting ten bookmakers every minute, web platforms with their tests wired up before the first commit.</p>
```

Replace with:

```html
<p>Computer engineering at Queen&rsquo;s. I&rsquo;m most at home building systems that run unattended &mdash; trading agents that paper-trade the S&amp;P 500, an arbitrage daemon ingesting ten bookmakers every minute, and the automation glue that keeps both running unattended.</p>
```

- [ ] **Step 4: Skills tools & frameworks line**

Find:

```html
<p class="skill-group__items">git &middot; next.js &middot; supabase &middot; fastapi &middot; playwright &middot; unity &middot; sqlite &middot; alembic &middot; monday.com &middot; google apps script</p>
```

Replace with:

```html
<p class="skill-group__items">git &middot; next.js &middot; fastapi &middot; playwright &middot; unity &middot; sqlite &middot; alembic &middot; monday.com &middot; google apps script</p>
```

- [ ] **Step 5: JSON-LD `knowsAbout`**

Find:

```html
"knowsAbout": [
        "Python", "JavaScript", "C", "C++", "C#", "Java", "Dart", "SQL",
        "Next.js", "Supabase", "Unity", "Playwright", "FastAPI",
        "Machine learning", "Automation", "Trading systems"
      ],
```

Replace with:

```html
"knowsAbout": [
        "Python", "JavaScript", "C", "C++", "C#", "Java", "Dart", "SQL",
        "Next.js", "Unity", "Playwright", "FastAPI",
        "Machine learning", "Automation", "Trading systems"
      ],
```

- [ ] **Step 6: Verify**

```bash
echo "=== zero hits for FUSE / fuse / Supabase / Vitest / 'web platforms' in index.html ==="
for term in 'FUSE-Web' 'fuse-web' 'Supabase' 'Vitest' 'web platforms' '4 production'; do
  c=$(grep -c "$term" "C:/Users/14jak/GitHub/website/index.html")
  echo "  '$term': $c"
done
```

Expected: all zeros. (If `fuse-web` still appears, the `<img src>` line wasn't fully removed in Task 1; revisit.)

- [ ] **Step 7: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: drop FUSE-Web copy from hero, about, skills, json-ld"
```

---

## Task 3: Delete the FUSE-Web screenshot

**Files:**
- Delete: `C:/Users/14jak/GitHub/website/assets/projects/fuse-web.webp`

- [ ] **Step 1: Remove from working tree + git index**

```bash
git -C "C:/Users/14jak/GitHub/website" rm assets/projects/fuse-web.webp
ls "C:/Users/14jak/GitHub/website/assets/projects/"
```

Expected: `mega-ttt.webp` and `walking-jumping-cm.png` only.

- [ ] **Step 2: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: delete fuse-web.webp screenshot asset"
```

---

## Task 4: Update `scripts/refresh-meta.mjs`

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/scripts/refresh-meta.mjs`

- [ ] **Step 1: Trim the `REPOS` array**

Find:

```js
const REPOS = [
  { owner: "jakethehoffer", name: "trader",     key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage",  key: "arbitrage.last_commit" },
  // FUSE-Web is in a different org. Adjust the owner if you have access.
  { owner: "Shield-Restoration-Services", name: "FUSE-Web", key: "FUSE-Web.last_commit" },
];
```

Replace with:

```js
const REPOS = [
  { owner: "jakethehoffer", name: "trader",    key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage", key: "arbitrage.last_commit" },
];
```

- [ ] **Step 2: Verify**

```bash
grep -c 'FUSE' "C:/Users/14jak/GitHub/website/scripts/refresh-meta.mjs"
```

Expected: `0`.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/refresh-meta.mjs
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: drop FUSE-Web from refresh-meta REPOS"
```

---

## Task 5: Update + re-run `scripts/render-og-image.py`

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/scripts/render-og-image.py`
- Regenerate: `C:/Users/14jak/GitHub/website/assets/og-image.png`

- [ ] **Step 1: Update body_lines**

Find:

```python
    body_lines = [
        "> i build production-grade software — trading",
        "> agents, arbitrage daemons, web platforms,",
        "> and ml pipelines.",
    ]
```

Replace with:

```python
    body_lines = [
        "> i build production-grade software — trading",
        "> agents, arbitrage daemons, and ML",
        "> pipelines.",
    ]
```

- [ ] **Step 2: Update metrics line**

Find:

```python
    metrics = "//  4 production systems  ·  10 bookmakers  ·  dean's scholar"
```

Replace with:

```python
    metrics = "//  3 production systems  ·  10 bookmakers  ·  dean's scholar"
```

- [ ] **Step 3: Regenerate the OG image**

```bash
python "C:/Users/14jak/GitHub/website/scripts/render-og-image.py"
ls -la "C:/Users/14jak/GitHub/website/assets/og-image.png"
```

Expected output:
- `wrote .../og-image.png  (some bytes)`
- Followed by writes of favicon.ico and apple-touch-icon (unchanged content but the script renders them anyway — fine, they'll be byte-identical or near-identical).

- [ ] **Step 4: Eyeball the new OG image via Read tool**

Confirm the new OG image:
- Says "3 production systems" in the metrics strip
- Body lines end with "and ML pipelines."
- No "web platforms" string visible

- [ ] **Step 5: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/render-og-image.py assets/og-image.png favicon.ico apple-touch-icon.png
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: regenerate OG image without FUSE-Web copy"
```

---

## Task 6: Update README PAT-setup section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/README.md`

- [ ] **Step 1: Trim the PAT instructions**

Find:

```markdown
1. Create a **fine-grained PAT** at
   <https://github.com/settings/personal-access-tokens/new> with
   *Repository permissions &rarr; Metadata: Read* on `jakethehoffer/trader`,
   `jakethehoffer/arbitrage`, and `Shield-Restoration-Services/FUSE-Web`.
```

Replace with:

```markdown
1. Create a **fine-grained PAT** at
   <https://github.com/settings/personal-access-tokens/new> with
   *Repository permissions &rarr; Metadata: Read* on
   `jakethehoffer/trader` and `jakethehoffer/arbitrage`.
```

- [ ] **Step 2: Verify**

```bash
grep -c 'FUSE\|fuse' "C:/Users/14jak/GitHub/website/README.md"
```

Expected: `0`.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add README.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: drop FUSE-Web from README PAT-setup steps"
```

---

## Task 7: Final sweep + push + Lighthouse spot-check

**Files:** none modified (verification only).

- [ ] **Step 1: Final reference sweep across runtime files**

```bash
echo "=== reference sweep (expected 0 in each line) ==="
for f in index.html 404.html styles.css script.js README.md scripts/refresh-meta.mjs scripts/render-og-image.py; do
  c=$(grep -c -i -E 'fuse-web|fuse_web|supabase|vitest|web platforms|4 production' "C:/Users/14jak/GitHub/website/$f" 2>/dev/null || echo 0)
  echo "  $f: $c"
done
```

Expected: all zeros.

(Spec / plan files under `docs/superpowers/` are intentionally
preserved with their original FUSE-Web references — those are
historical design artifacts.)

- [ ] **Step 2: Push and wait for redeploy**

```bash
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
echo "polling for Pages redeploy..."
for i in 1 2 3 4 5 6; do
  sleep 25
  c=$(curl -s "https://jakethehoffer.github.io/website/" | grep -c "3 production systems")
  echo "  attempt $i: live has new metric: $c"
  if [ "$c" -ge 1 ]; then echo "  deployed"; break; fi
done
```

- [ ] **Step 3: Confirm FUSE-Web is gone from the live site**

```bash
curl -s "https://jakethehoffer.github.io/website/" | grep -c -i 'fuse-web\|supabase\|vitest\|web platforms\|4 production'
```

Expected: `0`.

- [ ] **Step 4: Lighthouse mobile spot-check**

```bash
mkdir -p "C:/Users/14jak/GitHub/website/.tmp"
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v27.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3

PYTHONIOENCODING=utf-8 python <<'PY'
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r"C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v27.json", encoding="utf-8") as f:
    data = json.load(f)
print("=== v2.7 mobile spot-check ===")
for k in ("performance","accessibility","best-practices","seo"):
    s = (data["categories"][k].get("score") or 0) * 100
    flag = "PASS" if s >= 95 else "FAIL"
    print(f"  {data['categories'][k]['title']:25s} {s:5.1f}  {flag}")
a = data["audits"]
print(f"  CLS: {a['cumulative-layout-shift']['displayValue']}")
print(f"  LCP: {a['largest-contentful-paint']['displayValue']}")
PY
```

Expected: 100/100/100/100, CLS 0, LCP comparable to v2.6 or faster
(weight is now lower).

- [ ] **Step 5: Cleanup + commit plan + handoff**

```bash
rm -rf "C:/Users/14jak/GitHub/website/.tmp" 2>&1 || true
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-remove-fuse-web.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add FUSE-Web removal implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3

powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.ai-sync/ai-sync.ps1" -Action handoff -Agent claude -Summary "Removed every public reference to FUSE-Web from the site per Jake's request (FUSE is a hidden project). Card deleted, screenshot deleted, hero metrics dropped to 3, About + boot + OG copy reworded, Supabase/Vitest removed from skills, JSON-LD knowsAbout trimmed, refresh-meta and OG renderer scripts updated, README PAT instructions trimmed." -FilesChanged "index.html (card, metrics, About, boot, skills, JSON-LD), assets/projects/fuse-web.webp (DELETED), assets/og-image.png (regenerated), scripts/refresh-meta.mjs (drop FUSE-Web), scripts/render-og-image.py (drop web platforms + 3 systems), README.md (PAT setup), docs/superpowers/specs/2026-05-12-remove-fuse-web.md, docs/superpowers/plans/2026-05-12-remove-fuse-web.md" -TestsRun "Final grep sweep: 0 hits for fuse-web/supabase/vitest/'web platforms'/'4 production' across runtime files. Mobile Lighthouse spot-check pending (record actual scores at run time)." -Blockers "PAT-driven refresh-meta workflow still returns 404 from GitHub API; may be a propagation lag or stray secret-value character. Will resolve itself or need a re-paste. Without it, weekly workflow no-ops harmlessly." -NextSteps "1) Watch the next scheduled refresh-meta run (Monday 12:00 UTC) — if it still 404s, re-set the secret in case the original paste had a stray char. 2) Custom domain still on the polish backlog. 3) Share the URL with reviewers."
```

---

## Closing checklist

- [ ] All 7 tasks checked off
- [ ] Live site has 5 project cards, "3 production systems" in the hero strip, no FUSE-Web / Supabase / Vitest / "web platforms" references anywhere
- [ ] OG image regenerated with new copy
- [ ] `refresh-meta.mjs` and `render-og-image.py` updated
- [ ] README PAT instructions trimmed
- [ ] Lighthouse v2.7 mobile spot-check 100/100/100/100
- [ ] Page weight dropped ~70 KB
- [ ] Everything pushed
- [ ] Handoff updated
