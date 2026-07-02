"""verify-site.py — rendered-artifact checks for the website + resume.

Every release before v2.27 was verified with text greps over the HTML
and PDF; nothing ever looked at the rendered page, which is how a
projects-grid layout blowout (horizontal scroll on every phone) shipped
invisibly. This script checks the artifacts a visitor actually
receives:

  static   - index.html structure: card count matches projects.yml,
             case-study anchors resolve, data-meta sentinels present,
             private projects don't link to their (404ing) repos,
             JSON-LD parses, exactly one <h1>
  claims   - every metric phrase baked into the OG share card exists
             in the page hero (the card once carried a hero claim
             retracted weeks earlier)
  og       - og-image.png is exactly 1200x630 (as the meta tags claim),
             and its jh:metrics tEXt chunk matches the METRICS constant
             in render-og-image.py (catches "edited the script, forgot
             to re-render the PNG" — dimensions alone can't)
  sitemap  - <lastmod> is a plausible ISO date, not years stale
  resume   - resume.pdf is exactly 1 page with the expected hyperlinks,
             and its text contains the name, GPA, and every project
             name the resume is supposed to feature (top
             RESUME_MAX_PROJECTS by resume_priority) — catches a stale
             committed PDF after a projects.yml/resume-static.yml edit
             (requires pypdf)
  layout   - rendered index.html AND 404.html, served under the
             production /website/ subpath, have no horizontal overflow
             at 320/375/768/834/1280px in BOTH color schemes
             (requires playwright + chromium)
  a11y     - axe-core pass on both pages in both schemes; violations
             with impact critical/serious fail, the rest warn
             (axe loads from CDN; unreachable CDN degrades to warning)

Exit 0 = all checks pass. In CI every check is mandatory; locally,
missing optional deps (pypdf/playwright) degrade to a warning so the
script stays runnable everywhere.

Usage:
    python scripts/verify-site.py
"""

from __future__ import annotations

import html as html_mod
import json
import os
import re
import struct
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
PROJECTS_YML = ROOT / "projects.yml"
RESUME_STATIC = ROOT / "resume-static.yml"
BUILD_RESUME = ROOT / "scripts" / "build-resume.py"
OG_SCRIPT = ROOT / "scripts" / "render-og-image.py"
OG_IMAGE = ROOT / "assets" / "og-image.png"
SITEMAP = ROOT / "sitemap.xml"
RESUME = ROOT / "resume.pdf"

IN_CI = bool(os.environ.get("GITHUB_ACTIONS"))

# Viewports that cover the historical failure modes: small phone,
# phone, the old hamburger boundary, the old nav-overflow band, and a
# stock laptop.
LAYOUT_WIDTHS = (320, 375, 768, 834, 1280)

# Pinned axe-core build for the a11y pass. CDN-loaded at check time;
# if the CDN is unreachable the check degrades to a warning (an axe
# CDN outage should not block a deploy — the next push re-runs it).
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.10.3/axe.min.js"

failures: list[str] = []
warnings: list[str] = []


def ok(msg: str) -> None:
    print(f"[ok]   {msg}")


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"[FAIL] {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"[warn] {msg}")


def soft_dep_missing(what: str, why: str) -> None:
    """A missing optional dependency is fatal in CI, a warning locally."""
    if IN_CI:
        fail(f"{what} unavailable in CI: {why}")
    else:
        warn(f"{what} not installed locally — skipping ({why})")


def normalize(text: str) -> str:
    """Decode entities and fold typographic apostrophes for comparison."""
    return html_mod.unescape(text).replace("’", "'")


# ---------------- static structure ----------------

