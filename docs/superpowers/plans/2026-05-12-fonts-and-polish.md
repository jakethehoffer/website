# Self-Host Fonts + Tiny Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Google Fonts dependency with a self-hosted JetBrains Mono Variable WOFF2, and add `404.html`, `robots.txt`, and `sitemap.xml` so the site is GitHub-Pages-ready.

**Architecture:** One WOFF2 asset + a shell fetch script + a CSS `@font-face` block + 3 small static files at the repo root + a 3-line removal from `index.html` head. No JS changes, no design-token changes, no breaking changes to existing assets.

**Tech Stack:** WOFF2 from fontsource via jsdelivr (curl). Hand-written 404 HTML reusing the v2 styles. Plain text + XML for robots / sitemap.

**Spec:** `docs/superpowers/specs/2026-05-12-fonts-and-polish.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── 404.html                                NEW (~80 lines)
├── robots.txt                              NEW (4 lines)
├── sitemap.xml                             NEW (~10 lines)
├── assets/fonts/
│   └── jetbrains-mono-variable.woff2       NEW (~30 KB)
├── scripts/
│   └── fetch-fonts.sh                      NEW (~25 lines)
├── index.html                              MODIFIED (remove 3 head lines)
└── styles.css                              MODIFIED (prepend @font-face)
```

Each task below produces a self-contained commit.

---

## Verification Approach

Static site, no test suite. Verifications are inline:
- After fetching the font: confirm file size, content, and that the file is a valid WOFF2.
- After CSS / HTML changes: serve locally, confirm `localhost:8000` has no `fonts.googleapis.com` or `fonts.gstatic.com` references in the served HTML.
- After 404 / robots / sitemap: `curl` each path and verify content.
- Final smoke: same all-assets-200 check plus a check that the served HTML does NOT contain any Google Fonts URLs.

---

## Task 1: Download the WOFF2 + commit the fetch script

**Files:**
- Create: `C:/Users/14jak/GitHub/website/scripts/fetch-fonts.sh`
- Create: `C:/Users/14jak/GitHub/website/assets/fonts/jetbrains-mono-variable.woff2`

- [ ] **Step 1: Write the fetch script**

```bash
#!/usr/bin/env bash
# fetch-fonts.sh — refresh the self-hosted JetBrains Mono Variable WOFF2.
#
# Idempotent. Run from anywhere; resolves output paths from this script's location.
#
# Usage:
#     bash scripts/fetch-fonts.sh
# Writes:
#     assets/fonts/jetbrains-mono-variable.woff2

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$HERE/../assets/fonts"
OUT_FILE="$OUT_DIR/jetbrains-mono-variable.woff2"

mkdir -p "$OUT_DIR"

PRIMARY="https://cdn.jsdelivr.net/fontsource/fonts/jetbrains-mono:vf@latest/latin-wght-normal.woff2"
FALLBACK="https://cdn.jsdelivr.net/npm/@fontsource-variable/jetbrains-mono@latest/files/jetbrains-mono-latin-wght-normal.woff2"

echo "fetching JetBrains Mono Variable (Latin subset) ..."
if ! curl -sSL --fail "$PRIMARY" -o "$OUT_FILE"; then
  echo "primary URL failed, trying fallback ..."
  curl -sSL --fail "$FALLBACK" -o "$OUT_FILE"
fi

SIZE=$(wc -c < "$OUT_FILE")
echo "wrote $OUT_FILE ($SIZE bytes)"

# Sanity check: WOFF2 files start with 'wOF2' (0x77 0x4F 0x46 0x32).
head -c 4 "$OUT_FILE" | grep -q '^wOF2' \
  || { echo "ERROR: $OUT_FILE is not a WOFF2 (magic mismatch)"; exit 1; }

echo "ok"
```

- [ ] **Step 2: Run the script**

```bash
bash "C:/Users/14jak/GitHub/website/scripts/fetch-fonts.sh"
```

Expected: prints "wrote ... (NNNN bytes)" with NNNN around 25–50 KB,
then "ok". If both URLs fail, stop and report the network error;
don't guess.

- [ ] **Step 3: Verify the file**

```bash
ls -la "C:/Users/14jak/GitHub/website/assets/fonts/jetbrains-mono-variable.woff2"
python -c "
with open(r'C:/Users/14jak/GitHub/website/assets/fonts/jetbrains-mono-variable.woff2', 'rb') as f:
    head = f.read(4)
print('Magic bytes:', head)
print('Is WOFF2:', head == b'wOF2')
"
```

