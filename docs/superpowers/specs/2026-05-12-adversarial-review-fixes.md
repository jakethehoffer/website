# Adversarial Review Fixes — Design Spec

**Author:** Jake Hoffman
**Date:** 2026-05-12
**Status:** Approved, executing

## Why

External adversarial review surfaced four real issues:

1. **FUSE-Web reference leakage in public docs.** v2.7 removed FUSE
   from the live site, but the v2.7 spec/plan (`remove-fuse-web.md`)
   are *more* explicit about FUSE than the site ever was — the spec
   even says "should not be publicly attributed to Jake on the site."
   Anyone reading the public repo learns more than someone reading
   the deployed site. 13 tracked files reference FUSE-Web.
2. **404 page absolute-path bug.** I used `/styles.css`,
   `/assets/...`, `/#projects` etc. in `404.html`. On GitHub Pages
   with the subpath `jakethehoffer.github.io/website/`, root-relative
   paths resolve to `jakethehoffer.github.io/*` — the wrong place.
   The 404 page is unstyled and its recovery links go to the user
   root, not back to the home page. 9 broken paths.
3. **`resume-source.docx` privacy.** The binary docx ships Office
   metadata (creator, last-modified). Two docs still contain the old
   full-address text "3 Collinson Blvd, Toronto ON M3H 3B7" even
   though the live resume now says "Toronto, ON".
4. **No regression guardrail.** Nothing prevents FUSE-Web, the old
   address, broken subpath links, or `resume-source.docx` from
   creeping back in on future edits.

## Goal

A repo where:
- The public surface (tracked files + live URL) tells the same story
  about FUSE-Web — namely, nothing.
- The 404 page actually works on the subpath deploy.
- The privacy-sensitive resume source isn't tracked at all.
- A CI guard rejects regressions of any of the above.

## Non-Goals

- **Git history rewrite to scrub the deleted FUSE-Web image blob.**
  Real concern, but force-pushing main is disruptive and irreversible.
  Documented as a deferred follow-up (v2.13 if you want it).
- **Deleting all `docs/superpowers/`.** The bulk of the design docs
  add real signal to the engineering audience. Scoped scrubs only.
- **Overclaim disclaim** ("sample" labels on output snippets). Lower
  priority; can come later if recruiter pushback surfaces.

## Concrete Changes

### Part A — fix `404.html` paths

