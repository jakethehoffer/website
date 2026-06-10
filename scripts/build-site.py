"""build-site.py — orchestrator that runs all four generators.

After editing projects.yml (or resume-static.yml), run this to regenerate:
- index.html projects block (generate-cards.py)
- resume-source.docx, built from scratch (build-resume.py)
- og-image.png + favicons (render-og-image.py; claims stay in sync
  with the hero — a share card once carried a hero claim retracted
  weeks earlier because this step wasn't part of the build)
- index.html data-meta sentinels and footer last_deployed (refresh-meta.py)

Then run the documented LibreOffice command to regenerate resume.pdf
from resume-source.docx.

Usage:
    python scripts/build-site.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script_name: str) -> None:
    print(f"\n=== {script_name} ===")
    result = subprocess.run([sys.executable, str(SCRIPTS / script_name)])
    if result.returncode != 0:
        raise SystemExit(f"{script_name} failed with exit {result.returncode}")


if __name__ == "__main__":
    run("generate-cards.py")
    run("build-resume.py")
    run("render-og-image.py")
    run("refresh-meta.py")
    print(
        "\nDone. resume-source.docx updated; regenerate resume.pdf via:\n"
        '  "C:/Program Files/LibreOffice/program/soffice.exe" '
        "--headless --convert-to pdf --outdir . resume-source.docx\n"
        "  mv resume-source.pdf resume.pdf"
    )
