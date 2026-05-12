# Odds Aggregator Case Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Insert a second case-study section into `index.html` covering Odds Aggregator, mirroring the existing `trader` case study structure.

**Architecture:** Single HTML insertion. No JS, no CSS, no new assets. Reuses every existing class.

**Tech Stack:** Plain HTML edit + structural smoke check + Lighthouse regression check.

**Spec:** `docs/superpowers/specs/2026-05-12-odds-aggregator-case-study.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
└── index.html                            MODIFIED (one new section)
```

---

## Verification Approach

Static site, no test suite. Verification = three things:
1. The new section renders correctly in a browser
2. Page weight stays under 200 KB
3. Lighthouse post-deploy doesn't regress from v2.4's 100/100/100/100

---

## Task 1: Insert the new case-study section

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (insert one section)

- [ ] **Step 1: Insert the new section markup**

In `index.html`, find the closing `</section>` of the existing
`<section id="case-study">` (the trader case study). Immediately
after it, before `<section id="experience">`, insert this block:

```html
      <section id="case-study-arb" class="section">
        <div class="container">
          <p class="section__label"># case study</p>
          <h2>odds aggregator &mdash; a 24/7 cross-book arbitrage daemon</h2>
          <p class="case-study__lede">
            Ten bookmakers, six sports, polled every minute. When prices on
            the same outcome diverge enough to clear the vig and transaction
            friction, an alert fires to Telegram and Discord within seconds of
            the gap opening. Runs unattended on a Windows host with
            replay-tooling for postmortems.
          </p>

          <pre class="diagram" aria-label="odds aggregator architecture: ingest, normalize, detect, alert, journal">
   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;
   &#9474;  scraper pool   &#9474;&#9472;&#9472;&#9658;&#9474;   normalize     &#9474;&#9472;&#9472;&#9658;&#9474;  arb detector   &#9474;
   &#9474;  (10 books)     &#9474;   &#9474;  (canonical     &#9474;   &#9474;  (cross-book,  &#9474;
   &#9474;                 &#9474;   &#9474;   markets)       &#9474;   &#9474;   per-event)    &#9474;
   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9516;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9516;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;
            &#9474;                                          &#9474;
            &#9660;                                          &#9660;
   &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;                          &#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;
   &#9474;  SQLite +       &#9474;&#9668;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9474; alert pipeline  &#9474;
   &#9474;  Alembic        &#9474;                          &#9474; (Telegram /     &#9474;
   &#9474;  (journal)      &#9474;                          &#9474;  Discord)       &#9474;
   &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;                          &#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;
          </pre>

          <div class="case-study__prose">
            <h3>The problem</h3>
            <p>A real-time cross-book ingester sounds simple and isn&rsquo;t. Each book formats markets differently, prices go stale within seconds, and books vary wildly in scrape-friendliness &mdash; <code>FanDuel</code> removed itself with bot detection; <code>Pinnacle</code> requires auth. An arb that&rsquo;s real on paper is often gone by the time you see it; an arb that looks &ldquo;available&rdquo; is often a stale price. The hard part isn&rsquo;t math, it&rsquo;s <em>fresh</em> math.</p>

            <h3>The system</h3>
            <p>Per-book ingest workers feed a normalization layer that canonicalizes markets (so <code>Moneyline</code> on BetMGM resolves to the same key as <code>h2h</code> on Pinnacle). The arb detector walks canonical odds for each event, converts to implied probabilities, and flags any cross-book combination where &Sigma; implied &lt; 1 minus a configurable edge floor. SQLite with Alembic handles schema evolution &mdash; over ten migrations so far. A separate journal table records every raw scrape, which means failures and false-positives are replayable against the exact inputs that produced them.</p>

            <h3>What I learned / what&rsquo;s next</h3>
            <p>Production scrapers fail in interesting ways. The most underestimated work was <em>defensive ingestion</em> &mdash; per-book health scoring, automatic backoff on bot-detection, intermittent-cluster tolerance. The math layer was small; the operations layer was most of it. Next step: a paper-trading recorder that attributes realized P&amp;L to historical alerts without actually placing bets, so the alert pipeline can be calibrated against real outcomes.</p>
          </div>
        </div>
      </section>
```

Notes:
- The `id="case-study-arb"` differentiates it from the existing
  `id="case-study"`. The nav doesn't link to either anchor by id
  directly (the menu uses `#case-study` for the first one); the
  second is reachable by scrolling.
- The box-drawing entities (`&#9484;`, `&#9472;`, etc.) are the same
  encoding used in the trader diagram and render correctly under the
  `.diagram` CSS class.
- Uses `<em>` for emphasis and `<code>` for project / market names,
  same conventions as the trader case study's prose. The
  `.case-study__prose code` rule already handles the inline-code
  styling.

- [ ] **Step 2: Structural verification**

