# Share-Card Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a custom 1200×630 OG image, an SVG favicon with ICO fallback, an Apple touch icon, and the full set of OG / Twitter / theme-color / icon-link `<meta>` tags so the site shows a polished preview anywhere the URL is shared.

**Architecture:** One hand-written `favicon.svg`. One Python script (`scripts/render-og-image.py`) that produces three raster assets via PIL: `assets/og-image.png` (1200×630), `favicon.ico` (32×32), `apple-touch-icon.png` (180×180). One block of `<head>` edits to wire everything up. No new dependencies — Pillow is already installed locally.

**Tech Stack:** Pillow (PIL) for raster rendering, hand-written SVG, raw HTML head edits. No JS, no CSS changes. Live page weight stays at 160 KB (icons + OG image are fetched only by scrapers and OS icon handlers, never by the page itself).

**Spec:** `docs/superpowers/specs/2026-05-12-share-card-polish.md`

**Working directory:** `C:/Users/14jak/GitHub/website/`

---

## File Structure

```
website/
├── favicon.svg                            NEW (hand-written, ~600 bytes)
├── favicon.ico                            NEW (generated, ~3 KB)
├── apple-touch-icon.png                   NEW (generated, ~5 KB)
├── assets/og-image.png                    NEW (generated, ~60 KB)
├── scripts/
│   └── render-og-image.py                 NEW (~150 lines, handles all 3 rasters)
├── index.html                             MODIFIED (head only — +10 tags)
└── docs/superpowers/plans/
    └── 2026-05-12-share-card-polish.md    THIS DOC
```

Responsibilities:
- `favicon.svg` is the source of truth for the brand glyph. SVG is shipped to browsers directly.
- `scripts/render-og-image.py` produces the three raster assets in one run. Idempotent (running again replaces them). Committed for reproducibility.
- `index.html` head changes are scoped — they don't touch the body, the JSON-LD, the inline theme-preload script, or anything outside `<head>`.

---

## Verification Approach

This work is mostly file-generation + markup, not interactive logic. Each task that produces a file ends with a visual or structural check:
- Image assets get viewed in the chat (via the `Read` tool, which renders images visually) to confirm typography, alignment, and color.
- The HTML head edit gets checked structurally (count of expected tags via `grep`).
- A final smoke test serves the site and confirms no broken references.

No automated tests because the site has no test suite (consistent with v1/v2/v2.1 cycles).

---

## Task 1: Hand-write `favicon.svg`

**Files:**
- Create: `C:/Users/14jak/GitHub/website/favicon.svg`

- [ ] **Step 1: Write the SVG**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" aria-label="Jake Hoffman">
  <rect width="32" height="32" rx="6" fill="#0a0e14" />
  <rect x="1" y="1" width="30" height="30" rx="5" fill="none" stroke="#f5b342" stroke-width="1.5" stroke-opacity="0.35" />
  <text x="16" y="22" text-anchor="middle" font-family="JetBrains Mono, ui-monospace, Menlo, monospace" font-size="16" font-weight="700" fill="#f5b342" letter-spacing="-0.5">JH</text>
</svg>
```

This SVG renders an amber `JH` glyph on a near-black `#0a0e14` rounded
square, with a faint amber rim. It uses literal hex colors (not
`currentColor`) for the glyph so Chrome's tab favicon renders correctly
in both light and dark browser chrome — amber reads well against both.

- [ ] **Step 2: View the SVG in the chat to verify alignment**

Read the file. Confirm:
- The `JH` glyph is roughly centered (slight optical lift since `y=22` accounts for descender space)
- Amber-on-near-black contrast is strong
- The rim is visible but subtle

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add favicon.svg
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add SVG favicon (amber JH on near-black, v2 palette)"
```

---

## Task 2: Write the raster-render script

**Files:**
- Create: `C:/Users/14jak/GitHub/website/scripts/render-og-image.py`

- [ ] **Step 1: Write the script**

```python
"""Render the OG image, favicon.ico, and apple-touch-icon.png in one run.

Reads no external state. Idempotent: running again replaces the outputs.
Committed for reproducibility. Uses Pillow (already installed locally).

Usage:
    python scripts/render-og-image.py

Writes:
    assets/og-image.png         (1200x630, OG/Twitter share card)
    favicon.ico                 (32x32, fallback for old browsers)
    apple-touch-icon.png        (180x180, iOS Add-to-Home-Screen)
"""

