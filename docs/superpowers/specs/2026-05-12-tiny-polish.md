# Tiny Polish v2.6 — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, proceeding to plan + implementation

## Why

Three small wins from the polish backlog, none requiring user input
or design decisions:

1. **Auto-refresh project metadata** so the "last commit" timestamps
   stay current without manual `node scripts/refresh-meta.mjs` runs.
2. **One ad-hoc refresh** before tagging, so v2.6 ships with the
   freshest dates achievable today.
3. **Two `<meta>` hygiene additions** that are universally
   recommended and cost essentially nothing.

## Non-Goals

- A "Now" status block. Anything I'd write would be redundant with
  the About section and the case studies. If Jake wants one, he'll
  drop a sentence.
- Google Search Console verification. Requires Jake's Google
  account; documented as a follow-up in the handoff `next-steps`.
- Custom domain (e.g., `jakehoffman.dev`). Bigger lift, separate
  cycle.
- Performance hand-tuning. Already at 100/100/100/100.
- Per-page canonical URLs for `404.html`. Standard practice is to
  omit canonical from 404 pages.

## Concrete Changes

### 1. GitHub Actions workflow — weekly metadata refresh

**File:** `.github/workflows/refresh-meta.yml`

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

**Why this shape:**
- `cron: "0 12 * * 1"` — Monday noon UTC; a quiet time, plenty of
  headroom before any expected sharing.
- `workflow_dispatch` — lets `gh workflow run refresh-meta.yml`
  trigger an ad-hoc refresh without waiting for the next Monday.
- `permissions: contents: write` — minimum scope required for the
  bot to push back to `main`.
- The bot user `github-actions[bot]` with the `noreply` email is the
  GitHub-supplied identity for `GITHUB_TOKEN` commits. Required so
  the push is authenticated correctly.
- Filters on `index.html` so the conditional commit doesn't trip on
  other working-tree noise.
- The auto-commit will retrigger Pages, which redeploys with the
  fresh markup automatically.

**Failure modes:**
- `gh api` returns 404 for a private repo the bot can't see (e.g.,
  FUSE-Web in the Shield-Restoration-Services org). The existing
  `refresh-meta.mjs` `try/catch` logs `[skip]` and leaves that field
  on the default string. Acceptable.
- Network blip prevents one of the API calls. The script may write
  *some* updates and skip others; the next Monday catches up.
- The workflow itself fails (rare). No site impact; the previous
  metadata stays.

### 2. One ad-hoc refresh now

Run `node scripts/refresh-meta.mjs` locally once before tagging
v2.6 so the tagged release has the latest dates baked in. The
workflow will keep them current from this point forward.

### 3. `<meta>` hygiene additions

**`index.html`** — insert one canonical link and one author meta in
the `<head>` block. Place after the existing OG/Twitter cluster and
before the JSON-LD script.

```html
<link rel="canonical" href="https://jakethehoffer.github.io/website/" />
<meta name="author" content="Jake Hoffman" />
```

**`404.html`** — author only (canonical doesn't apply to 404 pages
by standard practice):

```html
<meta name="author" content="Jake Hoffman" />
```

## File Layout Delta

```
website/
├── .github/
│   └── workflows/
│       └── refresh-meta.yml             NEW (~30 lines)
├── index.html                            MODIFIED (head: canonical + author, possibly fresh dates)
├── 404.html                              MODIFIED (head: author)
└── docs/superpowers/specs/
    └── 2026-05-12-tiny-polish.md         THIS DOC
```

## Verification

- `gh workflow run refresh-meta.yml` manually dispatches the action
  and completes without error. Inspect the run log via
  `gh run view --log` to confirm `[ok]` lines for trader / arbitrage
  (and the expected `[skip]` for FUSE-Web). If it auto-commits,
  confirm the new commit appears on `origin/main` with the bot
  as author.
- `curl -s https://jakethehoffer.github.io/website/ | grep -c 'rel="canonical"'`
  returns `1`.
- `curl -s https://jakethehoffer.github.io/website/ | grep -c 'name="author"'`
  returns `1`.
- `curl -s https://jakethehoffer.github.io/website/404.html | grep -c 'name="author"'`
  returns `1`.
- Lighthouse spot-check: hold 100/100/100/100, no regressions. (No
  page-weight or structural change that could plausibly move any
  metric.)

## Risks

- **Workflow trigger costs Actions minutes.** Free for public repos
  (unlimited). The job runs in well under a minute (script is one
  HTTP call per repo and a small text rewrite). Acceptable.
- **Bot commits could conflict with concurrent human commits.**
  Unlikely on a personal portfolio. If it ever does, the next
  scheduled run picks up where the conflict left off; the script
  is idempotent.
- **Auto-commit might trigger noise in commit history.** Each
  auto-commit is clearly marked `[auto]` in the message; rare
  (only fires when a date actually changes) and adds a one-liner
  per change. Acceptable.

## Out of Scope (YAGNI restatement)

- "Now" status block.
- Search Console submit (manual user step).
- Workflow that runs on `push` (cron-only avoids commit-bot loops).
- Canonical URL on 404.
- Custom domain.
- Replacing `refresh-meta.mjs` with a different approach (e.g.,
  client-side `gh api` calls). The committed-to-HTML pattern is
  good as-is.

## Success Criteria

- The next time `last commit` changes on `trader` or `arbitrage`,
  the workflow refreshes the value within a week without human
  intervention.
- Manual `gh workflow run refresh-meta.yml` works as an
  on-demand refresh.
- `<link rel="canonical">` and `<meta name="author">` are present on
  the deployed pages.
- Lighthouse stays at 100/100/100/100.
