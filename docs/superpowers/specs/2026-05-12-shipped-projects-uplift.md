# Shipped Projects Visual Uplift — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved direction, proceeding to plan + implementation

## Why

v2 introduced FUSE-Web's real product screenshot but left the three SHIPPED
projects (Mega Tic-Tac-Toe, Smart Shoe, Walking/Jumping Classifier) with
ASCII output samples. Two of those samples reference real projects but no
longer feel as concrete as FUSE-Web's. This cycle uplifts Mega TTT and
Walking/Jumping with real visual assets sourced from real outputs — no
fakery, no fresh implementation, no scope drift into "what else can we
improve."

## Goal

Pull two real visual assets into the site:
1. A gameplay screenshot of Mega Tic-Tac-Toe pulled from the public
   itch.io listing.
2. A matplotlib-rendered confusion matrix using the actual numeric
   results already shown in the Walking/Jumping ASCII sample.

Add an itch.io CTA to the Mega TTT card so the path from "I see this"
to "I downloaded the game" is one click.

## Non-Goals

- No re-implementation of the game in JS / canvas / WebGL.
- No new screenshots for Smart Shoe (no good public asset; the Dart code
  sample is authentic and on-aesthetic).
- No changes to the trader, Odds Aggregator, or FUSE-Web cards.
- No animations, no carousels, no lightbox.

## Concrete Changes

### 1. Mega TTT — gameplay screenshot + itch.io CTA

**Asset source:** the 3rd image on
<https://jakethehoffer.itch.io/mega-tictactoe>, a gameplay screenshot
showing several sub-board placements plus a large blue O that has
claimed one of the sub-boards. Communicates the meta-rule visually in a
single frame.

**File output:**
`C:/Users/14jak/GitHub/website/assets/projects/mega-ttt.webp`,
encoded at quality 80, ≤ 50 KB. Source PNG is 802×802; WebP keeps the
same dimensions.

**HTML changes** in `index.html` Mega TTT card:
- Change `<h3 class="project__name">Mega Tic-Tac-Toe</h3>` to wrap the
  title in an anchor pointing to the itch.io page (matches the link
  pattern used by `trader` and `Odds Aggregator` for their GitHub
  links).
- Remove the existing `<pre class="project__sample">+---+---+---+ ...`
  ASCII board block.
- Insert a `<figure class="project__media">` with the WebP image
  (same `.project__media` class FUSE-Web already uses — zero new CSS).
- Below the figure, insert a `<p class="project__cta">` containing a
  `[ play on itch.io ↗ ]` link styled as `.btn`.

**Minor CSS:** one new rule, `.project__cta { margin: 0.875rem 0 0; }`.

### 2. Walking/Jumping — matplotlib confusion matrix

**Source numbers** (already in the existing ASCII sample, copied to a
real chart):
- TN (true walk, pred walk): 182
- FP (true walk, pred jump):   7
- FN (true jump, pred walk):   5
- TP (true jump, pred jump): 156
- Reported accuracy 0.965, F1 0.964 (rendered as subtitle).

**Generation script:** a one-shot Python script at
`scripts/render-wj-cm.py` (kept in the repo for reproducibility, not
required to run for normal site serving). Renders a 600×400 PNG with:

- Background `#0a0e14` (matches `--bg`)
- Text `#d6dee6` (matches `--text`)
- Heatmap diagonal in amber `#f5b342` (matches `--accent`); off-diagonal
  in muted grey `#1c2330` (matches `--bg-grid`)
- Cell counts rendered in cell, in `#0a0e14` on the amber diagonal and
  `#d6dee6` on the muted cells
- Title: `confusion matrix — walking vs jumping`
- Subtitle: `accuracy 0.965 · f1 0.964`
- Mono font family — fall back to DejaVu Sans Mono if JetBrains Mono
  isn't installed locally (matplotlib doesn't auto-discover Google
  Fonts; we use whatever mono is available, which renders identically
  in spirit)

**File output:**
`C:/Users/14jak/GitHub/website/assets/projects/walking-jumping-cm.png`,
≤ 25 KB target.

**HTML changes** in the Walking/Jumping card:
- Remove the existing `<pre class="project__sample">...182 ... 7 ...
  5 ... 156 ...</pre>` block.
- Insert a `<figure class="project__media">` referencing the new PNG.
- The card retains its tech chips and metrics row unchanged.

No new CSS — reuses `.project__media`.

### 3. Smart Shoe — unchanged

The Dart code sample is the authentic asset for a mobile/embedded
project where no real screenshot is at hand. Mocking up a stylized
phone frame would downgrade authenticity. Leave it as-is.

## File Layout Delta

```
website/
├── assets/projects/
│   ├── fuse-web.webp                  unchanged
│   ├── mega-ttt.webp                  NEW
│   └── walking-jumping-cm.png         NEW
├── scripts/
│   ├── refresh-meta.mjs               unchanged
│   └── render-wj-cm.py                NEW
├── index.html                         modified (2 cards)
├── styles.css                         +1 rule
└── docs/superpowers/specs/
    └── 2026-05-12-shipped-projects-uplift.md   THIS DOC
```

## Verification

- Open the page after each change; confirm the new asset renders and
  the card still flows correctly on mobile (1-col grid) and desktop
  (2-col grid).
- Confirm new total page weight stays under the 200 KB budget. Pre-
  change baseline is 114 KB; adding ≤ 50 KB mega-ttt.webp + ≤ 25 KB
  walking-jumping-cm.png lands at roughly 189 KB. Within budget.
- Confirm the itch.io CTA opens the public page in a new tab.

## Risks

- **The confusion-matrix PNG won't quite match the page's
  JetBrains-Mono-via-Google-Fonts rendering.** Matplotlib can't read
  Google Fonts; we fall back to a system mono. Visually close enough
  for a portfolio chart, not pixel-identical.
- **WebP quality on the itch.io PNG.** Quality 80 is conservative and
  usually fine for 800×800 source. If banding/artifacts show up after
  conversion, bump to quality 85 or fall back to PNG.
- **The CTA button could compete with the GitHub-style title link.**
  Mitigated by placing the CTA *after* the screenshot, in a different
  visual register, and using `.btn` (which is already the
  resume-page primary CTA style and reads as a recognizable affordance).

## Out of Scope

- Changes to any other project card.
- The case-study section (already done in v2).
- Boot sequence, theme system, refresh-meta script.
- A "play in browser" build of the Unity game.
- Smart Shoe asset hunt.
