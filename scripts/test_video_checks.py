"""Prove the publication video check rejects real browser regressions."""

import importlib.util
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Error as PlaywrightError, sync_playwright


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("verify_site_video", ROOT / "scripts/verify-site.py")
vs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vs)
PROJECT = next(p for p in yaml.safe_load((ROOT / "projects.yml").read_text(encoding="utf-8"))
               if p["key"] == "cockpit")


@pytest.fixture(scope="module")
def movie_site():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(vs.SitePreviewHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                yield browser, f"http://127.0.0.1:{server.server_port}/website/index.html"
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture
def javascript_enabled():
    return True


@pytest.fixture
def video_page(movie_site, javascript_enabled):
    browser, url = movie_site
    context = browser.new_context(viewport={"width": 390, "height": 844},
                                  reduced_motion="reduce", java_script_enabled=javascript_enabled)
    try:
        yield context.new_page(), url
    finally:
        context.close()


@pytest.mark.parametrize("javascript_enabled", [True, False], ids=["scripts-on", "scripts-off"])
def test_published_movie_path_passes(video_page, javascript_enabled):
    page, url = video_page
    vs.check_video_page(page, url, PROJECT, javascript_enabled=javascript_enabled)


def test_preview_serves_real_movie_byte_ranges(video_page):
    page, url = video_page
    movie_url = url.replace("index.html", PROJECT["video"]["src"])
    content = (ROOT / PROJECT["video"]["src"]).read_bytes()
    for header, start, end in (("bytes=0-1023", 0, 1023),
                               ("bytes=4096-", 4096, len(content) - 1),
                               ("bytes=-512", len(content) - 512, len(content) - 1)):
        response = page.request.get(movie_url, headers={"Range": header})
        assert response.status == 206
        assert response.headers["content-range"] == f"bytes {start}-{end}/{len(content)}"
        assert response.body() == content[start:end + 1]
    for header in ("bytes=bad", "bytes=-", "bytes=-0", "bytes=20-10", f"bytes={len(content)}-"):
        response = page.request.get(movie_url, headers={"Range": header})
        assert response.status == 416
        assert response.body() == b""


@pytest.mark.parametrize(("old", "new", "message"), [
    ('preload="none"', 'preload="auto"', "downloads before Play"),
    ('<video controls', '<video autoplay controls', "starts without Play"),
    ('<video controls', '<video', "native movie controls"),
])
def test_unsafe_player_attributes_are_rejected(video_page, old, new, message):
    page, url = video_page
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert old in html
    page.route("**/index.html", lambda route: route.fulfill(
        status=200, content_type="text/html", body=html.replace(old, new, 1)))
    with pytest.raises(AssertionError, match=message):
        vs.check_video_page(page, url, PROJECT)


@pytest.mark.parametrize("javascript_enabled", [True, False], ids=["scripts-on", "scripts-off"])
def test_missing_movie_is_rejected(video_page, javascript_enabled):
    page, url = video_page
    page.route("**/*.mp4", lambda route: route.fulfill(status=404, body="Missing movie"))
    with pytest.raises(PlaywrightError, match="movie did not start after Play"):
        vs.check_video_page(page, url, PROJECT, javascript_enabled=javascript_enabled)


def test_hidden_movie_without_pause_is_rejected(video_page):
    page, url = video_page
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    old = 'if (card.hidden) card.querySelectorAll("video").forEach(video => video.pause());'
    assert old in script
    page.route("**/script.js*", lambda route: route.fulfill(
        status=200, content_type="application/javascript", body=script.replace(old, "")))
    with pytest.raises(AssertionError, match="hidden movie keeps playing"):
        vs.check_video_page(page, url, PROJECT)
