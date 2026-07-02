# website

Single-page resume for Jake Hoffman &mdash; the "engineering log" v2.
Plain HTML, CSS, and a touch of vanilla JS. No framework, no build step.

**Live at <https://jakethehoffer.github.io/website/>**

## Serve locally

```bash
python -m http.server 8000
```

Open <http://localhost:8000/>. You can also just double-click
`index.html` &mdash; it works `file://` too.

## Adding or editing projects

Project content (cards on the site + entries on the resume) lives in
`projects.yml`. To add or edit a project, change that one file and run:

```bash
python scripts/build-site.py
```

This calls four generators in order:

- `scripts/generate-cards.py` &mdash; rewrites the `<div class="projects">`
  block of `index.html` from `projects.yml`. Live `last commit:` pill
  values already on the page are preserved (the YAML placeholder is
  only used for a brand-new card).
- `scripts/build-resume.py` &mdash; builds `resume-source.docx` **from
  scratch** out of two tracked text files: `resume-static.yml` (contact
  header, summary, education, experience) + `projects.yml` (the
  PERSONAL PROJECTS section, by `resume_priority` + cap). No binary
  template; the docx is fully reproducible from text.
- `scripts/render-og-image.py` &mdash; renders `assets/og-image.png` +
  favicons from constants in the script (Pillow). Part of the build so
  the share card can't drift from the hero claims again.
- `scripts/refresh-meta.py` &mdash; refreshes `last-commit` timestamps
  for projects with `auto_meta: true` and stamps the footer
  `last_deployed` + the sitemap `lastmod`.

`build-site.py` then rebuilds `resume.pdf` automatically when
LibreOffice is installed (soffice on PATH or the default Windows
install location). Without LibreOffice it prints the manual command:

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

Commit `index.html`, the YAML you changed, and `resume.pdf` together.
Forgetting the PDF is now caught in CI: `verify-site.py` asserts the
PDF's text contains the name, GPA, and every project name the resume
is supposed to feature from the current sources.
`resume-source.docx` is gitignored &mdash; it's a derived artifact, not a
source.

### Editing the resume

- **Projects** on the resume: edit `projects.yml` (`resume:` block +
  `resume_priority`). See "Resume curation" below.
- **Everything else** (contact line, summary, education, experience):
  edit `resume-static.yml`. It's plain, diffable text; the formatting
  (Garamond, margins, bullet/date layout) lives in `build-resume.py`.

## projects.yml schema

Each entry:

| field | description |
|---|---|
| `key` | short id; matches `data-meta="<key>.last_commit"` on the page |
| `name` | displayed name in the card's `<h3>` |
| `status` | `active`, `shipped`, or `archived` (controls the pill colour) |
| `url` | external link; `null` = name renders without an `<a>` wrapper |
| `private` | `true` &rarr; name renders as a `private` pill, not a (404-ing) link |
| `case_study` | optional on-page anchor (e.g. `"#case-study"`) for a `[ read case study ↓ ]` CTA |
| `resume_priority` | int; higher = more important (drives resume curation, below) |
| `meta_key` | data-meta sentinel key (usually `<key>.last_commit`) |
| `auto_meta` | `true` &rarr; `refresh-meta.py` auto-updates the timestamp |
| `hardcoded_date` | fallback string when `auto_meta: false` (e.g. `"mar 2024"`) |
| `what` | 1-2 sentence lede (HTML allowed for entities) |
| `body` | 80-120 word description (HTML allowed) |
| `metrics` | terse stats line (HTML entities pre-encoded) |
| `chips` | tech-stack chips line |
| `sample` | optional `{label, html}` for a code-block example |
| `media` | optional `{src, alt, width, height}` for an image |
| `cta` | optional `{label, url}` for an external CTA button |
| `resume` | optional `{role, bullets}` for the resume; `null`/omit to skip |

Project order in the rendered page matches order in `projects.yml`.

### Resume curation (one-page guarantee)

The **website** shows every project. The **resume** shows only the top
`RESUME_MAX_PROJECTS` (in `scripts/build-resume.py`, currently 4) of
the projects that have a `resume:` block, ranked by `resume_priority`
(highest first) and displayed in `projects.yml` order.