from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont

# v2 design tokens
BG = (10, 14, 20)            # #0a0e14
FG = (214, 222, 230)         # #d6dee6
DIM = (90, 101, 115)         # #5a6573
ACCENT = (245, 179, 66)      # #f5b342

ROOT = Path(__file__).resolve().parent.parent
OG_OUT = ROOT / "assets" / "og-image.png"
ICO_OUT = ROOT / "favicon.ico"
APPLE_OUT = ROOT / "apple-touch-icon.png"


# ---------- font discovery ----------
FONT_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts/JetBrainsMono-Regular.ttf",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts/JetBrainsMono-Bold.ttf",
    Path("C:/Windows/Fonts/JetBrainsMono-Regular.ttf"),
    Path("C:/Windows/Fonts/JetBrainsMono-Bold.ttf"),
    Path("C:/Windows/Fonts/CascadiaMono.ttf"),
    Path("C:/Windows/Fonts/CascadiaCode.ttf"),
    Path("C:/Windows/Fonts/consola.ttf"),     # Consolas
    Path("C:/Windows/Fonts/consolab.ttf"),    # Consolas Bold
]


def find_mono(prefer_bold: bool = False) -> Path | None:
    """Return the first available mono font on this machine, preferring bold."""
    bold_names = ("Bold", "consolab", "CascadiaMono")
    if prefer_bold:
        for p in FONT_PATHS:
            if p.exists() and any(b in p.name for b in bold_names):
                return p
    for p in FONT_PATHS:
        if p.exists():
            return p
    return None


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = find_mono(prefer_bold=bold)
    if path is None:
        print("warning: no JetBrains Mono / Cascadia / Consolas found on disk; using PIL default")
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size=size)


# ---------- OG image (1200x630) ----------
def render_og() -> None:
    W, H = 1200, 630
    PAD = 80

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    name_font = load_font(76, bold=True)
    eyebrow_font = load_font(26, bold=False)
    prompt_font = load_font(28, bold=True)
    body_font = load_font(28, bold=False)
    metrics_font = load_font(22, bold=False)
    url_font = load_font(20, bold=False)

    # Name
    d.text((PAD, PAD), "JAKE HOFFMAN", font=name_font, fill=FG)

    # Status dot in the right margin, aligned to the name's baseline
    dot_r = 9
    dot_cx = W - PAD - 14
    dot_cy = PAD + 76 // 2 + 4
    d.ellipse((dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r), fill=ACCENT)
    d.text((dot_cx - dot_r - 110, dot_cy - 13), "ACTIVE", font=eyebrow_font, fill=DIM)

    # Eyebrow
    d.text((PAD, PAD + 92), "computer engineering @ queen's · class of 2027", font=eyebrow_font, fill=DIM)

    # Terminal-flavored body
    y = PAD + 92 + 50
    d.text((PAD, y), "$ whoami", font=prompt_font, fill=ACCENT)
    y += 50
    body_lines = [
        "> i build production-grade software — trading",
        "> agents, arbitrage daemons, web platforms,",
        "> and ml pipelines.",
    ]
    for line in body_lines:
        d.text((PAD, y), line, font=body_font, fill=FG)
        y += 42

    # Metrics
    y += 28
    metrics = "//  4 production systems  ·  10 bookmakers  ·  dean's scholar"
    d.text((PAD, y), metrics, font=metrics_font, fill=DIM)

    # Footer URL (bottom-right)
    url = "jakethehoffer.github.io/website"
    bbox = d.textbbox((0, 0), url, font=url_font)
    url_w = bbox[2] - bbox[0]
    d.text((W - PAD - url_w, H - PAD - 20), url, font=url_font, fill=DIM)

    OG_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OG_OUT, "PNG", optimize=True)
    print(f"wrote {OG_OUT}  ({OG_OUT.stat().st_size:,} bytes)")


