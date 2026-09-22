"""The privacy check must block every Pages publish, not run beside it."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


def workflow(name):
    return yaml.load(
        (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )


def test_pages_publish_waits_for_privacy_check():
    deploy = workflow("deploy.yml")
    jobs = deploy["jobs"]
    publishers = [job for job in jobs.values() if any(
        step.get("uses", "").startswith("actions/deploy-pages@")
        for step in job.get("steps", [])
    )]
    assert publishers, "No Pages publish job found"
    for job in publishers:
        needs = job.get("needs", [])
        needs = [needs] if isinstance(needs, str) else needs
        assert "public-safety" in needs, "Publishing must wait for the privacy check"
        assert "if" not in job, "Do not bypass a failed privacy check with a job condition"
    safety = jobs["public-safety"]
    assert safety["uses"] == "./.github/workflows/public-safety.yml"
    assert "if" not in safety, "Privacy checks must run on every deploy trigger"
    assert safety["secrets"] == {"BANNED_TERMS": "${{ secrets.BANNED_TERMS }}"}
    assert safety["permissions"] == {"contents": "read"}
    called = workflow("public-safety.yml")
    assert called["on"]["workflow_call"]["secrets"]["BANNED_TERMS"]["required"] == "true"
    assert "pull_request" in called["on"]
