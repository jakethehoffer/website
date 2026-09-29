"""Check the actual publish folder, including material it must exclude."""

import importlib.util
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import pytest


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("stage_site", ROOT / "scripts/stage-site.py")
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "project"
    for name in stage.PUBLIC_FILES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    return root


def test_stages_current_content_and_excludes_unlisted_material(source):
    for name in ("notes.html", "README.md", "resume-static.yml", "scripts/build.py",
                 "assets/notes.txt", "assets/private.png", "docs/plan.md", ".env"):
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not for the website", encoding="utf-8")
    index = source / "index.html"
    index.write_text(index.read_text(encoding="utf-8") + "<!-- refreshed -->", encoding="utf-8")
    destination = source / "_site"
    stage.stage_site(source, destination)
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()}
    assert actual == set(stage.PUBLIC_FILES)
    for name in actual:
        assert (destination / name).read_bytes() == (source / name).read_bytes()


def test_missing_asset_stops_staging_before_output_is_created(source):
    (source / "resume.pdf").unlink()
    with pytest.raises(ValueError, match="resume.pdf"):
        stage.stage_site(source, source / "_site")
    assert not (source / "_site").exists()


def test_existing_output_is_not_reused_or_deleted(source):
    destination = source / "_site"
    destination.mkdir()
    note = destination / "notes.txt"
    note.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        stage.stage_site(source, destination)
    assert note.read_text(encoding="utf-8") == "keep"


def test_output_stays_inside_project(source):
    for destination in (source, source.parent / "outside"):
        with pytest.raises(ValueError, match="inside the project"):
            stage.stage_site(source, destination)


class PageResources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src", "poster"):
            if key in attrs:
                self.urls.append(attrs[key])
        if tag == "meta" and attrs.get("property") == "og:image":
            self.urls.append(attrs["content"])
        if "srcset" in attrs:
            self.urls.extend(item.strip().split()[0] for item in attrs["srcset"].split(","))


def test_published_pages_and_styles_have_their_local_resources(source):
    destination = source / "_site"
    stage.stage_site(source, destination)
    base = "https://jakethehoffer.github.io/website/"
    for name in stage.PUBLIC_FILES:
        path = destination / name
        if path.suffix == ".html":
            parser = PageResources()
            parser.feed(path.read_text(encoding="utf-8"))
            urls = parser.urls
        elif path.suffix == ".css":
            urls = re.findall(r"url\(['\"]?([^)'\"]+)", path.read_text(encoding="utf-8"))
        else:
            continue
        for url in urls:
            resolved = urlsplit(urljoin(base + name, url))
            if resolved.netloc != urlsplit(base).netloc or not resolved.path.startswith("/website/"):
                continue
            resource = resolved.path.removeprefix("/website/") or "index.html"
            assert (destination / resource).is_file(), f"{name} needs unpublished {resource}"
