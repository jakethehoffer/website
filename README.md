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

## Refresh project last-commit data (optional)

`scripts/refresh-meta.mjs` pulls `pushed_at` from GitHub for each
featured repo and rewrites the corresponding `<span data-meta="...">` in
`index.html`. It also stamps the footer `last_deployed`.

```bash
node scripts/refresh-meta.mjs
```

Requires the `gh` CLI authenticated with read access to the repos in the
script's `REPOS` list. Safe to skip &mdash; defaults stay in place if you
don't run it.

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
- `assets/projects/[removed].webp` &mdash; [removed] product screenshot.
- `resume.pdf` &mdash; downloadable PDF.
- `docs/superpowers/` &mdash; design spec and implementation plan.