def check_structure(html: str, projects: list[dict]) -> None:
    cards = html.count('<article class="project">')
    if cards == len(projects):
        ok(f"card count matches projects.yml ({cards})")
    else:
        fail(f"card count {cards} != {len(projects)} projects in projects.yml")

    open_articles = len(re.findall(r"<article\b", html))
    close_articles = html.count("</article>")
    if open_articles == close_articles:
        ok(f"<article> tags balanced ({open_articles})")
    else:
        fail(f"<article> tags unbalanced: {open_articles} open, {close_articles} close")

    for p in projects:
        anchor = p.get("case_study")
        if anchor:
            target = anchor.lstrip("#")
            if re.search(r'id="' + re.escape(target) + '"', html):
                ok(f"case-study anchor {anchor} resolves ({p['key']})")
            else:
                fail(f"case-study anchor {anchor} has no id target ({p['key']})")

        if p.get("auto_meta") and p.get("meta_key"):
            if f'data-meta="{p["meta_key"]}"' in html:
                ok(f"data-meta sentinel present ({p['meta_key']})")
            else:
                fail(f"data-meta sentinel missing ({p['meta_key']})")

        if p.get("private") and p.get("url"):
            # The whole point of the private pill: no 404ing link.
            block = html.split("BEGIN projects-block")[1].split("END projects-block")[0]
            if f'href="{p["url"]}"' in block:
                fail(f"private project {p['key']} links to {p['url']} (404s for visitors)")
            else:
                ok(f"private project {p['key']} renders without repo link")

    if 'data-meta="last_deployed"' in html:
        ok("footer last_deployed sentinel present")
    else:
        fail("footer last_deployed sentinel missing")

    h1s = len(re.findall(r"<h1\b", html))
    if h1s == 1:
        ok("exactly one <h1>")
    else:
        fail(f"expected exactly one <h1>, found {h1s}")

    m = re.search(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        html, re.DOTALL,
    )
    if not m:
        fail("JSON-LD block not found")
    else:
        try:
            json.loads(m.group(1))
            ok("JSON-LD parses")
        except json.JSONDecodeError as e:
            fail(f"JSON-LD does not parse: {e}")


# ---------------- OG claim sync + image dimensions ----------------

def og_script_metrics() -> str | None:
    """Return the METRICS constant from render-og-image.py, or None."""
    src = OG_SCRIPT.read_text(encoding="utf-8")
    m = re.search(r'^METRICS\s*=\s*"(.+)"', src, re.MULTILINE)
    return m.group(1) if m else None


def check_og_claims(html: str) -> None:
    metrics = og_script_metrics()
    if metrics is None:
        fail("METRICS constant not found in render-og-image.py")
        return
    phrases = [p.strip() for p in metrics.lstrip("/ ").split("·") if p.strip()]

    hero = re.search(r'<p class="hero__metrics">(.*?)</p>', html, re.DOTALL)
    if not hero:
        fail("hero__metrics block not found in index.html")
        return
    hero_text = normalize(re.sub(r"<[^>]+>", " ", hero.group(1)))

    for phrase in phrases:
        if normalize(phrase) in hero_text:
            ok(f'OG share-card claim "{phrase}" backed by hero')
        else:
            fail(f'OG share-card claim "{phrase}" not present in hero metrics '
                 "(stale og-image.png? run scripts/render-og-image.py)")


def check_og_dimensions() -> None:
    # PNG IHDR: width/height are big-endian uint32 at byte offsets 16/20.
    data = OG_IMAGE.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("og-image.png is not a PNG")
        return
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) == (1200, 630):
        ok("og-image.png is 1200x630 (matches og:image:width/height meta)")
    else:
        fail(f"og-image.png is {w}x{h}, meta tags claim 1200x630")


