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
from specle.schema_registry import SCHEMA_IDENTIFIERS


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


def test_validates_per_spec_state_and_ignored_selection(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "202611200001-example", status="defined")
    selector = target / ".specle" / "current-spec"
    selector.write_text("202611200001-example\n")

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_reports_invalid_status_and_archived_non_completion(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "202611200001-example", status="unknown")
    _write_status(target, "202611200002-archived", status="defined", archived=True)

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert {"invalid-status", "archived-not-complete"} <= codes


def test_reports_an_implementation_status_for_a_spike(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "202611200001-example", status="building", kind="spike")
    skills = (
        _skill(
            "spike",
            LifecycleDeclaration(
                accepts=("defined", "spiking"),
                creates=("defined",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined", kind="spike"),
                        LifecycleState("spiking", kind="spike"),
                        "spike",
                    ),
                    LifecycleTransition(
                        LifecycleState("spiking", kind="spike"),
                        LifecycleState("complete", kind="spike"),
                        None,
                    ),
                ),
                terminal=("complete",),
            ),
        ),
    )

    diagnostics = validate_runtime_records(target, skills)

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-status"}


def test_reports_malformed_status_and_invalid_local_selector(tmp_path: Path) -> None:
    target = tmp_path / "project"
    directory = target / ".specle" / "specs" / "202611200001-example"
    directory.mkdir(parents=True)
    (directory / "status.json").write_text("{")
    (target / ".specle" / "current-spec").write_text("not-a-spec\nsecond\n")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "malformed JSON" in diagnostics[0].message


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


def _write_status(
    target: Path,
    name: str,
    *,
    status: str,
    archived: bool = False,
    kind: str = "change",
) -> None:
    root = "archive" if archived else "specs"
    directory = target / ".specle" / root / name
    directory.mkdir(parents=True)
    (directory / "status.json").write_text(
        json.dumps(
            {
                "$schema": SCHEMA_IDENTIFIERS["spec-status"],
                "kind": kind,
                "status": status,
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": "not-run"},
                "delivery": None,
                "relationships": [],
                "dependencies": [],
            }
        )
    )


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
