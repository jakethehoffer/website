"""Copy only finished public website files into a fresh publish directory."""

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# Add a file deliberately when the website needs it. Do not copy directories
# wholesale: source, tests and working notes are not website assets.
PUBLIC_FILES = (
    "index.html",
    "404.html",
    "styles.css",
    "script.js",
    "resume.pdf",
    "robots.txt",
    "sitemap.xml",
    "googlea7123ac853be3d73.html",
    "favicon.svg",
    "favicon.ico",
    "apple-touch-icon.png",
    "assets/og-image.png",
    "assets/fonts/jetbrains-mono-variable.woff2",
    "assets/projects/mega-ttt.webp",
    "assets/projects/walking-jumping-cm.png",
    "assets/projects/workshop-arcade.jpg",
    "assets/projects/cockpit-film.mp4",
    "assets/projects/cockpit-film.jpg",
)


def stage_site(root: Path, destination: Path) -> None:
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or not destination.is_relative_to(root):
        raise ValueError("Publish directory must be a separate folder inside the project")
    if destination.exists():
        raise FileExistsError("Publish directory already exists; choose a fresh folder")

    # Check every input before creating output. Refuse redirects through links
    # so an asset cannot silently include material outside the public file list.
    for name in PUBLIC_FILES:
        source = root / name
        if source.resolve() != source or not source.is_file():
            raise ValueError(f"Missing or linked public file: {name}")

    destination.mkdir(parents=True)
    for name in PUBLIC_FILES:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="_site", help="New output folder inside the project")
    args = parser.parse_args()
    destination = ROOT / args.output
    stage_site(ROOT, destination)
    print(f"Staged {len(PUBLIC_FILES)} public website files in {destination}")
    for name in PUBLIC_FILES:
        print(name)


if __name__ == "__main__":
    main()