# ---------- shared icon glyph ----------
def render_jh_glyph(size: int, *, padding_ratio: float = 0.12, with_rim: bool = True) -> Image.Image:
    """Render the JH glyph centered in a near-black rounded square."""
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)

    if with_rim:
        rim_width = max(1, size // 32)
        rim_color = (int(ACCENT[0] * 0.45), int(ACCENT[1] * 0.45), int(ACCENT[2] * 0.45))
        d.rectangle((rim_width, rim_width, size - rim_width, size - rim_width), outline=rim_color, width=rim_width)

    # Glyph
    glyph_size = int(size * (1 - padding_ratio * 2) * 0.7)
    font = load_font(glyph_size, bold=True)
    text = "JH"
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1]
    d.text((x, y), text, font=font, fill=ACCENT)

    return img


def render_favicon_ico() -> None:
    # Render at 32x32 (the actual final size). We also bake a 16x16 frame
    # so old clients picking the smaller size still look acceptable.
    icon_32 = render_jh_glyph(32, padding_ratio=0.06)
    icon_16 = render_jh_glyph(16, padding_ratio=0.0, with_rim=False)
    icon_32.save(ICO_OUT, format="ICO", sizes=[(16, 16), (32, 32)], append_images=[icon_16])
    print(f"wrote {ICO_OUT}  ({ICO_OUT.stat().st_size:,} bytes)")


def render_apple_touch() -> None:
    img = render_jh_glyph(180, padding_ratio=0.12, with_rim=False)
    img.save(APPLE_OUT, "PNG", optimize=True)
    print(f"wrote {APPLE_OUT}  ({APPLE_OUT.stat().st_size:,} bytes)")


def main() -> None:
    render_og()
    render_favicon_ico()
    render_apple_touch()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit the script**

```bash
git -C "C:/Users/14jak/GitHub/website" add scripts/render-og-image.py
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add render-og-image.py for OG card + favicon.ico + apple-touch-icon"
```

---

## Task 3: Run the script and inspect the OG image

**Files:**
- Create (via script): `assets/og-image.png`, `favicon.ico`, `apple-touch-icon.png`

- [ ] **Step 1: Run the script**

```bash
python "C:/Users/14jak/GitHub/website/scripts/render-og-image.py"
ls -la "C:/Users/14jak/GitHub/website/assets/og-image.png" "C:/Users/14jak/GitHub/website/favicon.ico" "C:/Users/14jak/GitHub/website/apple-touch-icon.png"
```

Expected: three new files. OG image around 50–80 KB, favicon.ico under
5 KB, apple-touch-icon under 10 KB. If the script prints
`warning: no JetBrains Mono / Cascadia / Consolas found on disk`, the
files still render but the typography will use PIL's bitmap default —
visually ugly, retry would be needed. If that happens, install
JetBrains Mono locally (or accept Cascadia) and re-run.

- [ ] **Step 2: View `og-image.png` in the chat**

Confirm:
- 1200×630, near-black background
- "JAKE HOFFMAN" rendered in bold mono at top-left
- Amber `● ACTIVE` cluster in top-right
- Three-line `> ...` body block, readable
- `// 4 production systems · ...` metric line below
- URL `jakethehoffer.github.io/website` in dim text at bottom-right

If the layout looks off (text overlapping, name running off the right
edge, etc.) adjust the script and re-run.

- [ ] **Step 3: View `favicon.ico` and `apple-touch-icon.png`**

Read both files. Confirm:
- Amber `JH` glyph centered in a near-black rounded square
- 32×32 favicon is recognizable at small size
- 180×180 apple touch icon has more breathing room (12% padding)

- [ ] **Step 4: Commit all three raster assets**

```bash
git -C "C:/Users/14jak/GitHub/website" add assets/og-image.png favicon.ico apple-touch-icon.png
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: render og-image, favicon.ico, apple-touch-icon"
```

---

## Task 4: Wire up `<head>` in `index.html`

