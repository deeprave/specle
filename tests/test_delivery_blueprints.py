from pathlib import Path

from specle.inventory import discover_policies, discover_skills

BLUEPRINTS = Path(__file__).parents[1] / "src" / "specle" / "blueprints"


def test_distribution_includes_delivery_and_automation_policy() -> None:
    policies = discover_policies(BLUEPRINTS / "policies")
    skills = discover_skills(BLUEPRINTS / "skills")

    assert "delivery.md" in [path.name for path in policies]
    assert "automation.md" in [path.name for path in policies]
    assert {
        (skill.name, skill.specle_group)
        for skill in skills
        if skill.name in {"commit", "complete"}
    } == {("commit", "Integration"), ("complete", "Integration")}
    assert "implement" not in {skill.name for skill in skills}


def test_delivery_blueprints_define_the_required_workflow_safeguards() -> None:
    delivery = (BLUEPRINTS / "policies" / "delivery.md").read_text()
    onboard = (BLUEPRINTS / "skills" / "onboard" / "SKILL.md").read_text()
    lifecycle = (BLUEPRINTS / "policies" / "lifecycle.md").read_text()
    triage = (BLUEPRINTS / "skills" / "triage" / "SKILL.md").read_text()
    resolve = (BLUEPRINTS / "skills" / "resolve" / "SKILL.md").read_text()
    verify = (BLUEPRINTS / "skills" / "verify" / "SKILL.md").read_text()
    commit = (BLUEPRINTS / "skills" / "commit" / "SKILL.md").read_text()
    complete = (BLUEPRINTS / "skills" / "complete" / "SKILL.md").read_text()
    bugfix = (BLUEPRINTS / "skills" / "bugfix" / "SKILL.md").read_text()
    status = (BLUEPRINTS / "skills" / "status" / "SKILL.md").read_text()

    assert all(
        model in delivery
        for model in (
            "Local-only Git",
            "Shared upstream, direct to the delivery branch",
            "Shared upstream, branch and pull request",
        )
    )
    assert "another model" in delivery
    assert "delivery.md" in onboard
    assert "one focused question at a\n   time" in onboard
    assert all(status in lifecycle for status in ("`approved`", "`committed`"))
    assert "without replacing `.specle/current-spec`" in triage
    assert (
        "returns through build, verification, review, approval, and commit" in resolve
    )
    assert "locally reviewed target to `approved`" in resolve
    assert "previously committed target to `committed`" in resolve
    assert "unselected `defined` work" in resolve
    assert "Do not complete the origin" in resolve
    assert {"activate", "spec"} <= {
        skill.name for skill in discover_skills(BLUEPRINTS / "skills")
    }
    assert "committed` normal changes may be verified" in verify
    assert "explicit user authorisation" in commit
    assert "target's `status.json`" in commit
    assert "versioned delivery-record contract" not in commit
    assert "checkout is on the recorded delivery head branch" in complete
    assert "selected target's `status.json`" in complete
    assert "versioned delivery-record contract" not in complete
    assert "Do not stash, switch, merge, pull, fetch" in complete
    assert "stash that includes untracked files" in complete
    assert "retain the stash" in complete
    assert "current-spec" in commit
    assert "archive" in complete
    assert "branch-and-pull-request delivery" in (BLUEPRINTS / "AGENTS.md").read_text()
    assert (
        "explicitly named committed normal target"
        in (BLUEPRINTS / "skills" / "build" / "SKILL.md").read_text()
    )
    assert '"delivery": "with-related-spec"' in bugfix
    assert "declared related sidecars" in status
    assert "related approved sidecars" in commit
    assert "unlinked abbreviated work" in bugfix
    assert (
        "unlinked abbreviated work"
        in (BLUEPRINTS / "skills" / "refactor" / "SKILL.md").read_text()
    )


def test_root_references_match_the_delivery_workflow() -> None:
    lifecycle = (Path(__file__).parents[1] / "docs" / "LIFECYCLE.md").read_text()
    schema = (Path(__file__).parents[1] / "docs" / "LAYOUT.md").read_text()

    assert "`approved`" in lifecycle
    assert "`committed`" in lifecycle
    assert "review approves| approved" in lifecycle
    assert "resolve: local all no-action| approved" in lifecycle
    assert "resolve: external all no-action| committed" in lifecycle
    assert "creates unselected normal work" in lifecycle
    assert "src/specle/blueprints/skills/" in schema
    assert "skills/specle/index.json" in schema
    assert "delivery evidence" in schema
    assert "versioned JSON-contract change" not in schema


def test_planning_skills_keep_changes_independent_by_default() -> None:
    skills = {
        name: (BLUEPRINTS / "skills" / name / "SKILL.md").read_text()
        for name in ("spec", "estimate", "design", "tasks", "revise")
    }

    for content in skills.values():
        assert "independent by default" in content
        assert "explicit user decision" in content
        assert "must not create a dependency" in content


def test_dependabot_automerge_defers_the_app_token_until_merge() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "dependabot-automerge.yml"
    ).read_text()

    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "checks: read" in workflow
    assert "statuses: read" in workflow
    assert "github-token: ${{ github.token }}" in workflow
    assert "GH_TOKEN: ${{ github.token }}" in workflow
    assert (
        workflow.index("- name: Fetch Dependabot metadata")
        < workflow.index("- name: Wait for required checks")
        < workflow.index("- name: Create GitHub App token for merge")
        < workflow.index("- name: Enable merge-commit auto-merge")
    )
    assert workflow.count("private-key: ${{ secrets.AUTOMERGE_APP_PRIVATE_KEY }}") == 1