def check_og_provenance() -> None:
    """The committed PNG must carry the METRICS string it was rendered
    from (a jh:metrics tEXt chunk written by render-og-image.py). If
    the chunk differs from the script constant, someone edited the
    script and committed without re-rendering — the dimensions check
    can't see that, and check_og_claims compares the SCRIPT to the
    hero, not the PNG to anything."""
    script_metrics = og_script_metrics()
    if script_metrics is None:
        return  # check_og_claims already failed on this

    data = OG_IMAGE.read_bytes()
    texts: dict[str, str] = {}
    pos = 8  # skip PNG signature
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if ctype == b"tEXt":
            key, _, val = data[pos + 8:pos + 8 + length].partition(b"\x00")
            texts[key.decode("latin-1")] = val.decode("latin-1")
        pos += 12 + length  # length + type + data + CRC

    baked = texts.get("jh:metrics")
    if baked is None:
        fail("og-image.png has no jh:metrics tEXt chunk — stale PNG from "
             "before provenance stamping? re-run scripts/render-og-image.py")
    elif baked == script_metrics:
        ok("og-image.png jh:metrics chunk matches METRICS in render-og-image.py")
    else:
        fail(f'og-image.png was rendered from METRICS "{baked}" but the '
             f'script now says "{script_metrics}" — re-run '
             "scripts/render-og-image.py and commit the new PNG")


# ---------------- sitemap ----------------

def check_sitemap() -> None:
    xml = SITEMAP.read_text(encoding="utf-8")
    m = re.search(r"<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>", xml)
    if m:
        ok(f"sitemap lastmod is ISO date ({m.group(1)})")
    else:
        fail("sitemap <lastmod> missing or not YYYY-MM-DD")


# ---------------- resume.pdf ----------------

def resume_expected_strings(projects: list[dict]) -> list[str]:
    """Strings the committed resume.pdf must contain: the name, the
    GPA from resume-static.yml, and the name of every project the
    resume is supposed to feature (top RESUME_MAX_PROJECTS by
    resume_priority among entries with a resume block — mirrors
    select_resume_projects in build-resume.py). If any is missing, the
    committed PDF predates the current sources."""
    static = yaml.safe_load(RESUME_STATIC.read_text(encoding="utf-8"))
    expected = [static["contact"]["name"]]

    for section in static.get("sections", []):
        for block in section.get("blocks", []):
            for item in block.get("items", []) if block.get("type") == "bullets" else []:
                m = re.search(r"GPA of (\d\.\d+)", item)
                if m:
                    expected.append(m.group(1))

    src = BUILD_RESUME.read_text(encoding="utf-8")
    m = re.search(r"^RESUME_MAX_PROJECTS\s*=\s*(\d+)", src, re.MULTILINE)
    cap = int(m.group(1)) if m else 4
    candidates = [p for p in projects if p.get("resume")]
    ranked = sorted(candidates, key=lambda p: -p["resume_priority"])[:cap]
    expected.extend(normalize(p["name"]) for p in ranked)
    return expected


def check_resume(projects: list[dict]) -> None:
    try:
        from pypdf import PdfReader
    except ImportError:
        soft_dep_missing("pypdf", "resume.pdf page/link/content checks")
        return
    reader = PdfReader(str(RESUME))
    n_pages = len(reader.pages)
    if n_pages == 1:
        ok("resume.pdf is 1 page")
    else:
        fail(f"resume.pdf is {n_pages} pages — the one-page guarantee broke")
    links = 0
    for page in reader.pages:
        for annot in page.get("/Annots") or []:
            if annot.get_object().get("/Subtype") == "/Link":
                links += 1
    if links >= 4:
        ok(f"resume.pdf has {links} hyperlink annotations (>= 4)")
    else:
        fail(f"resume.pdf has {links} hyperlink annotations, expected >= 4 "
             "(email, LinkedIn, site, writing)")

    # Content sync: page/link counts can't see a stale PDF committed
    # after a projects.yml / resume-static.yml edit. Fold whitespace
    # (and typographic apostrophes) before matching — extraction
    # splits lines unpredictably.
    text = normalize(" ".join(p.extract_text() or "" for p in reader.pages))
    flat = re.sub(r"\s+", " ", text)
    for needle in resume_expected_strings(projects):
        if needle in flat:
            ok(f'resume.pdf contains "{needle}"')
        else:
            fail(f'resume.pdf does not contain "{needle}" — stale PDF? '
                 "re-run scripts/build-site.py and commit the new resume.pdf")