Expected: file size 25,000–50,000 bytes; magic bytes `b'wOF2'`; `Is WOFF2: True`.

- [ ] **Step 4: Commit script + font asset together**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/fetch-fonts.sh assets/fonts/jetbrains-mono-variable.woff2
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: self-host JetBrains Mono Variable WOFF2 (Latin subset)"
```

---

## Task 2: Add `@font-face` to `styles.css`

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/styles.css` (prepend `@font-face`)

- [ ] **Step 1: Prepend the `@font-face` block**

`styles.css` currently begins with:

```css
/* ============================================================
   Engineering Log — v2 design system
   ============================================================ */

/* ---------- Dark theme (default) ---------- */
:root {
```

Prepend (before the existing top comment) so that the very first rule in the file is the `@font-face`:

```css
@font-face {
  font-family: "JetBrains Mono";
  src: url("assets/fonts/jetbrains-mono-variable.woff2") format("woff2-variations"),
       url("assets/fonts/jetbrains-mono-variable.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

```

The result should look like:

```css
@font-face {
  font-family: "JetBrains Mono";
  src: url("assets/fonts/jetbrains-mono-variable.woff2") format("woff2-variations"),
       url("assets/fonts/jetbrains-mono-variable.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

/* ============================================================
   Engineering Log — v2 design system
   ============================================================ */
…
```

- [ ] **Step 2: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add styles.css
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: declare local @font-face for JetBrains Mono Variable"
```

---

## Task 3: Drop the Google Fonts links from `index.html`

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (remove 3 head lines)

- [ ] **Step 1: Remove the preconnect + Google Fonts CSS link**

Find this exact block in `index.html` `<head>` (currently around lines 18–20):

```html
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

Replace with empty (just delete those three lines). The surrounding
context — the meta description above and the local stylesheet link
below — stays intact:

```html
    <meta name="description" content="Jake Hoffman — 3rd-year Computer Engineering student at Queen's University. Builds production-grade software in Python, JavaScript, C/C++, Java, and Dart." />
    <link rel="stylesheet" href="styles.css" />
```

- [ ] **Step 2: Verify the change**

```bash
grep -c 'fonts.googleapis\|fonts.gstatic' "C:/Users/14jak/GitHub/website/index.html"
```

Expected: `0` (no Google Fonts references left).

- [ ] **Step 3: Smoke-check the site locally**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > "$TEMP/jh-http5.log" 2>&1 &
sleep 2
echo "=== Confirm no Google Fonts in served HTML ==="
curl -s http://localhost:8765/ | grep -c 'fonts.googleapis\|fonts.gstatic'
echo "(expected: 0)"
echo ""
echo "=== Confirm font file is served ==="
curl -s -o /dev/null -w "%{http_code} (%{size_download} bytes)\n" "http://localhost:8765/assets/fonts/jetbrains-mono-variable.woff2"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Expected: `0` Google-Fonts references; the WOFF2 path serves 200
with the same size as the file on disk.

