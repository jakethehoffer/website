"""refresh-meta.py — opt-in metadata injector for index.html.

For each project in projects.yml with auto_meta: true, fetch
`pushed_at` via `gh api` and rewrite the text content of
<span data-meta="<meta_key>"> in index.html. Also stamps the footer
<span data-meta="last_deployed"> with today's ISO date.

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
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
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


def main() -> None:
    projects = yaml.safe_load(PROJECTS_YML.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8")
    touched = 0

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
        value = humanize(gh_pushed_at(owner, name))
        if value is None:
            continue
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

    # Footer last_deployed stamp — always set to today.
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

    if touched > 0:
        INDEX.write_text(html, encoding="utf-8")
        print(f"\nWrote {touched} update(s) to {INDEX}.")
    else:
        print("\nNo updates written.")


if __name__ == "__main__":
    main()
