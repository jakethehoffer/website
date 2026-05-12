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

## Refresh project last-commit data

`scripts/refresh-meta.mjs` pulls `pushed_at` from GitHub for each
featured repo and rewrites the corresponding `<span data-meta="...">` in
`index.html`. It also stamps the footer `last_deployed`.

```bash
node scripts/refresh-meta.mjs
```

Requires the `gh` CLI authenticated with read access to the repos in the
script's `REPOS` list. Safe to skip &mdash; defaults stay in place if you
don't run it.

### Automated weekly refresh (optional setup)

A GitHub Action at `.github/workflows/refresh-meta.yml` runs the same
script every Monday at 12:00 UTC (and on manual `gh workflow run`).
It commits any changes back to `main` automatically.

The source repos (`trader`, `arbitrage`, `FUSE-Web`) are private, so the
default `GITHUB_TOKEN` can't read them &mdash; the action no-ops without
a personal-access token. To activate weekly refresh:

1. Create a **fine-grained PAT** at
   <https://github.com/settings/personal-access-tokens/new> with
   *Repository permissions &rarr; Metadata: Read* on `jakethehoffer/trader`,
   `jakethehoffer/arbitrage`, and `Shield-Restoration-Services/FUSE-Web`.
2. Add it to the website repo at
   <https://github.com/jakethehoffer/website/settings/secrets/actions>
   as `META_REFRESH_TOKEN`.

Without the secret the workflow stays inert. Manual
`node scripts/refresh-meta.mjs` continues to work normally either way.

## Refresh `resume.pdf`

```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
mv resume-source.pdf resume.pdf
```

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo,
then in **Settings &rarr; Pages**, source = `main` branch / root.

## Files

- `index.html` &mdash; semantic single-page markup, boot-sequence end-state, JSON-LD Person.
- `styles.css` &mdash; all-mono design system, dark default + parchment light.
- `script.js` &mdash; boot animation, mobile nav, theme toggle, IntersectionObserver reveal.
- `scripts/refresh-meta.mjs` &mdash; optional last-commit injector (Node, uses `gh`).
- `assets/projects/fuse-web.webp` &mdash; FUSE-Web product screenshot.
- `resume.pdf` &mdash; downloadable PDF.
- `docs/superpowers/` &mdash; design spec and implementation plan.