Open <http://localhost:8765/> in a browser (or after stopping the
local server, double-click `index.html`). Confirm JetBrains Mono
still renders. In DevTools → Network, no `fonts.googleapis.com` or
`fonts.gstatic.com` requests appear.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: drop Google Fonts links, font now served locally"
```

---

## Task 4: Add `404.html`

**Files:**
- Create: `C:/Users/14jak/GitHub/website/404.html`

- [ ] **Step 1: Write the 404 page**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>404 — Jake Hoffman</title>
    <script>
      (function () {
        try {
          var stored = localStorage.getItem("jh-theme");
          var prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
          var theme = stored || (prefersLight ? "light" : "dark");
          document.documentElement.setAttribute("data-theme", theme);
        } catch (e) {}
      })();
    </script>
    <meta name="description" content="Page not found." />
    <meta name="robots" content="noindex" />
    <link rel="stylesheet" href="/styles.css" />
    <meta name="theme-color" content="#0a0e14" media="(prefers-color-scheme: dark)" />
    <meta name="theme-color" content="#f5efe4" media="(prefers-color-scheme: light)" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="icon" type="image/x-icon" href="/favicon.ico" sizes="32x32" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180" />
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>

    <header class="site-header">
      <nav class="site-nav" aria-label="Primary">
        <a class="nav-brand" href="/"><span class="nav-brand__prompt">$</span> jake_hoffman</a>
      </nav>
    </header>

    <main id="main">
      <section class="hero">
        <div class="container hero__inner">
          <pre class="hero__boot" aria-label="404 error">
<span class="boot__prompt">$ cat /requested/path</span>
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> error: file not found (404)</span>

<span class="boot__prompt">$ ls /jake_hoffman</span>
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> the page you tried to visit doesn&rsquo;t exist.</span>
<span class="boot__line"><span class="boot__caret-mark">&gt;</span> try one of:<span class="boot__caret" aria-hidden="true">_</span></span>
          </pre>

          <div class="hero__ctas" role="group" aria-label="Recovery links">
            <a class="btn btn--primary" href="/">[ home ]</a>
            <a class="btn" href="/#projects">[ projects ]</a>
            <a class="btn" href="/#contact">[ contact ]</a>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container site-footer__inner">
        <p class="site-footer__prompt">$ <span class="boot__caret" aria-hidden="true">_</span></p>
        <p class="site-footer__meta"><span>&copy; <span id="footer-year">2026</span> jake hoffman</span></p>
      </div>
    </footer>

    <script>
      // Stamp the current year and apply the existing theme.
      var y = document.getElementById("footer-year");
      if (y) y.textContent = String(new Date().getFullYear());
    </script>
  </body>
</html>
```

Notes:
- All resource paths are absolute (`/styles.css`, `/favicon.svg`, etc.) so the page works regardless of the 404 route depth.
- Reuses the existing `.hero`, `.btn`, `.site-header`, `.site-footer`, `.boot__*` classes from `styles.css` — no new CSS needed.
- `<meta name="robots" content="noindex">` so crawlers don't accidentally index 404 routes.
- The boot caret blinks (CSS) for visual continuity with the home page.
- Theme preload mirrors `index.html`'s logic so the page paints in the correct theme on first frame.

- [ ] **Step 2: Verify locally**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > "$TEMP/jh-http6.log" 2>&1 &
sleep 2
echo "=== /404.html response ==="
curl -s -o /dev/null -w "%{http_code} (%{size_download} bytes)\n" "http://localhost:8765/404.html"
echo ""
echo "=== Recovery links present ==="
curl -s http://localhost:8765/404.html | grep -c -E 'href="/(#projects|#contact|)"'
echo "(expected: 3)"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Open `http://localhost:8765/404.html` in a browser. Confirm:
- The amber `$ cat /requested/path` prompt and `> error: ...` body
- Three `[ home ] / [ projects ] / [ contact ]` recovery buttons
- The theme matches your home-page theme (toggle persists from localStorage)
- The footer shows the current year and a blinking `$ _`

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add 404.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add 404.html on-brand with recovery links"
```

---

## Task 5: Add `robots.txt` + `sitemap.xml`

**Files:**
- Create: `C:/Users/14jak/GitHub/website/robots.txt`
- Create: `C:/Users/14jak/GitHub/website/sitemap.xml`

- [ ] **Step 1: Write `robots.txt`**

```
User-agent: *
Allow: /

Sitemap: https://jakethehoffer.github.io/website/sitemap.xml
```

- [ ] **Step 2: Write `sitemap.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://jakethehoffer.github.io/website/</loc>
    <lastmod>2026-05-12</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

- [ ] **Step 3: Verify both files**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > "$TEMP/jh-http7.log" 2>&1 &
sleep 2
echo "=== robots.txt ==="
curl -s http://localhost:8765/robots.txt
echo "---"
echo "=== sitemap.xml ==="
curl -s http://localhost:8765/sitemap.xml
echo "---"
echo "=== XML sanity ==="
python -c "import xml.etree.ElementTree as ET; ET.parse(r'C:/Users/14jak/GitHub/website/sitemap.xml'); print('sitemap parses ok')"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Expected: both files served with their literal content; the Python
parse prints "sitemap parses ok" with no exception.

