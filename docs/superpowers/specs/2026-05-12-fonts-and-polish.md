# Self-Host Fonts + Tiny Polish — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

Two small, complementary polish moves bundled into one cycle:

1. **Self-host JetBrains Mono.** The site currently loads its only
   font from Google Fonts, which means every visit makes 2 third-party
   DNS lookups, 2 TLS handshakes, fetches the CSS, parses it, then
   fetches the WOFF2 — a chained dependency that hurts FCP and LCP and
   leaks visitor IPs to Google. Bringing the font in-house eliminates
   the third-party trip entirely.
2. **GitHub Pages plumbing.** A static site without a 404 page,
   `robots.txt`, or `sitemap.xml` looks unfinished the moment it goes
   public. None of these need to be elaborate; they need to exist.

## Non-Goals

- Web app manifest / installable PWA setup.
- Microsoft Edge tile config (`browserconfig.xml`).
- Subsetting the font further (Latin subset is already small enough).
- Multiple sitemap URLs (the site has one page).
- Locale-aware 404 / multi-language routing.
- Removing the existing OG image / favicon scaffolding (already done
  in v2.2).

## Concrete Changes

### Part A: self-hosted JetBrains Mono Variable

**Asset:**
`C:/Users/14jak/GitHub/website/assets/fonts/jetbrains-mono-variable.woff2`,
the Latin-subset variable-weight WOFF2 from fontsource, target size
≤ 35 KB.

**Fetch script:**
`C:/Users/14jak/GitHub/website/scripts/fetch-fonts.sh`, downloads the
single WOFF2 file from a known fontsource CDN URL. Committed for
reproducibility. The script is *idempotent* (running it again
replaces the file). The committed `.woff2` remains the source of truth
for the site; the script just makes future refreshes one command.

**Primary URL** (fontsource on jsdelivr, well-maintained):
`https://cdn.jsdelivr.net/fontsource/fonts/jetbrains-mono:vf@latest/latin-wght-normal.woff2`

If that URL doesn't resolve at execution time, fallback to npm-pkgd:
`https://cdn.jsdelivr.net/npm/@fontsource-variable/jetbrains-mono@latest/files/jetbrains-mono-latin-wght-normal.woff2`

**CSS — add this block at the top of `styles.css`** (before the existing `:root` block):

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

The double `src` provides a fallback `format()` hint for browsers that
don't recognize `woff2-variations` (rare in 2026, but harmless — the
fallback line just re-points at the same file).

**HTML — remove these three lines from `<head>` in `index.html`:**

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

That's the only HTML change. The existing CSS already targets
`"JetBrains Mono"` as the family name; the new `@font-face` makes
that name resolve locally.

### Part B: tiny polish

**1. `404.html`** at repo root, ~80 lines.

GitHub Pages auto-serves any `404.html` at the repo root for
unrecognized routes. Content stays on-brand:

```
$ cat /requested/path
> error: file not found (404)

> the page you tried to visit doesn't exist.

[ home ]   [ projects ]   [ contact ]
```

Same `<head>` boilerplate as `index.html` (theme preload, font
`@font-face` via styles.css, favicons, theme-color meta). Links use
absolute paths (`/`, `/#projects`, `/#contact`) so they work from any
404 route depth. No boot-sequence animation — 404 should resolve
instantly.

**2. `robots.txt`** at repo root.

```
User-agent: *
Allow: /

Sitemap: https://jakethehoffer.github.io/website/sitemap.xml
```

Allow all crawlers, point to sitemap. Standard for a personal portfolio.

**3. `sitemap.xml`** at repo root.

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

Single URL, properly formed, discoverable by Google / Bing crawlers
via the `robots.txt` reference.

## File Layout Delta

```
website/
├── 404.html                                NEW
├── robots.txt                              NEW
├── sitemap.xml                             NEW
├── assets/fonts/
│   └── jetbrains-mono-variable.woff2       NEW (~30 KB)
├── scripts/
│   └── fetch-fonts.sh                      NEW
├── index.html                              MODIFIED (remove 3 head lines)
├── styles.css                              MODIFIED (add @font-face)
└── docs/superpowers/specs/
    └── 2026-05-12-fonts-and-polish.md      THIS DOC
```

## Page Weight Impact

Live page (browser-fetched on first visit):

| | Before (v2.2) | After |
|---|---|---|
| HTML / CSS / JS | 45,693 B | 45,693 B (unchanged) |
| favicon.svg | 468 B | 468 B (unchanged) |
| Image assets (3) | 115,343 B | 115,343 B (unchanged) |
| **Font (Google Fonts WOFF2)** | ~30,000 B (third-party) | — |
| **Font (self-hosted WOFF2)** | — | ~30,000 B (in-repo) |
| **Total** | ~192 KB | ~192 KB |
| **Third-party requests** | 2 (preconnect + CSS + font) | 0 |
| **Budget** | < 200 KB | < 200 KB ✓ |

Net: same total weight, fewer requests, no third-party trip.

## Verification

- Open the page after removing the Google Fonts link; confirm the
  page still renders in JetBrains Mono (DevTools → Network: no
  fonts.googleapis.com or fonts.gstatic.com requests).
- Hard reload with cache disabled (DevTools → Network → "Disable
  cache"); confirm the local `.woff2` loads and the font swaps in.
- Open `/404.html` directly via the local server; confirm it renders
  on-brand and the home/projects/contact links navigate to the right
  anchors.
- `curl http://localhost:8000/robots.txt` returns the 4-line file.
- `curl http://localhost:8000/sitemap.xml` returns valid XML.
- Total live page weight stays under 200 KB.
- Lighthouse perf score doesn't regress (and theoretically improves
  by ~50ms FCP from skipping the Google Fonts round-trip).

## Risks

- **fontsource URL pattern.** The exact slug
  (`jetbrains-mono:vf@latest` vs `@fontsource-variable/jetbrains-mono`)
  is volatile across major fontsource releases. Mitigated by trying
  the primary URL and falling back; ultimately, the WOFF2 is committed
  to the repo so the site doesn't depend on the URL at runtime — only
  the fetch script does, and it's a one-time refresh tool.
- **`woff2-variations` `format()` value.** Officially in the CSS Fonts
  spec but not always recognized by older browsers. The duplicate
  `format("woff2")` line covers that.
- **404 page font.** The 404 page uses the same `styles.css` so the
  `@font-face` resolves the same way. If `styles.css` is somehow
  missing, the page falls back to the system mono stack (
  `ui-monospace, SFMono-Regular, Menlo, monospace`) — acceptable.
- **No GitHub Pages deployment yet.** `robots.txt` and `sitemap.xml`
  do nothing until the site is publicly served. Committed now so
  they're in place when Pages flips on.

## Out of Scope (YAGNI)

- Italic / variable-italic font axis (the site doesn't use italics).
- `unicode-range` subsetting beyond Latin (we just use the Latin
  subset already; further subsetting is overkill).
- Adding a manifest, MS tile config, or any other icon variant.
- Custom 404 page with site search, navigation tree, etc.
- Sitemap entries for fragment anchors (`/#projects` etc.) — search
  engines treat fragment URLs as the same page.

## Success Criteria

After deployment:
- Network panel on a fresh visit shows zero requests to `fonts.*.com`.
- Type renders identically to before (visual diff: none).
- Lighthouse perf ≥ 95 (matches or beats v2.2).
- Visiting `/does-not-exist` (or any 404 route on the deployed site)
  shows the styled 404 page.
- `robots.txt` and `sitemap.xml` are accessible at the standard URLs.
