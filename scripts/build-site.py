"""build-site.py — orchestrator that runs all four generators, then
rebuilds resume.pdf via LibreOffice when it's installed.

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
    run("generate-cards.py")
    run("build-resume.py")
    run("render-og-image.py")
    run("refresh-meta.py")
    build_pdf()
    print("\nDone.")
