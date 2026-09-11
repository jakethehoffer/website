"""Tests for scripts/refresh-meta.py failure behaviour.

The deploy job runs this script and ships whatever it leaves in the
working tree. A lookup that fails must therefore never let the
committed pill text (which reads "last commit: today" after a human
build) deploy under a fresh date stamp: that is the one shape the
browser-side stale guard cannot see, because the stamp is current.

gh_pushed_at is replaced in these tests. It is the only network call,
and a real lookup needs a token with access to private repos.

Run:  python -m pytest scripts -q
"""

from __future__ import annotations

import importlib.util
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rm = load_script("refresh-meta")

FRESH = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def tree(tmp_path, monkeypatch):
    for name in ("index.html", "projects.yml", "sitemap.xml"):
        shutil.copy(ROOT / name, tmp_path / name)
    monkeypatch.setattr(rm, "INDEX", tmp_path / "index.html")
    monkeypatch.setattr(rm, "PROJECTS_YML", tmp_path / "projects.yml")
    monkeypatch.setattr(rm, "SITEMAP", tmp_path / "sitemap.xml")
    return tmp_path


def lookups(failing: set[str]):
    """A stand-in for gh_pushed_at: None for the named repos, a
    just-now timestamp for the rest."""
    def fake(owner: str, name: str):
        return None if name in failing else FRESH
    return fake


def pill(tree: Path, key: str) -> str:
    html = (tree / "index.html").read_text(encoding="utf-8")
    m = rm.re.search(r'data-meta="' + rm.re.escape(key) + r'"[^>]*>([^<]*)<', html)
    return m.group(1)


def test_one_failed_lookup_in_ci_exits_nonzero(tree, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(rm, "gh_pushed_at", lookups(failing={"trader"}))
    before = (tree / "index.html").read_text(encoding="utf-8")
    with pytest.raises(SystemExit) as exit_info:
        rm.main()
    assert exit_info.value.code == 1
    assert (tree / "index.html").read_text(encoding="utf-8") == before


def test_every_lookup_failing_in_ci_exits_nonzero(tree, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(rm, "gh_pushed_at",
                        lookups(failing={"trader", "arbitrage", "tax-rebalance"}))
    with pytest.raises(SystemExit) as exit_info:
        rm.main()
    assert exit_info.value.code == 1


def test_all_lookups_succeeding_in_ci_writes_the_pills(tree, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(rm, "gh_pushed_at", lookups(failing=set()))
    rm.main()
    assert pill(tree, "trader.last_commit") == "last commit: today"
    assert pill(tree, "tax-rebalance.last_commit") == "last commit: today"


def test_one_failed_lookup_locally_only_warns(tree, monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(rm, "gh_pushed_at", lookups(failing={"trader"}))
    rm.main()
    out = capsys.readouterr().out
    assert "[warn] 1 of 3 gh lookup(s) failed (jakethehoffer/trader)" in out
    assert pill(tree, "arbitrage.last_commit") == "last commit: today"
