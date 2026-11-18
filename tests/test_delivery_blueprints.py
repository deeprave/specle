from pathlib import Path

from specle.inventory import discover_skills, discover_steering

BLUEPRINTS = Path(__file__).parents[1] / "src" / "specle" / "blueprints"


def test_distribution_includes_delivery_policy_and_integration_skills() -> None:
    steering = discover_steering(BLUEPRINTS / "steering")
    skills = discover_skills(BLUEPRINTS / "skills")

    assert "delivery.md" in [path.name for path in steering]
    assert {
        (skill.name, skill.specle_group)
        for skill in skills
        if skill.name in {"commit", "complete"}
    } == {("commit", "Integration"), ("complete", "Integration")}


def test_delivery_blueprints_define_the_required_workflow_safeguards() -> None:
    delivery = (BLUEPRINTS / "steering" / "delivery.md").read_text()
    onboard = (BLUEPRINTS / "skills" / "onboard" / "SKILL.md").read_text()
    lifecycle = (BLUEPRINTS / "steering" / "lifecycle.md").read_text()
    triage = (BLUEPRINTS / "skills" / "triage" / "SKILL.md").read_text()
    resolve = (BLUEPRINTS / "skills" / "resolve" / "SKILL.md").read_text()
    spec = (BLUEPRINTS / "skills" / "spec" / "SKILL.md").read_text()
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
    assert "without replacing the active current issue" in triage
    assert (
        "returns through build, verification, review, approval, and commit" in resolve
    )
    assert "locally reviewed target to `approved`" in resolve
    assert "previously committed target to `committed`" in resolve
    assert "queued `defined` work" in resolve
    assert "Do not complete the origin" in resolve
    assert 'queued record with `kind: "change"`' in spec
    assert "committed` normal changes may be verified" in verify
    assert "explicit user authorisation" in commit
    assert "selected target's existing context record" in commit
    assert "versioned delivery-record contract" not in commit
    assert "checkout is on the recorded delivery head branch" in complete
    assert "selected target's existing context record" in complete
    assert "versioned delivery-record contract" not in complete
    assert "Do not stash, switch, merge, pull, fetch" in complete
    assert "stash that includes untracked files" in complete
    assert "retain the stash" in complete
    assert '"delivery": "with-related-spec"' in bugfix
    assert "declared related sidecars" in status
    assert "related approved sidecars" in commit
    assert "unlinked abbreviated work" in bugfix
    assert (
        "unlinked abbreviated work"
        in (BLUEPRINTS / "skills" / "refactor" / "SKILL.md").read_text()
    )
    assert (
        "separate worktree"
        in (BLUEPRINTS / "skills" / "implement" / "SKILL.md").read_text()
    )


def test_root_references_match_the_delivery_workflow() -> None:
    lifecycle = (Path(__file__).parents[1] / "LIFECYCLE.md").read_text()
    schema = (Path(__file__).parents[1] / "SCHEMA.md").read_text()

    assert "`approved`" in lifecycle
    assert "`committed`" in lifecycle
    assert "review approves| approved" in lifecycle
    assert "resolve: local all no-action| approved" in lifecycle
    assert "resolve: external all no-action| committed" in lifecycle
    assert "creates queued normal work" in lifecycle
    assert "src/specle/blueprints/skills/" in schema
    assert "skills/specle/index.json" in schema
    assert "delivery evidence" in schema
    assert "versioned JSON-contract change" not in schema


def test_planning_skills_keep_changes_independent_by_default() -> None:
    skills = {
        name: (BLUEPRINTS / "skills" / name / "SKILL.md").read_text()
        for name in ("spec", "estimate", "design", "tasks", "revise", "implement")
    }

    for content in skills.values():
        assert "independent by default" in content
        assert "explicit user decision" in content
        assert "must not create a dependency" in content