**Files:**
- Modify: `C:/Users/14jak/GitHub/website/index.html` (head only)

- [ ] **Step 1: Replace the OG/Twitter block with the expanded version**

In `index.html`, find this exact block (currently lines 22–26):

```html
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="Jake Hoffman — Computer Engineering @ Queen's University" />
    <meta property="og:description" content="3rd-year Computer Engineering student. Builds trading agents, arbitrage daemons, web platforms, and ML pipelines." />
    <meta property="og:url" content="https://jakethehoffer.github.io/website/" />
    <meta name="twitter:card" content="summary" />
```

Replace with:

```html
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="Jake Hoffman — Computer Engineering @ Queen's University" />
    <meta property="og:description" content="3rd-year Computer Engineering student. Builds trading agents, arbitrage daemons, web platforms, and ML pipelines." />
    <meta property="og:url" content="https://jakethehoffer.github.io/website/" />
    <meta property="og:image" content="https://jakethehoffer.github.io/website/assets/og-image.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="Jake Hoffman — engineering-log style portfolio preview" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:image" content="https://jakethehoffer.github.io/website/assets/og-image.png" />
    <meta name="theme-color" content="#0a0e14" media="(prefers-color-scheme: dark)" />
    <meta name="theme-color" content="#f5efe4" media="(prefers-color-scheme: light)" />
    <link rel="icon" type="image/svg+xml" href="favicon.svg" />
    <link rel="icon" type="image/x-icon" href="favicon.ico" sizes="32x32" />
    <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180" />
```

This adds 10 lines of meta/link tags between the existing OG block and
the closing `</head>` JSON-LD block, without touching anything else.

- [ ] **Step 2: Verify the head structurally**

```bash
echo "=== Head section after edit ==="
python -c "
import re
with open(r'C:/Users/14jak/GitHub/website/index.html', encoding='utf-8') as f:
    h = f.read()
head = h.split('</head>')[0]
print('og:* tags:           ', len(re.findall(r'property=\"og:', head)))
print('twitter:* tags:      ', len(re.findall(r'twitter:', head)))
print('theme-color tags:    ', head.count('name=\"theme-color\"'))
print('link rel=\"icon\":     ', len(re.findall(r'rel=\"icon\"', head)))
print('link rel=\"apple-touch-icon\":', head.count('rel=\"apple-touch-icon\"'))
print('Inter refs (should be 0):', head.lower().count('inter:wght'))
"
```

Expected:
- og:* tags: 8 (type, title, description, url, image, image:width, image:height, image:alt)
- twitter:* tags: 2 (card, image)
- theme-color tags: 2 (dark, light)
- link rel="icon": 2 (svg, ico)
- link rel="apple-touch-icon": 1
- Inter refs: 0

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/14jak/GitHub/website" add index.html
git -C "C:/Users/14jak/GitHub/website" commit -m "feat: add og:image, twitter card, theme-color, favicon links to head"
```

---

## Task 5: Smoke tests + push + handoff

**Files:** none modified; verification only

- [ ] **Step 1: Serve and check every asset returns 200**

```bash
cd "C:/Users/14jak/GitHub/website" && python -m http.server 8765 > "$TEMP/jh-http4.log" 2>&1 &
sleep 2
echo "=== Asset responses ==="
for path in "" styles.css script.js favicon.svg favicon.ico apple-touch-icon.png assets/og-image.png assets/projects/mega-ttt.webp assets/projects/walking-jumping-cm.png assets/projects/private-platform.webp resume.pdf; do
  curl -s -o /dev/null -w "$path: %{http_code} (%{size_download} bytes)\n" "http://localhost:8765/$path"