Change all 9 absolute paths to relative form. For a static GitHub
Pages subpath site, relative paths are robust to subpath changes
(future custom domain wouldn't need a path rewrite either):

| Before | After |
|---|---|
| `/styles.css` | `styles.css` |
| `/favicon.svg` | `favicon.svg` |
| `/favicon.ico` | `favicon.ico` |
| `/apple-touch-icon.png` | `apple-touch-icon.png` |
| `/assets/fonts/...` | `assets/fonts/...` |
| `/` (nav-brand href) | `./` |
| `/` (home button) | `./` |
| `/#projects` | `./#projects` |
| `/#contact` | `./#contact` |

### Part B — scrub FUSE-Web from public docs

**Delete entirely:**
- `docs/superpowers/specs/2026-05-12-remove-fuse-web.md`
- `docs/superpowers/plans/2026-05-12-remove-fuse-web.md`

These exist solely to document the removal of FUSE-Web and contain
the most egregious leak phrasing ("should not be publicly attributed
to Jake on the site"). Their disappearance is itself the fix.

**Edit (redact FUSE-Web references):**
- `docs/superpowers/specs/2026-05-12-resume-website-design.md`
- `docs/superpowers/specs/2026-05-12-resume-website-v2-design.md`
- `docs/superpowers/plans/2026-05-12-resume-website.md`
- `docs/superpowers/plans/2026-05-12-resume-website-v2.md`
- `docs/superpowers/specs/2026-05-12-shipped-projects-uplift.md`
- `docs/superpowers/plans/2026-05-12-shipped-projects-uplift.md`
- `docs/superpowers/specs/2026-05-12-share-card-polish.md`
- `docs/superpowers/plans/2026-05-12-share-card-polish.md`
- `docs/superpowers/plans/2026-05-12-fonts-and-polish.md`
- `docs/superpowers/plans/2026-05-12-tiny-polish.md`
- `docs/superpowers/specs/2026-05-12-tiny-polish.md`

Strategy: replace "FUSE-Web" / "fuse-web" with a generic placeholder
(`a private client web platform` or `[redacted]` depending on
context). Preserve the narrative shape (so the docs still make sense
as design history) but remove the specific name and any details
that uniquely identify it (insurance-domain, catastrophe-management,
Shield-Restoration-Services, etc.).

### Part C — scrub old-address references

- `docs/superpowers/plans/2026-05-12-resume-refresh.md`
- `docs/superpowers/specs/2026-05-12-resume-polish.md`

Replace `"3 Collinson Blvd, Toronto ON M3H 3B7"` with
`"<full-address>"` placeholder. The narrative point ("we shortened
the address to 'Toronto, ON'") survives without the actual address.

### Part D — untrack `resume-source.docx`

- `git rm --cached resume-source.docx` (keep the local file, untrack
  it in the index)
- Add `resume-source.docx` to `.gitignore`
- Update `scripts/refresh-resume.py` to scrub Office metadata before
  saving: clear `doc.core_properties.author`, `last_modified_by`,
  `comments`, `keywords`, `category`, etc.
- Update `README.md`: the docx is now expected to live locally only;
  `resume.pdf` remains the only committed artifact.

The PDF still gets regenerated and committed (so the live site has
a fresh PDF). The docx becomes a personal-workstation file.

### Part E — `public-safety.yml` GitHub Action

Triggers on push to `main` and on `pull_request`. Runs four checks:

1. **Banned-term grep** across tracked files: `FUSE-Web`,
   `fuse-web`, `Shield-Restoration-Services`, `Collinson`.
2. **404.html absolute-path check**: any `href="/"` or `src="/"` in
   404.html that doesn't start with `/website/` fails. We standardize
   on relative paths, so this catches accidental absolute-path
   regressions.
3. **`resume-source.docx` tracking check**: fails if
   `resume-source.docx` is in the git index.
4. **Banned-term grep on commit message** (best-effort) for the
   current push: catches commit messages that accidentally name the
   redacted project.

The workflow is small (~30 lines) and fast (<10s). It's primarily a
self-defense against future drift.

## File Layout Delta

```
website/
├── 404.html                            MODIFIED (relative paths)
├── .gitignore                          MODIFIED (+ resume-source.docx)
├── README.md                           MODIFIED (docx workflow note)
├── resume-source.docx                  UNTRACKED (still on disk)
├── scripts/refresh-resume.py           MODIFIED (metadata scrub)
├── docs/superpowers/specs/
│   ├── 2026-05-12-remove-fuse-web.md   DELETED
│   ├── 2026-05-12-adversarial-review-fixes.md   NEW (this doc)
│   └── (... 7 other files edited ...)
├── docs/superpowers/plans/
│   ├── 2026-05-12-remove-fuse-web.md   DELETED
│   └── (... 6 other files edited ...)
└── .github/workflows/
    └── public-safety.yml               NEW
```

## Verification

After all changes:
- `git grep -i "fuse-web\|fuse_web\|collinson\|shield-restoration"` → no results
- `git ls-files | grep -i "resume-source"` → no results
- 404 page on `https://jakethehoffer.github.io/website/does-not-exist` renders with the styled boot-prompt layout (not the unstyled fallback)
- 404 page's home/projects/contact buttons land on the right pages
- `public-safety.yml` runs on the next push and passes

## Risks

- **Doc edits could subtly change the design narrative.** Mitigated
  by minimal-edit principle (replace name, preserve structure).
- **Relative paths might break if a deep URL like
  `/website/foo/bar/does-not-exist` 404s.** GitHub Pages serves the
  same `404.html` for all 404s, so relative paths resolve against
  the current URL, not the 404.html's location. Workaround: use
  absolute `/website/...` paths instead of relative, which is what
  GitHub's own docs recommend for project pages. Switching mid-flight
  to that approach if relative-path testing on a deep 404 shows
  breakage.
- **Untracking the docx means resume edits require a local copy.**
  Acceptable trade-off; the README documents the workflow.
- **Banned-term CI could false-positive on legitimate uses.** We
  keep the term list narrow (project-specific identifiers, not
  generic words).

## Success Criteria

- `git grep` for banned terms returns nothing across tracked files.
- 404 page styled correctly on the live URL with working recovery
  links.
- `resume-source.docx` removed from the tracked tree.
- CI safety check active and passing.

## Deferred

- **History rewrite** to scrub the deleted FUSE-Web image blob from
  prior commits. Out of scope for v2.12. If you want this, it's a
  ~10-minute `git filter-repo` operation followed by force-push.
  Disrupts any clones; irreversible. Available as v2.13 on request.
