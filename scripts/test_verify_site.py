"""Tests for scripts/verify-site.py: each check must still bite.

The checks in verify-site.py were each proven with a throwaway mutation
harness at the time they were written, then the harness was discarded.
This file keeps those mutations. Every test plants one known defect in
a scratch copy of the tree and asserts the check reports it, so a
refactor that quietly neuters a check goes red here instead of staying
green until the next incident.

No browser: the playwright checks are exercised by the real run in CI.
Only the threshold-band branch of the stale guard is covered here,
because it fails before a browser is ever touched.

Run:  python -m pytest scripts -q
"""

from __future__ import annotations

import importlib.util
import shutil
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vs = load_script("verify-site")

COPIED = ("index.html", "404.html", "projects.yml", "resume-static.yml",
          "sitemap.xml", "script.js")


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A scratch copy of the text sources, with verify-site pointed at it.

    resume.pdf, og-image.png and the generator scripts stay on the real
    tree: they are read, never mutated, by anything here."""
    for name in COPIED:
        shutil.copy(ROOT / name, tmp_path / name)
    monkeypatch.setattr(vs, "ROOT", tmp_path)
    monkeypatch.setattr(vs, "INDEX", tmp_path / "index.html")
    monkeypatch.setattr(vs, "PROJECTS_YML", tmp_path / "projects.yml")
    monkeypatch.setattr(vs, "RESUME_STATIC", tmp_path / "resume-static.yml")
    monkeypatch.setattr(vs, "SITEMAP", tmp_path / "sitemap.xml")
    monkeypatch.setattr(vs, "SCRIPT_JS", tmp_path / "script.js")
    vs.failures.clear()
    vs.warnings.clear()
    return tmp_path


def mutate(path: Path, old: str, new: str, count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"mutation target not found in {path.name}: {old!r}"
    path.write_text(text.replace(old, new, count), encoding="utf-8")


def html(tree: Path) -> str:
    return (tree / "index.html").read_text(encoding="utf-8")


def projects(tree: Path):
    return vs.yaml.safe_load((tree / "projects.yml").read_text(encoding="utf-8"))


def failed_with(fragment: str) -> bool:
    return any(fragment in f for f in vs.failures)


def warned_with(fragment: str) -> bool:
    return any(fragment in w for w in vs.warnings)


# ---------------- baseline ----------------

def test_unmutated_tree_passes_every_non_browser_check(tree):
    vs.check_structure(html(tree), projects(tree))
    vs.check_og_claims(html(tree))
    vs.check_og_dimensions()
    vs.check_og_provenance()
    vs.check_sitemap()
    vs.check_expiring_claims()
    vs.check_cross_repo_claims(projects(tree))
    vs.check_resume(projects(tree))
    vs.check_padded_metrics()
    vs.check_voice()
    assert vs.failures == []


# ---------------- structure ----------------

def test_missing_card_fails(tree):
    mutate(tree / "index.html", '<article class="project">', "<article>")
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("card count")


def test_case_study_anchor_without_target_fails(tree):
    mutate(tree / "index.html", 'id="case-study-arb"', 'id="case-study-arb-moved"')
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("case-study anchor #case-study-arb")


def test_private_project_with_repo_link_fails(tree):
    mutate(tree / "index.html",
           'trader <span class="project__private">private</span>',
           '<a href="https://github.com/jakethehoffer/trader">trader</a>')
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("private project trader links")


def test_second_h1_fails(tree):
    mutate(tree / "index.html", "<h2>What I work on</h2>", "<h1>What I work on</h1>")
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("exactly one <h1>")


def test_broken_json_ld_fails(tree):
    mutate(tree / "index.html", '"@type": "Person",', '"@type": "Person"')
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("JSON-LD does not parse")


def test_missing_last_deployed_sentinel_fails(tree):
    mutate(tree / "index.html", 'data-meta="last_deployed"', 'data-meta="deployed"')
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("last_deployed sentinel missing")


def test_resume_link_without_download_filename_fails(tree):
    mutate(tree / "index.html", 'href="resume.pdf" download="Jake-Hoffman-Resume.pdf"',
           'href="resume.pdf" download')
    vs.check_structure(html(tree), projects(tree))
    assert failed_with("download")


# ---------------- OG share card ----------------

def test_og_claim_missing_from_hero_fails(tree, monkeypatch):
    monkeypatch.setattr(vs, "og_script_metrics", lambda: "//  99 dragons tamed")
    vs.check_og_claims(html(tree))
    assert failed_with('"99 dragons tamed" not present in hero')


# ---------------- calendar claims ----------------

@pytest.mark.parametrize("today, year", [
    (date(2023, 9, 1), 1),
    (date(2024, 8, 31), 1),
    (date(2024, 9, 1), 2),
    (date(2026, 9, 10), 4),
    (date(2027, 8, 31), 4),
    (date(2027, 9, 1), 5),
])
def test_academic_year_rolls_over_in_september(today, year):
    assert vs.academic_year(today) == year


def test_wrong_year_of_study_fails(tree):
    correct = vs.academic_year(date.today())
    wrong = vs.ORDINALS[correct - 1]
    mutate(tree / "resume-static.yml", f"{vs.ORDINALS[correct]} Year at", f"{wrong} Year at")
    vs.check_expiring_claims()
    assert failed_with(f'says "{wrong} Year"')


# ---------------- cross-repo claims ----------------

# One claim that names every private project, so the date tests below
# exercise only the timer and not the coverage rule.
EVERY_PRIVATE_PROJECT = "trader, arbitrage, tax-rebalance and market-bot still hum"


def test_cross_repo_claim_past_stale_days_fails(tree, monkeypatch):
    old = date.today() - timedelta(days=vs.CLAIM_STALE_DAYS)
    monkeypatch.setattr(vs, "CROSS_REPO_CLAIMS",
                        ((EVERY_PRIVATE_PROJECT, "its log", old),))
    vs.check_cross_repo_claims(projects(tree))
    assert failed_with("cross-repo claim unverified")


def test_cross_repo_claim_past_warn_days_warns(tree, monkeypatch):
    aging = date.today() - timedelta(days=vs.CLAIM_WARN_DAYS)
    monkeypatch.setattr(vs, "CROSS_REPO_CLAIMS",
                        ((EVERY_PRIVATE_PROJECT, "its log", aging),))
    vs.check_cross_repo_claims(projects(tree))
    assert warned_with("due for re-check")
    assert not failed_with("cross-repo")


def test_private_project_with_no_dated_claim_fails(tree):
    """A visitor cannot open a private repo, so every private project
    needs at least one claim on the timer. market-bot had none, and its
    'runs unattended' outlived the collector by three months."""
    mutate(tree / "projects.yml", "- key: market-bot\n", "- key: ghost-project\n")
    vs.check_cross_repo_claims(projects(tree))
    assert failed_with("ghost-project")


# ---------------- padded metrics ----------------

@pytest.mark.parametrize("sneak", [
    "shipped 4,100+ commits since spring",
    "<strong>4,100+</strong> commits of work",
    "about 900 commits",
    "5,700+ total commits across both",
    "1,600+ combined commits",
])
def test_commit_count_in_page_fails(tree, sneak):
    mutate(tree / "index.html", "<h2>What I work on</h2>", f"<h2>What I work on</h2><p>{sneak}</p>")
    vs.check_padded_metrics()
    assert failed_with("padded metric in index.html")


def test_commit_count_in_yaml_prose_fails(tree):
    mutate(tree / "projects.yml", 'what: "24/7 AI swing-trading agent',
           'what: "2,000+ commits. 24/7 AI swing-trading agent')
    vs.check_padded_metrics()
    assert failed_with("padded metric in projects.yml")


@pytest.mark.parametrize("legit", [
    "last commit: today",
    "from first commit to a verdict in three weeks",
    "117 tests and counting",
])
def test_legitimate_commit_phrasing_passes(tree, legit):
    mutate(tree / "index.html", "<h2>What I work on</h2>", f"<h2>What I work on</h2><p>{legit}</p>")
    vs.check_padded_metrics()
    assert not failed_with("padded metric")


# ---------------- voice ----------------

def test_literal_em_dash_fails(tree):
    mutate(tree / "index.html", "<h2>What I work on</h2>", "<h2>What I work — on</h2>")
    vs.check_voice()
    assert failed_with("em-dash(es) in index.html")


def test_entity_em_dash_fails(tree):
    mutate(tree / "index.html", "<h2>What I work on</h2>", "<h2>What I work &mdash; on</h2>")
    vs.check_voice()
    assert failed_with("em-dash(es) in index.html")


def test_marketing_adjective_in_yaml_fails(tree):
    mutate(tree / "projects.yml", 'what: "24/7 AI swing-trading agent',
           'what: "Production-grade 24/7 AI swing-trading agent')
    vs.check_voice()
    assert failed_with("banned marketing adjective(s) in projects.yml (prose): production-grade")


def test_marketing_adjective_in_resume_source_fails(tree):
    mutate(tree / "resume-static.yml", '"Computer Engineering student focused',
           '"Rigorous Computer Engineering student focused')
    vs.check_voice()
    assert failed_with("resume-static.yml (prose): rigorous")


def test_yaml_comment_is_exempt_from_voice_rules(tree):
    mutate(tree / "projects.yml", "# projects.yml — single source",
           "# projects.yml — a robust, seamless source")
    vs.check_voice()
    assert not failed_with("projects.yml")


# ---------------- stale guard threshold band ----------------

@pytest.mark.parametrize("threshold", ["99999", "0", "-1"])
def test_stale_guard_threshold_outside_band_fails_before_browser(tree, threshold):
    mutate(tree / "script.js", "const STALE_AFTER_DAYS = 7;",
           f"const STALE_AFTER_DAYS = {threshold};")
    vs.check_stale_guard(browser=None, port=0)
    assert failed_with("STALE_AFTER_DAYS")


def test_stale_guard_constant_removed_fails(tree):
    mutate(tree / "script.js", "const STALE_AFTER_DAYS = 7;", "const LIMIT = 7;")
    vs.check_stale_guard(browser=None, port=0)
    assert failed_with("STALE_AFTER_DAYS not found")


# ---------------- sitemap ----------------

def test_sitemap_lastmod_not_a_date_fails(tree):
    mutate(tree / "sitemap.xml", "<lastmod>", "<lastmod>soon")
    vs.check_sitemap()
    assert failed_with("lastmod")


def stamp_sitemap(tree: Path, day: date) -> None:
    text = (tree / "sitemap.xml").read_text(encoding="utf-8")
    text = vs.re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{day.isoformat()}</lastmod>", text)
    (tree / "sitemap.xml").write_text(text, encoding="utf-8")


def test_sitemap_lastmod_a_year_old_fails(tree):
    stamp_sitemap(tree, date.today() - timedelta(days=400))
    vs.check_sitemap()
    assert failed_with("stale")


def test_sitemap_lastmod_two_months_old_warns(tree):
    stamp_sitemap(tree, date.today() - timedelta(days=70))
    vs.check_sitemap()
    assert warned_with("lastmod")
    assert vs.failures == []


def test_sitemap_lastmod_in_the_future_fails(tree):
    stamp_sitemap(tree, date.today() + timedelta(days=5))
    vs.check_sitemap()
    assert failed_with("future")


def test_sitemap_lastmod_today_passes(tree):
    stamp_sitemap(tree, date.today())
    vs.check_sitemap()
    assert vs.failures == [] and vs.warnings == []


# ---------------- resume expectations ----------------

def test_resume_expected_strings_name_gpa_and_capped_projects(tree):
    expected = vs.resume_expected_strings(projects(tree))
    assert expected[0] == "Jake Hoffman"
    assert "3.85" in expected
    names = expected[2:]
    assert len(names) == 4
    assert "trader" in names and "Odds Aggregator" in names


# ---------------- axe-core with a fallback CDN ----------------

class FakePage:
    def __init__(self, failing: set[str]):
        self.failing = failing
        self.loaded: list[str] = []

    def add_script_tag(self, url: str) -> None:
        if url in self.failing:
            raise RuntimeError("net::ERR_CONNECTION_REFUSED")
        self.loaded.append(url)

    def evaluate(self, _js: str):
        return {"violations": []}


def test_axe_falls_back_to_second_cdn(tree):
    page = FakePage(failing={vs.AXE_URLS[0]})
    vs.run_axe(page, "index.html [dark]")
    assert page.loaded == [vs.AXE_URLS[1]]
    assert vs.warnings == [] and vs.failures == []


def test_axe_warns_only_when_every_cdn_fails(tree):
    page = FakePage(failing=set(vs.AXE_URLS))
    vs.run_axe(page, "index.html [dark]")
    assert warned_with("a11y checks skipped")
    assert vs.failures == []


# ---------------- local playwright matches the CI pin ----------------

def test_playwright_pin_is_read_from_deploy_workflow():
    assert vs.pinned_playwright_version() == "1.62.0"


def test_local_playwright_older_than_pin_warns(tree, monkeypatch):
    monkeypatch.setattr(vs, "IN_CI", False)
    vs.check_playwright_pin(installed="1.58.0")
    assert warned_with("1.58.0")
    assert vs.failures == []


def test_ci_playwright_differing_from_pin_fails(tree, monkeypatch):
    """In CI the installed build comes from a workflow pin, so a
    mismatch means the two workflows drifted apart."""
    monkeypatch.setattr(vs, "IN_CI", True)
    vs.check_playwright_pin(installed="1.58.0")
    assert failed_with("must pin the same build")


def test_local_playwright_matching_pin_is_quiet(tree):
    vs.check_playwright_pin(installed=vs.pinned_playwright_version())
    assert vs.warnings == [] and vs.failures == []