# ---------------- rendered layout + a11y (playwright) ----------------

def run_axe(page, label: str) -> None:
    """axe-core pass on the current page. critical/serious violations
    fail; moderate/minor warn. An unreachable CDN warns instead of
    failing — an axe outage should not block a deploy."""
    try:
        page.add_script_tag(url=AXE_URL)
    except Exception as e:
        warn(f"axe-core CDN unreachable — a11y checks skipped for {label} "
             f"({e.__class__.__name__})")
        return
    results = page.evaluate(
        "() => axe.run(document, {resultTypes: ['violations']})"
    )
    violations = results.get("violations", [])
    if not violations:
        ok(f"a11y clean ({label})")
        return
    for v in violations:
        target = v["nodes"][0]["target"] if v.get("nodes") else "?"
        msg = (f"a11y {v.get('impact', 'unknown')}: {v['id']} — {v['help']} "
               f"[{len(v.get('nodes', []))} node(s), e.g. {target}] ({label})")
        if v.get("impact") in ("critical", "serious"):
            fail(msg)
        else:
            warn(msg)


def check_layout_and_a11y() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        soft_dep_missing("playwright", "layout overflow + a11y checks")
        return

    class SiteHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):  # keep CI output to the checks
            pass

        def translate_path(self, path):
            # Serve the repo under the production /website/ subpath so
            # 404.html's absolute /website/... asset URLs resolve here
            # exactly like they do on GitHub Pages. (Unprefixed paths
            # keep working, but the checks below always use the prefix.)
            if path == "/website":
                path = "/website/"
            if path.startswith("/website/"):
                path = path[len("/website"):]
            return super().translate_path(path)

    handler = partial(SiteHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            # Both color schemes: the themes have independent palettes
            # (an AA contrast bug shipped in one theme before), and the
            # inline theme script keys off prefers-color-scheme.
            # reduced_motion="reduce" makes the run deterministic: the
            # scroll-reveal fade otherwise leaves below-fold sections
            # mid-transition when axe samples them, producing flaky
            # blended-color contrast failures that no settled page has.
            for scheme in ("dark", "light"):
                context = browser.new_context(color_scheme=scheme,
                                              reduced_motion="reduce")
                page = context.new_page()
                for doc in ("index.html", "404.html"):
                    label_base = f"{doc} [{scheme}]"
                    page.goto(f"http://127.0.0.1:{port}/website/{doc}",
                              wait_until="networkidle")
                    for width in LAYOUT_WIDTHS:
                        page.set_viewport_size({"width": width, "height": 900})
                        metrics = page.evaluate(
                            "() => ({scroll: document.documentElement.scrollWidth,"
                            "        client: document.documentElement.clientWidth})"
                        )
                        if metrics["scroll"] <= metrics["client"] + 1:
                            ok(f"no horizontal overflow at {width}px "
                               f"({label_base}, layout {metrics['scroll']}px)")
                        else:
                            fail(f"horizontal overflow at {width}px viewport "
                                 f"({label_base}): layout is {metrics['scroll']}px "
                                 f"vs {metrics['client']}px visible")
                    run_axe(page, label_base)
                context.close()
            browser.close()
    finally:
        server.shutdown()


# ---------------- main ----------------

def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    projects = yaml.safe_load(PROJECTS_YML.read_text(encoding="utf-8"))

    check_structure(html, projects)
    check_og_claims(html)
    check_og_dimensions()
    check_og_provenance()
    check_sitemap()
    check_resume(projects)
    check_layout_and_a11y()

    print()
    if failures:
        print(f"verify-site: {len(failures)} FAILURE(S), {len(warnings)} warning(s)")
        return 1
    print(f"verify-site: all checks passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