```bash
echo "=== sections matching id=case-study* ==="
grep -c 'section id="case-study' "C:/Users/14jak/GitHub/website/index.html"
echo "(expected: 2)"
echo
echo "=== .diagram blocks ==="
grep -c 'class="diagram"' "C:/Users/14jak/GitHub/website/index.html"
echo "(expected: 2 — one per case study)"
echo
echo "=== .case-study__prose blocks ==="
grep -c 'class="case-study__prose"' "C:/Users/14jak/GitHub/website/index.html"
echo "(expected: 2)"
echo
echo "=== order: trader before odds aggregator before experience ==="
python -c "
with open(r'C:/Users/14jak/GitHub/website/index.html', encoding='utf-8') as f:
    h = f.read()
i_trader = h.find('id=\"case-study\"')
i_arb = h.find('id=\"case-study-arb\"')
i_exp = h.find('id=\"experience\"')
print('  trader pos:', i_trader)
print('  arb pos:   ', i_arb)
print('  exp pos:   ', i_exp)
print('  ordered correctly:', i_trader < i_arb < i_exp)
"
```

Expected: `2`, `2`, `2`, and `ordered correctly: True`.

- [ ] **Step 3: Local serve + visual sanity check**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > /tmp/odds-cs.log 2>&1 &
sleep 2
echo "=== index.html responds 200 ==="
curl -s -o /dev/null -w "%{http_code} (%{size_download} bytes)\n" http://localhost:8765/
echo
echo "=== odds-aggregator case study reachable via anchor ==="
curl -s http://localhost:8765/ | grep -c 'case-study-arb'
echo "(expected: 1)"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Open `http://localhost:8765/#case-study-arb` in a browser. Confirm:
- Section heading reads "odds aggregator — a 24/7 cross-book arbitrage daemon"
- ASCII diagram aligns cleanly in dark mode
- Three subsection headings render with the same uppercase letter-
  spacing as the trader case study's
- Inline `<code>` styling (amber on near-black bg) applies to
  `FanDuel`, `Pinnacle`, `Moneyline`, `h2h`
- Toggle to parchment theme; diagram and code styling still readable

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add odds aggregator case study with ascii diagram"
```

---

## Task 2: Push + verify live + re-audit

**Files:** none modified; verification only.

- [ ] **Step 1: Push to origin and wait for Pages redeploy**

```bash
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
echo "polling for redeploy..."
for i in 1 2 3 4 5 6; do
  sleep 25
  has=$(curl -s "https://jakethehoffer.github.io/website/" | grep -c 'case-study-arb')
  echo "  attempt $i: live has new section: $has"
  if [ "$has" -ge 1 ]; then echo "  deployed"; break; fi
done
```

- [ ] **Step 2: Re-run Lighthouse on the live URL (both strategies)**

```bash
mkdir -p "C:/Users/14jak/GitHub/website/.tmp"
echo "=== Lighthouse desktop ==="
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --preset=desktop \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-desktop-v25.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3

echo ""
echo "=== Lighthouse mobile ==="
npx --yes lighthouse@latest "https://jakethehoffer.github.io/website/" \
  --output=json \
  --output-path="C:/Users/14jak/GitHub/website/.tmp/lh-mobile-v25.json" \
  --chrome-flags="--headless=new --no-sandbox" \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo 2>&1 | tail -3
```

- [ ] **Step 3: Summarize**

```bash
PYTHONIOENCODING=utf-8 python <<'PY'
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
base = Path(r"C:/Users/14jak/GitHub/website/.tmp")
print("=== v2.5 audit ===")
for label, fname in [("Desktop", "lh-desktop-v25.json"), ("Mobile", "lh-mobile-v25.json")]:
    with open(base / fname, encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n  {label}")
    for k in ("performance","accessibility","best-practices","seo"):
        s = (data["categories"][k].get("score") or 0) * 100
        flag = "PASS" if s >= 95 else "FAIL"
        print(f"    {data['categories'][k]['title']:25s} {s:5.1f}  {flag}")
    a = data["audits"]
    print(f"    CLS: {a['cumulative-layout-shift']['displayValue']}")
    print(f"    LCP: {a['largest-contentful-paint']['displayValue']}")
PY
```

Expected: every category at 100, no regression from v2.4.

If anything regresses (e.g., a category drops to < 95), investigate
before tagging. The likely cause would be a malformed HTML insertion
breaking page structure.

- [ ] **Step 4: Clean up + commit the plan + handoff**

```bash
rm -rf "C:/Users/14jak/GitHub/website/.tmp" 2>&1 || true
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-odds-aggregator-case-study.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add odds aggregator case-study implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3

powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME/.ai-sync/ai-sync.ps1" -Action handoff -Agent claude -Summary "Added a second case study on Odds Aggregator, structurally mirroring the existing trader case study. ~300 words across three subsections plus an ASCII data-flow diagram (scraper pool, normalize, arb detector, alert pipeline, journal). All technical claims fact-checked against the arbitrage repo." -FilesChanged "index.html (one new <section>), docs/superpowers/specs/2026-05-12-odds-aggregator-case-study.md, docs/superpowers/plans/2026-05-12-odds-aggregator-case-study.md" -TestsRun "Live Lighthouse re-audit on https://jakethehoffer.github.io/website/. (Record actual scores in this field at run time.)" -Blockers "none" -NextSteps "1) Get real feedback by sharing the URL with reviewers. 2) Consider a custom domain (jakehoffman.dev or similar) as the next branding lift. 3) Refresh refresh-meta.mjs occasionally to keep last_commit fresh."
```

---

## Closing checklist

- [ ] All 2 tasks checked off
- [ ] index.html now has two case-study sections in order (trader → odds aggregator → experience)
- [ ] Lighthouse v2.5 audit shows no regression (100/100/100/100 on both strategies)
- [ ] Everything pushed to `origin/main`