This means adding a project never forces manual cuts to
EXPERIENCE/EDUCATION to keep the resume on one page — a new project
simply competes for the capped slots. To feature a new project on the
resume, give it a `resume:` block and a `resume_priority` higher than
whichever project it should displace. (Because the docx is now built
from scratch from text, the old `PARAGRAPHS_TO_DROP` trim-list — ~75
lines of page-fit hacks — is gone entirely.)

## Automated daily refresh

A GitHub Action at `.github/workflows/refresh-meta.yml` runs
`refresh-meta.py` daily at 11:23 UTC (and on manual
`gh workflow run`). It commits any changes back to `main` automatically.
Daily, not weekly: the pills carry day-granularity text
("last commit: today"), so a weekly refresh serves that claim up to
six days stale.

Because the auto-commit is pushed with `GITHUB_TOKEN`, it does **not**
trigger the `verify-site` / `public-safety` workflows (GitHub's
recursion guard). The refresh workflow therefore runs
`scripts/verify-site.py` itself, after mutating the tree and before
committing — an auto-commit can't ship an unverified `index.html`.

The action reads `META_REFRESH_TOKEN` (a fine-grained PAT) from secrets.
To set it up:

1. Create a **fine-grained PAT** at
   <https://github.com/settings/personal-access-tokens/new> with
   *Repository access &rarr; All repositories* and *Repository
   permissions &rarr; Metadata: Read*. "All repositories" is the right
   scope so new projects are picked up automatically.
2. Add it to the website repo at
   <https://github.com/jakethehoffer/website/settings/secrets/actions>
   as `META_REFRESH_TOKEN`.

If the PAT is missing or expired, the daily run **fails loudly**
(refresh-meta.py exits non-zero in CI when every lookup fails) instead
of silently freezing the `last commit:` pills at their last value.
The cron also only commits when a pill actually changed &mdash; the
footer/sitemap date stamps alone don't generate `[auto]` commits.

## The public-safety banned-terms check

`.github/workflows/public-safety.yml` greps every tracked file for a
set of banned privacy terms on each push/PR. The terms live in the
`BANNED_TERMS` repo secret (one term per line, set at
<https://github.com/jakethehoffer/website/settings/secrets/actions>) —
**never** in any tracked file, including that workflow: this repo is
public, so a term written in the workflow (even split into fragments)
is itself the leak the check exists to prevent. If the secret goes
missing the check fails loudly rather than passing empty.

## The `resume.pdf` pipeline

`resume-source.docx` is a **derived artifact** (gitignored). It's built
from scratch by `scripts/build-resume.py` out of `resume-static.yml` +
`projects.yml`, then LibreOffice converts it to `resume.pdf`. The full
sequence is documented above in "Adding or editing projects". The
committed `resume.pdf` is the only public-facing binary; the docx can
always be regenerated from the tracked text sources.

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo,
then in **Settings &rarr; Pages**, source = `main` branch / root.

## Files

- `projects.yml` &mdash; single source of truth for featured projects (site + resume).
- `resume-static.yml` &mdash; tracked source for the resume's static
  sections (contact, summary, education, experience).
- `index.html` &mdash; semantic single-page markup; projects block
  generated from `projects.yml`.
- `styles.css` &mdash; all-mono design system, dark default + parchment light.
- `script.js` &mdash; boot animation, mobile nav, theme toggle, IntersectionObserver reveal.
- `scripts/build-site.py` &mdash; orchestrator (runs the four generators).
- `scripts/generate-cards.py` &mdash; renders the projects block of `index.html`.
- `scripts/build-resume.py` &mdash; builds `resume-source.docx` from scratch
  out of `resume-static.yml` + `projects.yml`.
- `scripts/render-og-image.py` &mdash; renders the OG share card + favicons.
- `scripts/refresh-meta.py` &mdash; refreshes last-commit timestamps.
- `scripts/verify-site.py` &mdash; rendered-artifact checks (HTML structure,
  resume PDF page/link/content sync, OG-image claim sync + provenance
  chunk, layout overflow at 320&ndash;1280px in both color schemes for
  `index.html` and `404.html`, axe-core accessibility gate, and the
  voice rules: no em-dashes and no graded marketing adjectives in any
  rendered prose &mdash; the `VOICE_BANNED` list in the script is the
  source of truth); run by `.github/workflows/verify-site.yml` on
  every push and by `refresh-meta.yml` before each auto-commit.
- `resume.pdf` &mdash; downloadable PDF (the committed published artifact).
- `docs/superpowers/` &mdash; design specs and implementation plans.
