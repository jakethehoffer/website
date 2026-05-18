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

This calls three generators in order:

- `scripts/generate-cards.py` &mdash; rewrites the `<div class="projects">`
  block of `index.html` from `projects.yml`.
- `scripts/refresh-resume.py` &mdash; updates `resume-source.docx`
  PERSONAL PROJECTS section from each project's `resume:` block.
- `scripts/refresh-meta.py` &mdash; refreshes `last-commit` timestamps
  for projects with `auto_meta: true` and stamps the footer
  `last_deployed`.

All three are idempotent. After running `build-site.py`, regenerate
the PDF:

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

Commit `index.html`, `projects.yml`, and `resume.pdf` together.

## projects.yml schema

Each entry:

| field | description |
|---|---|
| `key` | short id; matches `data-meta="<key>.last_commit"` on the page |
| `name` | displayed name in the card's `<h3>` |
| `status` | `active`, `shipped`, or `archived` (controls the pill colour) |
| `url` | external link; `null` = name renders without an `<a>` wrapper |
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
| `resume` | optional `{role, bullets}` for the resume; omit to skip |

Project order in the rendered page matches order in `projects.yml`.

## Automated weekly refresh

A GitHub Action at `.github/workflows/refresh-meta.yml` runs
`refresh-meta.py` every Monday at 12:00 UTC (and on manual
`gh workflow run`). It commits any changes back to `main` automatically.

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

Without the secret the workflow stays inert &mdash; the default
`GITHUB_TOKEN` can only read the current repo, so every project with
`auto_meta: true` logs `[skip]`.

## Refresh `resume.pdf`

`resume-source.docx` is **not tracked** by git (Office metadata
privacy &mdash; the binary captures creator/last-modified info). It lives
locally next to `resume.pdf`. `scripts/refresh-resume.py` reads,
edits, and scrubs metadata before saving.

The full refresh sequence is documented above in the "Adding or
editing projects" section. The committed `resume.pdf` is the only
public-facing artifact.

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo,
then in **Settings &rarr; Pages**, source = `main` branch / root.

## Files

- `projects.yml` &mdash; single source of truth for featured projects.
- `index.html` &mdash; semantic single-page markup; projects block
  generated from `projects.yml`.
- `styles.css` &mdash; all-mono design system, dark default + parchment light.
- `script.js` &mdash; boot animation, mobile nav, theme toggle, IntersectionObserver reveal.
- `scripts/build-site.py` &mdash; orchestrator (runs the three generators).
- `scripts/generate-cards.py` &mdash; renders the projects block.
- `scripts/refresh-resume.py` &mdash; rewrites `resume-source.docx`.
- `scripts/refresh-meta.py` &mdash; refreshes last-commit timestamps.
- `resume.pdf` &mdash; downloadable PDF.
- `docs/superpowers/` &mdash; design specs and implementation plans.
