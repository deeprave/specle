import json
from pathlib import Path

from specle.inventory import (
    LifecycleDeclaration,
    LifecycleState,
    LifecycleTransition,
    SkillMetadata,
)
from specle.lifecycle import (
    validate_installed_skill_inventory,
    validate_lifecycle_graph,
    validate_runtime_records,
)


def test_packaged_lifecycle_has_no_graph_diagnostics() -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    from specle.inventory import discover_skills

    assert validate_lifecycle_graph(discover_skills(root)) == ()


def test_reports_missing_next_skill_and_dead_end() -> None:
    skills = (
        _skill(
            "start",
            LifecycleDeclaration(
                accepts=("defined",),
                creates=("defined",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined"),
                        LifecycleState("planned"),
                        "missing",
                    ),
                ),
                terminal=(),
            ),
        ),
    )

    codes = {diagnostic.code for diagnostic in validate_lifecycle_graph(skills)}

    assert {"missing-next-skill", "missing-terminal", "dead-end-status"} <= codes


def test_nested_selectors_participate_in_status_graph() -> None:
    skills = (
        _skill(
            "prepare",
            LifecycleDeclaration(
                accepts=("planned",),
                creates=("planned",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("planned", kind="bugfix", scope="queued"),
                        LifecycleState("complete", kind="bugfix", scope="queued"),
                        None,
                    ),
                ),
                terminal=("complete",),
            ),
        ),
    )

    assert validate_lifecycle_graph(skills) == ()


def test_reports_unreachable_and_contradictory_transitions() -> None:
    skills = (
        _skill(
            "start",
            LifecycleDeclaration(
                accepts=("defined",),
                creates=("defined",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined"),
                        LifecycleState("planned"),
                        "first-next",
                    ),
                    LifecycleTransition(
                        LifecycleState("defined"),
                        LifecycleState("planned"),
                        "second-next",
                    ),
                ),
                terminal=("complete",),
            ),
        ),
        _skill(
            "orphan",
            LifecycleDeclaration(
                accepts=("designed",),
                creates=(),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("designed"), LifecycleState("complete"), None
                    ),
                ),
                terminal=(),
            ),
        ),
        _skill("first-next", None),
        _skill("second-next", None),
    )

    codes = {diagnostic.code for diagnostic in validate_lifecycle_graph(skills)}

    assert {
        "contradictory-transition",
        "unreachable-status",
        "dead-end-status",
    } <= codes


def test_reports_an_invalid_installed_inventory(tmp_path: Path) -> None:
    target = tmp_path / "project"
    skill = target / ".agents" / "skills" / "managed" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        """---
name: managed
specle_group: Planning
requires:
  - missing
description: Managed test skill.
usage: Use for installed inventory tests.
---
"""
    )

    diagnostics = validate_installed_skill_inventory(target)

    assert diagnostics[0].code == "invalid-installed-inventory"
    assert "requires missing skill" in diagnostics[0].message


def test_validates_runtime_records_and_preserves_unknown_fields(tmp_path: Path) -> None:
    target = tmp_path / "project"
    spec_path = ".specle/specs/example"
    (target / spec_path).mkdir(parents=True)
    context = {
        "current_spec": {
            "name": "example",
            "path": spec_path,
            "kind": "change",
            "status": "defined",
            "next": "start",
            "future_field": {"kept": True},
        },
        "queued_specs": [],
        "future_root": True,
    }
    _write_runtime(target, context, {"spec_path": spec_path})

    assert validate_runtime_records(target, _runtime_skills()) == ()

    context["current_spec"].update(
        {"path": ".specle/specs/missing", "kind": "Invalid", "next": "missing"}
    )
    context["queued_specs"] = [
        {"name": "broken", "path": ".specle/specs/missing", "status": "unknown"}
    ]
    _write_runtime(target, context, {"spec_path": spec_path})

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert {
        "current-path-mismatch",
        "path-name-mismatch",
        "invalid-kind",
        "invalid-next",
        "invalid-status",
    } <= codes


def test_reports_malformed_runtime_json(tmp_path: Path) -> None:
    target = tmp_path / "project"
    runtime = target / ".specle"
    runtime.mkdir(parents=True)
    (runtime / "context.json").write_text("{")
    (runtime / "current-issue.json").write_text("{}")

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert "malformed-json" in codes


def _runtime_skills() -> tuple[SkillMetadata, ...]:
    return (
        _skill(
            "start",
            LifecycleDeclaration(
                accepts=("defined", "verified", "approved"),
                creates=("defined",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined"), LifecycleState("complete"), None
                    ),
                ),
                terminal=("complete",),
            ),
        ),
        _skill("review", None),
    )


def _write_runtime(target: Path, context: object, issue: object) -> None:
    runtime = target / ".specle"
    runtime.mkdir(exist_ok=True)
    (runtime / "context.json").write_text(json.dumps(context))
    (runtime / "current-issue.json").write_text(json.dumps(issue))


def _skill(name: str, lifecycle: LifecycleDeclaration | None) -> SkillMetadata:
    return SkillMetadata(
        name=name,
        specle_group="Test",
        description="Test skill.",
        usage="Use for lifecycle tests.",
        requires=(),
        path=Path(f"/{name}/SKILL.md"),
        lifecycle=lifecycle,
    )
