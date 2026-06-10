"""refresh-meta.py — opt-in metadata injector for index.html.

For each project in projects.yml with auto_meta: true, fetch
`pushed_at` via `gh api` and rewrite the text content of
<span data-meta="<meta_key>"> in index.html. Also stamps the footer
<span data-meta="last_deployed"> and the sitemap <lastmod> with
today's ISO date.

Failure behavior (deliberate):
- In CI (GITHUB_ACTIONS set), if every gh lookup fails the script
  exits non-zero so the workflow goes red — an expired PAT must be
  noticed within a week, not silently freeze the freshness pills.
- In CI, the footer/sitemap stamps are skipped unless a pill actually
  changed, so the weekly cron no longer creates footer-date-only
  commits (those caused repeated rebase conflicts with local work).
- Locally the stamps always run (a local build precedes a real push,
  i.e. an actual deploy) and lookup failures only warn.

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

    # All lookups failing means the pills silently freeze at their last
    # value — the exact false-freshness problem they exist to solve.
    # In CI that's a red run (expired/missing PAT); locally just warn.
    if attempted > 0 and succeeded == 0:
        msg = (
            f"all {attempted} gh lookup(s) failed — "
            "META_REFRESH_TOKEN expired/missing or gh unauthenticated?"
        )
        if in_ci:
            print(f"\n[FAIL] {msg}")
            sys.exit(1)
        print(f"\n[warn] {msg} Pills keep their last committed value.")

    # Footer + sitemap date stamps. In CI, only stamp when a pill
    # changed — otherwise the weekly cron commits a date-only diff.
    today = datetime.now(timezone.utc).date().isoformat()
    if in_ci and touched == 0:
        print("[skip] last_deployed/sitemap stamps (CI run, no pill changes)")
    else:
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
