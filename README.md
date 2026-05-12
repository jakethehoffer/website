# website

Single-page resume for Jake Hoffman. Plain HTML, CSS, and a touch of vanilla JS &mdash; no framework, no build step.

## Serve locally

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/>.

You can also just double-click `index.html` &mdash; it works file:// too.

## Deploy

Drop the repo contents on any static host. GitHub Pages: push the repo, then in **Settings &rarr; Pages**, source = `main` branch / root.

## Replace the placeholders

- `assets/avatar.svg` &mdash; swap with a real headshot at `assets/avatar.jpg` (and update the `<img src>` in `index.html`).
- `resume.pdf` &mdash; regenerate from a fresh `.docx` whenever the resume changes:
  ```bash
  "C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . resume-source.docx
  mv resume-source.pdf resume.pdf
  ```

## Files

- `index.html` &mdash; single-page document, semantic markup, JSON-LD Person schema.
- `styles.css` &mdash; design tokens, light + dark themes, all section styles.
- `script.js` &mdash; mobile nav, theme toggle, IntersectionObserver fade-in, footer year.
- `assets/avatar.svg` &mdash; initials placeholder.
- `resume.pdf` &mdash; downloadable resume.
- `docs/superpowers/` &mdash; design spec and implementation plan.
