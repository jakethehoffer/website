# refresh-meta `[miss]` Log Fix — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, executing inline

## Why

`refresh-meta.mjs` currently uses `[miss]` for two distinct situations:
1. Sentinel actually missing from `index.html` (real bug — script is
   referencing a key that doesn't exist on the page).
2. Sentinel found, but the computed new value is identical to the
   existing one — i.e., dates haven't changed since last run.

Case 2 is the **common case** during normal operation. Logging it as
`[miss]` makes weekly Action runs read like everything is broken when
they're actually healthy.

## Goal

Three distinct log outcomes in `refresh-meta.mjs`:

| Outcome | When | Severity |
|---|---|---|
| `[ok]`   | sentinel found AND value differs — wrote update | info |
| `[same]` | sentinel found AND value matches current text — no write | info |
| `[miss]` | sentinel NOT found in `index.html` — real config error | warn |

## Non-Goals

- Changing the script's API or CLI.
- Touching `index.html` or its sentinel markup.
- Changing the GitHub Action workflow.

## Implementation

`replaceMeta(html, key, value)` currently returns the new HTML
(possibly identical to input). Update it to return `{ html, matched }`
where `matched` is true iff the regex hit at least one occurrence.

Main loop branches on `matched` first, then on `html !== before`:

```js
const result = replaceMeta(html, repo.key, value);
html = result.html;
if (!result.matched) {
  console.warn(`[miss] ${repo.key} (no sentinel found in index.html)`);
} else if (html !== before) {
  touched++;
  console.log(`[ok]   ${repo.key} = "${value}"`);
} else {
  console.log(`[same] ${repo.key} = "${value}" (unchanged)`);
}
```

Apply the same pattern to the `last_deployed` block at the bottom.

## File Layout Delta

```
website/
└── scripts/refresh-meta.mjs              MODIFIED (~10 lines)
```

## Verification

- Run the script locally; expected output for all three repos:
  `[same] X.last_commit = "last commit: today" (unchanged)`. No
  `[miss]` lines (sentinels exist).
- Dispatch the GitHub Action via `gh workflow run refresh-meta.yml`
  and confirm the log shows `[same]` lines, not `[miss]`.

## Risks

- None meaningful. The change is internal logging only; the script's
  external behavior (commits, exit code) is unchanged.
