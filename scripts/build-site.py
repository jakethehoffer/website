"""build-site.py — orchestrator that runs all four generators, then
rebuilds resume.pdf via LibreOffice when it's installed.

Refuses to run on a checkout that's behind origin (see
check_not_behind). The daily cron pushes to main, so a clone drifts
stale within days, and every generator here rewrites tracked files.

After editing projects.yml (or resume-static.yml), run this to regenerate:
- index.html projects block (generate-cards.py)
- resume-source.docx, built from scratch (build-resume.py)
- og-image.png + favicons (render-og-image.py; claims stay in sync
  with the hero — a share card once carried a hero claim retracted
  weeks earlier because this step wasn't part of the build)
- index.html data-meta sentinels and footer last_deployed (refresh-meta.py)
- resume.pdf (soffice --headless; skipped with instructions if
  LibreOffice isn't on this machine). Automated because the manual
  tail of the pipeline was the one place a stale PDF could ship —
  verify-site.py now also asserts PDF content against the sources.

Usage:
    python scripts/build-site.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

MANUAL_PDF_CMD = (
    '  "C:/Program Files/LibreOffice/program/soffice.exe" '
    "--headless --convert-to pdf --outdir . resume-source.docx\n"
    "  mv resume-source.pdf resume.pdf"
)


def git(*args: str, timeout: int = 25) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, timeout=timeout,
    )


def check_not_behind() -> None:
    """Refuse to build on a checkout that is behind its upstream.

    The refresh-meta cron pushes to main daily, so a local clone goes
    stale within days while looking perfectly healthy. Every generator
    below rewrites tracked files, so a stale base regenerates from old
    inputs and guarantees a conflict on push.

    The sharper reason this exists: a stale checkout makes old local
    values look like live-site bugs. A freshness pill read from an
    8-week-old clone was once reported as a frozen cron, and the cron
    had been correct the whole time.

    Skipped in CI (always a fresh checkout). Set WEBSITE_ALLOW_STALE=1
    to override deliberately.
    """
    if os.environ.get("GITHUB_ACTIONS"):
        return
    if os.environ.get("WEBSITE_ALLOW_STALE"):
        print("[skip] upstream freshness check (WEBSITE_ALLOW_STALE set)")
        return
    try:
        upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        if upstream.returncode != 0:
            print("[skip] upstream freshness check (no upstream branch)")
            return
        tracking = upstream.stdout.strip()
        if git("fetch", "--quiet").returncode != 0:
            print("[warn] could not reach the remote; comparing against the last fetch")
        behind = git("rev-list", "--count", "HEAD..@{u}")
    except (subprocess.TimeoutExpired, OSError) as err:
        print(f"[warn] upstream freshness check skipped ({type(err).__name__})")
        return
    count = behind.stdout.strip()
    if behind.returncode != 0 or not count.isdigit():
        print("[warn] upstream freshness check inconclusive")
        return
    if int(count) > 0:
        raise SystemExit(
            f"[FAIL] this checkout is {count} commit(s) behind {tracking}.\n"
            "       Run 'git pull --rebase' before building. A stale base\n"
            "       regenerates tracked files from old inputs and makes stale\n"
            "       local values look like live-site bugs.\n"
            "       Set WEBSITE_ALLOW_STALE=1 to override."
        )
    print(f"[ok]   checkout is up to date with {tracking}")


def run(script_name: str) -> None:
    print(f"\n=== {script_name} ===")
    result = subprocess.run([sys.executable, str(SCRIPTS / script_name)])
    if result.returncode != 0:
        raise SystemExit(f"{script_name} failed with exit {result.returncode}")


def find_soffice() -> str | None:
    on_path = shutil.which("soffice")
    if on_path:
        return on_path
    windows_default = Path("C:/Program Files/LibreOffice/program/soffice.exe")
    return str(windows_default) if windows_default.exists() else None


def build_pdf() -> None:
    soffice = find_soffice()
    if soffice is None:
        print(
            "\nLibreOffice not found — regenerate resume.pdf manually:\n"
            + MANUAL_PDF_CMD
        )
        return
    print("\n=== resume.pdf (soffice) ===")
    intermediate = ROOT / "resume-source.pdf"
    intermediate.unlink(missing_ok=True)
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(ROOT), str(ROOT / "resume-source.docx")]
    )
    if result.returncode != 0:
        raise SystemExit(f"soffice failed with exit {result.returncode}")
    # soffice can return before the PDF lands on disk — wait for the
    # file to appear and its size to hold still before renaming.
    last_size = -1
    for _ in range(60):
        if intermediate.exists():
            size = intermediate.stat().st_size
            if size > 0 and size == last_size:
                break
            last_size = size
        time.sleep(0.5)
    else:
        raise SystemExit(
            "resume-source.pdf never appeared/stabilized after soffice — "
            "run the manual command:\n" + MANUAL_PDF_CMD
        )
    intermediate.replace(ROOT / "resume.pdf")
    size = (ROOT / "resume.pdf").stat().st_size
    print(f"[ok]   resume.pdf rebuilt ({size:,} bytes)")


if __name__ == "__main__":
    check_not_behind()
    run("generate-cards.py")
    run("build-resume.py")
    run("render-og-image.py")
    run("refresh-meta.py")
    build_pdf()
    print("\nDone.")
