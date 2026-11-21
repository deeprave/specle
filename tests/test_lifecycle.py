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


def test_validates_per_change_state_and_ignored_selection(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    selector = target / ".specle" / "current-change"
    selector.write_text("example\n")

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_reports_invalid_status_and_archived_non_completion(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="unknown")
    _write_status(target, "archived", status="defined", archived=True)

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert {"invalid-status", "archived-not-complete"} <= codes


def test_reports_duplicate_change_names_across_active_and_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    _write_status(target, "example", status="complete", archived=True)

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "duplicate change name" in diagnostics[0].message


def test_reports_an_implementation_status_for_a_spike(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="building", kind="spike")
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
    directory = target / ".specle" / "changes" / "example"
    directory.mkdir(parents=True)
    (directory / "status.json").write_text("{")
    (target / ".specle" / "current-change").write_text("not-a-change\nsecond\n")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "malformed JSON" in diagnostics[0].message


def test_accepts_a_status_symlink_to_a_regular_file(tmp_path: Path) -> None:
    target = tmp_path / "project"
    name = "example"
    _write_status(target, name, status="defined")
    status_path = target / ".specle" / "changes" / name / "status.json"
    source = tmp_path / "status-source.json"
    source.write_text(status_path.read_text())
    status_path.unlink()
    status_path.symlink_to(source)

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_reports_a_non_regular_status_before_reading_it(tmp_path: Path) -> None:
    target = tmp_path / "project"
    name = "example"
    directory = target / ".specle" / "changes" / name
    directory.mkdir(parents=True)
    (directory / "status.json").symlink_to(tmp_path, target_is_directory=True)

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "not a regular file" in diagnostics[0].message


def test_reports_a_broken_current_change_symlink(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    selector = target / ".specle" / "current-change"
    selector.symlink_to(tmp_path / "missing-current-change")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "not a regular file" in diagnostics[0].message


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
    root = "archive" if archived else "changes"
    directory = target / ".specle" / root / name
    directory.mkdir(parents=True)
    (directory / "status.json").write_text(
        json.dumps(
            {
                "$schema": SCHEMA_IDENTIFIERS["change-status"],
                "kind": kind,
                "status": status,
                "created_at": "2026-11-21T20:14:00+11:00",
                "activated_at": None,
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
