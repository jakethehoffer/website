"""refresh-meta.py — opt-in metadata injector for index.html.

For each project in projects.yml with auto_meta: true, fetch
`pushed_at` via `gh api` and rewrite the text content of
<span data-meta="<meta_key>"> in index.html. Also stamps the footer
<span data-meta="last_deployed"> and the sitemap <lastmod> with
today's ISO date.

Nothing here commits. In CI this runs inside deploy.yml, which stages
the mutated working tree into a Pages artifact, so the rewrite lives
exactly as long as the deploy that ships it.

Failure behavior (deliberate):
- In CI (GITHUB_ACTIONS set), ANY failed gh lookup exits non-zero so
  the workflow goes red. The deploy ships whatever this script leaves
  in the working tree, and after a human build the committed pill
  text reads "last commit: today", so one skipped repo would deploy
  that text under a fresh last_deployed stamp: a false claim the
  browser's stale guard cannot see, because the stamp is current.
  This used to trip only when every lookup failed, which covered an
  expired PAT and nothing else (not a renamed repo, and not a PAT
  expiry after one repo went public and the GITHUB_TOKEN fallback
  could still read that one). A red deploy leaves the previous
  deployment serving, so the site stays up while the failure is loud.
- Locally lookup failures only warn, because a local run is usually a
  build ahead of hand-editing rather than an unattended deploy.

The footer/sitemap stamps always run. They used to be skipped in CI
unless a pill had changed, purely to stop the old daily cron from
committing a date-only diff to main; that cron is gone, and a stamp
that names the day the artifact was built is now simply true.

Replaces the older refresh-meta.mjs (Node) — Python lets us share
YAML parsing with the other generators and removes the only Node
dependency.

Usage:
    python scripts/refresh-meta.py

Requires:
    - gh CLI on PATH, authenticated as a user with read access to
      each referenced repo.
    - PyYAML for parsing projects.yml.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
PROJECTS_YML = ROOT / "projects.yml"


def gh_pushed_at(owner: str, name: str) -> str | None:
    """Return the repo's pushed_at ISO timestamp, or None if not readable."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{name}"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
        return json.loads(result.stdout).get("pushed_at")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as err:
        first_line = (
            err.stderr.splitlines()[0] if hasattr(err, "stderr") and err.stderr
            else str(err)
        )
        print(f"[skip] {owner}/{name}: {first_line}")
        return None


def humanize(iso: str | None) -> str | None:
    """Convert an ISO timestamp to 'last commit: <duration>' text."""
    if not iso:
        return None
    then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    days = (now - then).days
    if days <= 0:
        return "last commit: today"
    if days == 1:
        return "last commit: 1d ago"
    if days < 14:
        return f"last commit: {days}d ago"
    if days < 60:
        return f"last commit: {round(days / 7)}w ago"
    return f"last commit: {then.date().isoformat()}"


def replace_meta(html: str, key: str, value: str | None) -> tuple[str, bool, bool]:
    """Replace text inside <span data-meta="{key}">...</span>.

    Returns (new_html, matched, changed).
    - matched: at least one span with that data-meta was found
    - changed: the span's text content actually differed
    """
    if value is None:
        return html, True, False
    pattern = re.compile(
        r'(<span[^>]*data-meta="' + re.escape(key) + r'"[^>]*>)([^<]*)(</span>)'
    )
    matched = False
    changed = False
    def _sub(m: re.Match) -> str:
        nonlocal matched, changed
        matched = True
        if m.group(2) != value:
            changed = True
        return f"{m.group(1)}{value}{m.group(3)}"
    new_html = pattern.sub(_sub, html)
    return new_html, matched, changed


def stamp_sitemap(today: str) -> bool:
    """Set the sitemap <lastmod> to today. Returns True if it changed."""
    if not SITEMAP.exists():
        print("[miss] sitemap.xml not found")
        return False
    xml = SITEMAP.read_text(encoding="utf-8")
    new_xml = re.sub(
        r"<lastmod>[^<]*</lastmod>", f"<lastmod>{today}</lastmod>", xml
    )
    if new_xml == xml:
        print(f"[same] sitemap lastmod = {today} (unchanged)")
        return False
    SITEMAP.write_text(new_xml, encoding="utf-8")
    print(f"[ok]   sitemap lastmod = {today}")
    return True


def main() -> None:
    in_ci = bool(os.environ.get("GITHUB_ACTIONS"))
    projects = yaml.safe_load(PROJECTS_YML.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8")
    touched = 0
    attempted = 0
    succeeded = 0
    failed: list[str] = []

    for proj in projects:
        if not proj.get("auto_meta"):
            continue
        meta_key = proj.get("meta_key")
        if not meta_key:
            continue
        # Parse owner/name from the project's url
        url = proj.get("url") or ""
        m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?", url)
        if not m:
            print(f"[skip] {proj['key']}: url does not match github.com/<owner>/<name>")
            continue
        owner, name = m.group(1), m.group(2)
        attempted += 1
        value = humanize(gh_pushed_at(owner, name))
        if value is None:
            failed.append(f"{owner}/{name}")
            continue
        succeeded += 1
        new_html, matched, changed = replace_meta(html, meta_key, value)
        if not matched:
            print(f"[miss] {meta_key} (no sentinel found in index.html)")
            continue
        if changed:
            touched += 1
            print(f'[ok]   {meta_key} = "{value}"')
            html = new_html
        else:
            print(f'[same] {meta_key} = "{value}" (unchanged)')

    # A failed lookup leaves that pill at whatever text is committed,
    # which after a human build is "last commit: today". Shipping that
    # under a fresh stamp is the one false-freshness shape nothing
    # downstream can catch, so in CI any failure is a red run and the
    # last good deployment keeps serving. Locally, warn and carry on.
    if failed:
        if succeeded == 0:
            why = "META_REFRESH_TOKEN expired/missing or gh unauthenticated?"
        else:
            why = "repo renamed, deleted, or unreadable with this token?"
        msg = (f"{len(failed)} of {attempted} gh lookup(s) failed "
               f"({', '.join(failed)}). {why}")
        if in_ci:
            print(f"\n[FAIL] {msg} Refusing to deploy the committed pill text.")
            sys.exit(1)
        print(f"\n[warn] {msg} Those pills keep their last committed value.")

    # Footer + sitemap date stamps. Always applied: this run feeds a
    # Pages artifact (or a local build), never a commit, so there is no
    # date-only diff to avoid any more.
    today = datetime.now(timezone.utc).date().isoformat()
    value = f"last_deployed: {today}"
    new_html, matched, changed = replace_meta(html, "last_deployed", value)
    if not matched:
        print("[miss] last_deployed (no sentinel found in index.html)")
    elif changed:
        touched += 1
        print(f"[ok]   last_deployed = {today}")
        html = new_html
    else:
        print(f"[same] last_deployed = {today} (unchanged)")
    stamp_sitemap(today)

    if touched > 0:
        INDEX.write_text(html, encoding="utf-8")
        print(f"\nWrote {touched} update(s) to {INDEX}.")
    else:
        print("\nNo updates written.")


if __name__ == "__main__":
    main()
