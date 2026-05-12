# Lighthouse Audit Fixes — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

First real Lighthouse audit on the live site
(<https://jakethehoffman.github.io/website/>) returned:

| Category | Desktop | Mobile | Target |
|---|---|---|---|
| Performance | 80 | **76** | 95 |
| Accessibility | 92 | **92** | 95 |
| Best Practices | **100** | **100** | 95 |
| SEO | **100** | **100** | 95 |

Best Practices and SEO are perfect. Performance and Accessibility miss
the 95 target because of four concrete, narrow issues — none requiring
redesign. This cycle fixes them.

## Goal

Get Performance ≥ 95 and Accessibility ≥ 95 on both mobile and
desktop, without changing the visual design or adding meaningful
complexity.

## Non-Goals

- Inline-critical-CSS optimization. The "render-blocking requests"
  audit calls it out, but inlining critical CSS adds significant
  maintenance burden for marginal gain on an already-fast page.
- Aggressive cache-control headers. GitHub Pages sets short
  `Cache-Control` and we can't change them without leaving Pages.
- Image format / size further changes. The 46 KiB savings flagged by
  "Improve image delivery" is for the OG image (scraper-only, off
  critical path).
- Light-mode visual redesign. We're darkening two tokens by a few hex
  values, not rebuilding the parchment palette.

## Concrete Findings → Fixes

### Finding 1: CLS = 0.77 mobile / 0.44 desktop (Performance)

**Root cause:** the hero boot animation clears `<span data-boot-line>`
contents on `DOMContentLoaded` and types characters back in. Between
the pre-rendered HTML and the JS-cleared state, the `<pre>` block
collapses to ~3 lines, then grows back as text is typed. Combined
with potential font-swap reflow when the locally-hosted WOFF2 finishes
loading, this stacks into 15 detected layout shifts and a 0.77 CLS.

**Fix A — reserve hero box height before clearing:**
In `script.js` `bootSequence()`, measure `.hero__boot` height *before*
clearing the spans and apply it as inline `min-height`. The `<pre>`
no longer collapses; the layout is locked from frame zero. Code
change:

```js
// In bootSequence(), after computing reduceMotion/alreadyPlayed and
// before clearing the spans:
const preEl = document.querySelector(".hero__boot");
if (preEl) {
  preEl.style.minHeight = preEl.getBoundingClientRect().height + "px";
}
```

**Fix B — preload the font:**
Add to `<head>` of `index.html` and `404.html`:

```html
<link rel="preload" href="assets/fonts/jetbrains-mono-variable.woff2"
      as="font" type="font/woff2" crossorigin />
```

This makes the browser fetch the WOFF2 in parallel with CSS parsing
rather than after CSS discovers the `@font-face` rule. The window
between system-mono and JetBrains Mono shrinks from ~200ms to ~30ms,
shrinking font-swap CLS into the noise.

The combination should drop CLS from 0.77 → < 0.05 on mobile and
0.44 → < 0.05 on desktop. With CLS in the "good" range, Performance
typically jumps from ~76 to ~95+ (CLS is a heavy contributor).

### Finding 2: Parchment-theme color contrast (Accessibility)

**Root cause:** two tokens in `:root[data-theme="light"]` don't meet
WCAG AA 4.5:1 against the cream background `#f5efe4`:

| Token | Current | Contrast | Status |
|---|---|---|---|
| `--accent` | `#a86a14` | 3.87:1 | Fails AA |
| `--text-mute` | `#6a7480` | 4.10:1 | Fails AA |

Affected elements (light-theme only — dark theme passes everywhere):
- `.boot__prompt`, `.btn--primary`, `.education__gpa` use `--accent`
- `.section__label`, `.hero__skip`, `.site-footer__meta` use `--text-mute`

**Fix — darken both tokens:**

| Token | New value | Contrast | Status |
|---|---|---|---|
| `--accent` | `#915308` | **5.28:1** | Passes AA, ~1.2× margin |
| `--text-mute` | `#525a66` | **6.08:1** | Passes AA + AAA for body |

Math: ratios computed using WCAG 2.x relative luminance against
background `#f5efe4` (luminance 0.869). The darker values shift the
parchment theme slightly toward "newsprint" but stay on-aesthetic.

The dark-theme tokens are unchanged.

### Finding 3: `aria-label` on `<span>` without role (Accessibility)

**Root cause:** the 6 project status dots use
`<span class="status" aria-label="Status: active"></span>`. Per ARIA
1.2, `aria-label` is "prohibited" on generic elements (any element
without a valid role). The timeline status dots have `aria-hidden=true`
so they're fine; only the project-card dots are flagged.

**Fix — add `role="img"`:** The dot is a visual status indicator, so
`role="img"` is semantically correct. New markup:

```html
<span class="status status--active" role="img" aria-label="Status: active"></span>
<span class="status status--shipped" role="img" aria-label="Status: shipped"></span>
```

Two `replace_all` edits in `index.html` cover all 6 cards.

## File Layout Delta

```
website/
├── index.html                              MODIFIED (head: preload; project cards: role="img")
├── 404.html                                MODIFIED (head: preload)
├── styles.css                              MODIFIED (parchment tokens)
├── script.js                               MODIFIED (boot sequence min-height)
└── docs/superpowers/specs/
    └── 2026-05-12-lighthouse-fixes.md      THIS DOC
```

No new files, no new dependencies, no design changes. All four edits
are narrow and reversible.

## Verification

After implementing, re-run the same Lighthouse audit (CLI via npx)
against the live deployed URL and confirm:

- Performance ≥ 95 on both mobile and desktop
- Accessibility ≥ 95 on both
- Best Practices and SEO remain 100
- CLS specifically drops to < 0.1 (Google's "good" threshold)
- No regression in FCP / LCP / TBT (they were excellent already)

If any category misses the target by a small margin, document it in
the v2.4 commit message and accept; if it misses by a lot, return to
this spec and revise.

## Risks

- **Boot sequence min-height could create dead space on a viewport
  width different from when the measurement was taken** — mitigated
  because the measurement happens after the static end-state is
  rendered in HTML, at the actual current viewport width. If the user
  resizes mid-animation, the locked height might be slightly off, but
  the animation typically completes in <2s and resizes during that
  window are vanishingly rare.
- **Preloading a 40 KB font on every page load is slightly wasteful
  if a return visitor has it cached** — Chrome's resource cache and
  HTTP cache handle this correctly; the preload becomes a no-op for
  cached fonts.
- **Darker parchment accent might read slightly muddier on certain
  monitors** — acceptable trade-off for accessibility compliance.
  Dark theme is unchanged and remains the default.
- **`role="img"` requires `aria-label` to be present** — already
  satisfied.

## Out of Scope (YAGNI restatement)

- Replacing the boot sequence with a CSS-only animation
- Tuning `size-adjust`, `ascent-override`, `descent-override` on a
  fallback `@font-face` (preload alone should be sufficient; this is
  a deeper optimization if preload isn't enough)
- WOFF2 subsetting beyond Latin (would drop ~20 KB but is a larger
  change in scope)
- Adding a Service Worker for caching
- Adding `<link rel="modulepreload">` for `script.js` (it's already
  4 KB and not critical-render-blocking with `defer`)

## Success Criteria

A second Lighthouse audit shows all four categories at ≥ 95 on both
strategies, with CLS in the "good" range (< 0.1) and the same fast
FCP/LCP as before. Visual design is identical to v2.3 on both themes.