done
echo ""
echo "=== Live page weight check (excluding scraper-only assets) ==="
python -c "
import os
live = [
    r'C:/Users/14jak/GitHub/website/index.html',
    r'C:/Users/14jak/GitHub/website/styles.css',
    r'C:/Users/14jak/GitHub/website/script.js',
    r'C:/Users/14jak/GitHub/website/favicon.svg',
    r'C:/Users/14jak/GitHub/website/assets/projects/private-platform.webp',
    r'C:/Users/14jak/GitHub/website/assets/projects/mega-ttt.webp',
    r'C:/Users/14jak/GitHub/website/assets/projects/walking-jumping-cm.png',
]
scraper_only = [
    r'C:/Users/14jak/GitHub/website/favicon.ico',
    r'C:/Users/14jak/GitHub/website/apple-touch-icon.png',
    r'C:/Users/14jak/GitHub/website/assets/og-image.png',
]
live_total = sum(os.path.getsize(p) for p in live)
scraper_total = sum(os.path.getsize(p) for p in scraper_only)
print(f'  Live (page-fetched):    {live_total:>7,} bytes  (target < 200000)')
print(f'  Scraper-only assets:    {scraper_total:>7,} bytes  (not on critical path)')
"
pkill -f "http.server 8765" 2>/dev/null; sleep 1
echo "server stopped"
```

Expected:
- All 11 paths return 200
- Live total stays under 200 KB (favicon.svg adds ~600 bytes; the
  three raster icons are NOT in the live total because nothing on the
  page links them directly into the body — they're only fetched by
  scrapers and OS handlers via the `<link rel="...">` tags in `<head>`,
  which trigger lazy fetches)
- Wait — `<link rel="icon">` *does* trigger a browser fetch, so the
  16/32 ICO and the SVG favicon **are** on the live critical path,
  technically. Both are tiny (under 5 KB combined) and the budget
  is fine. The OG image and apple touch icon are the truly off-path
  assets.

- [ ] **Step 2: Push to origin**

```bash
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

- [ ] **Step 3: Commit the implementation plan**

```bash
git -C "C:/Users/14jak/GitHub/website" add docs/superpowers/plans/2026-05-12-share-card-polish.md
git -C "C:/Users/14jak/GitHub/website" commit -m "docs: add share-card polish implementation plan"
git -C "C:/Users/14jak/GitHub/website" push 2>&1 | tail -3
```

- [ ] **Step 4: Update the .ai-sync handoff**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "Share-card polish landed. Custom 1200x630 OG image rendered via PIL, hand-written SVG favicon plus ICO fallback, 180x180 Apple touch icon, and the full meta tag block (og:image, twitter card upgrade to summary_large_image, theme-color for dark/light, icon links)." -FilesChanged "favicon.svg (NEW), favicon.ico (NEW), apple-touch-icon.png (NEW), assets/og-image.png (NEW), scripts/render-og-image.py (NEW), index.html (head only), docs/superpowers/specs/2026-05-12-share-card-polish.md, docs/superpowers/plans/2026-05-12-share-card-polish.md" -TestsRun "Smoke: all 11 asset paths 200, live page weight under 200KB, head has 8 og tags + 2 twitter tags + 2 theme-color tags + 2 icon links + 1 apple-touch-icon link, 0 Inter font refs." -Blockers "OG image scrapers won't fetch until the repo is public + Pages deployed; the asset is committed and the meta URL is absolute, so the moment the URL goes live, shares work." -NextSteps "1) Consider making repo public + enabling GitHub Pages. 2) Test the OG card via metatags.io or opengraph.xyz once deployed. 3) Next polish candidate: self-host JetBrains Mono."
```

- [ ] **Step 5: Final status check**

```bash
git -C "C:/Users/14jak/GitHub/website" log --oneline | head -10
git -C "C:/Users/14jak/GitHub/website" status
```

Expected: clean working tree, recent commits show the polish work,
`origin/main` in sync.

---

## Closing checklist

After Task 5:
- [ ] All 5 task headings checked off above
- [ ] `favicon.svg`, `favicon.ico`, `apple-touch-icon.png`, `assets/og-image.png` all exist and render correctly
- [ ] `scripts/render-og-image.py` reproduces them
- [ ] `index.html` head has all 13 new lines wired in
- [ ] Smoke tests pass (all assets 200, live weight under 200 KB)
- [ ] All work pushed to `origin/main`
- [ ] .ai-sync handoff updated