- [ ] **Step 4: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add robots.txt sitemap.xml
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add robots.txt and sitemap.xml for GitHub Pages"
```

---

## Task 6: Final smoke, push, handoff

**Files:** none modified; verification only.

- [ ] **Step 1: Full asset smoke**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > "$TEMP/jh-http8.log" 2>&1 &
sleep 2
echo "=== Asset responses ==="
for path in "" styles.css script.js favicon.svg favicon.ico apple-touch-icon.png assets/og-image.png assets/fonts/jetbrains-mono-variable.woff2 assets/projects/mega-ttt.webp assets/projects/walking-jumping-cm.png assets/projects/[removed].webp robots.txt sitemap.xml 404.html resume.pdf; do
  curl -s -o /dev/null -w "$path: %{http_code} (%{size_download} bytes)\n" "http://localhost:8765/$path"
done
echo ""
echo "=== No Google Fonts in served HTML ==="
echo "index.html:  $(curl -s http://localhost:8765/ | grep -c 'fonts.googleapis\|fonts.gstatic')   (expected 0)"
echo "404.html:    $(curl -s http://localhost:8765/404.html | grep -c 'fonts.googleapis\|fonts.gstatic')   (expected 0)"
echo ""
echo "=== Live page weight check ==="
python -c "
import os
live = [
    r'C:/Users/14jak/GitHub/website/index.html',
    r'C:/Users/14jak/GitHub/website/styles.css',
    r'C:/Users/14jak/GitHub/website/script.js',
    r'C:/Users/14jak/GitHub/website/favicon.svg',
    r'C:/Users/14jak/GitHub/website/assets/fonts/jetbrains-mono-variable.woff2',
    r'C:/Users/14jak/GitHub/website/assets/projects/[removed].webp',
    r'C:/Users/14jak/GitHub/website/assets/projects/mega-ttt.webp',
    r'C:/Users/14jak/GitHub/website/assets/projects/walking-jumping-cm.png',
]
total = sum(os.path.getsize(p) for p in live)
print(f'  Live (page-fetched):    {total:>7,} bytes  (target < 200000)')
"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Expected:
- All 15 paths return 200
- Both pages have 0 Google Fonts references
- Live page weight under 200 KB

- [ ] **Step 2: Commit + push the plan**

```bash
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-fonts-and-polish.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add fonts + tiny polish implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

- [ ] **Step 3: Update the .ai-sync handoff**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "Self-hosted JetBrains Mono Variable (Latin subset WOFF2) replaces the Google Fonts CDN dependency. Added 404.html, robots.txt, and sitemap.xml for the eventual GitHub Pages deploy. Net-zero page weight (same font weight, same total bytes), zero third-party requests on first paint." -FilesChanged "404.html (NEW), robots.txt (NEW), sitemap.xml (NEW), assets/fonts/jetbrains-mono-variable.woff2 (NEW), scripts/fetch-fonts.sh (NEW), index.html (3 head lines removed), styles.css (@font-face prepended), docs/superpowers/specs/2026-05-12-fonts-and-polish.md, docs/superpowers/plans/2026-05-12-fonts-and-polish.md" -TestsRun "Smoke: all 15 asset paths 200, 0 Google Fonts refs in served index.html or 404.html, live page weight under 200KB, sitemap.xml parses as valid XML." -Blockers "robots.txt + sitemap.xml only become meaningful once GitHub Pages is enabled; 404.html only auto-serves on GitHub Pages, not file://." -NextSteps "1) Make repo public + enable GitHub Pages. 2) Verify Lighthouse perf score didn't regress. 3) Optional: Subset the font further (already Latin-only; further trim of glyphs not in the page is possible but ROI is low)."
```

- [ ] **Step 4: Final state check**

```bash
git -C "C:/Users/14jak/GitHub/website" log --oneline | head -12
git -C "C:/Users/14jak/GitHub/website" status
```

Expected: clean working tree, recent commits show the polish work,
`origin/main` in sync.

---

## Closing checklist

After Task 6:
- [ ] All 6 tasks checked off above
- [ ] `assets/fonts/jetbrains-mono-variable.woff2` exists; `scripts/fetch-fonts.sh` reproduces it
- [ ] `styles.css` opens with the `@font-face` block
- [ ] `index.html` has no `fonts.googleapis.com` or `fonts.gstatic.com` references
- [ ] `404.html`, `robots.txt`, `sitemap.xml` exist at repo root
- [ ] Smoke tests pass; live page weight under 200 KB
- [ ] All work pushed to `origin/main`
- [ ] .ai-sync handoff updated
