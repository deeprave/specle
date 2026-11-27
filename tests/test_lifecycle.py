import json
from pathlib import Path

import pytest

from specle import sidecars
from specle.change_state import read_change_state, resolve_change
from specle.inventory import (
    LifecycleDeclaration,
    LifecycleState,
    LifecycleTransition,
    SkillMetadata,
)
from specle.lifecycle import (
    discover_delivery_sidecars,
    validate_installed_skill_inventory,
    validate_lifecycle_graph,
    validate_runtime_records,
)
from specle.schema_registry import SCHEMA_IDENTIFIERS
from specle.sidecars import SidecarRelationshipError, record_sidecar_relationship


def test_packaged_lifecycle_has_no_graph_diagnostics() -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    from specle.inventory import discover_skills

    assert validate_lifecycle_graph(discover_skills(root)) == ()


def test_archived_delivery_allows_only_completion_resumption() -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    from specle.inventory import discover_skills

    skills = {skill.name: skill for skill in discover_skills(root)}

    assert "wrapup" not in skills
    lifecycle = skills["complete"].lifecycle
    assert lifecycle is not None
    assert "complete" in lifecycle.accepts
    lifecycle = skills["commit"].lifecycle
    assert lifecycle is not None
    assert "complete" not in lifecycle.accepts
    for name in ("commit", "triage", "resolve"):
        lifecycle = skills[name].lifecycle
        assert lifecycle is not None
        assert "complete" not in lifecycle.accepts
    lifecycle = skills["triage"].lifecycle
    assert lifecycle is not None
    assert "committed" in lifecycle.accepts


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


def test_ignores_malformed_local_context_when_resolving_runtime_state(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    (target / ".specle" / "context.json").write_text("not valid json\n")

    snapshot = read_change_state(target)

    assert resolve_change(snapshot, "example").name == "example"
    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_accepts_a_selected_archived_change_awaiting_completion_resumption(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="complete", archived=True)
    (target / ".specle" / "current-change").write_text("example\n")

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_accepts_unicode_change_names_with_ascii_hyphen_separators(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "révision-東京", status="defined")
    (target / ".specle" / "current-change").write_text("révision-東京\n")

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_reports_non_ascii_dash_in_a_change_name(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "révision—東京", status="defined")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "invalid change directory name" in diagnostics[0].message


def test_reports_noncanonical_durable_timestamp(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    status_path = target / ".specle" / "changes" / "example" / "status.json"
    status = json.loads(status_path.read_text())
    status["created_at"] = "2026-11-21T20:14:00+11:00"
    status_path.write_text(json.dumps(status))

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "failed type" in diagnostics[0].message


def test_reports_invalid_status_and_archived_non_completion(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="unknown")
    _write_status(target, "archived", status="defined", archived=True)

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert {"invalid-status", "archived-not-complete"} <= codes


def test_accepts_archived_cancelled_change(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "cancelled", status="cancelled", archived=True)
    status_path = target / ".specle" / "archive" / "cancelled" / "status.json"
    status = json.loads(status_path.read_text())
    status["cancelled_at"] = 1_795_252_441
    status_path.write_text(json.dumps(status))

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_accepts_archived_cancelled_spike(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(
        target, "cancelled-spike", status="cancelled", archived=True, kind="spike"
    )
    status_path = target / ".specle" / "archive" / "cancelled-spike" / "status.json"
    status = json.loads(status_path.read_text())
    status["cancelled_at"] = 1_795_252_441
    status_path.write_text(json.dumps(status))

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_packaged_runtime_accepts_archived_cancelled_records_for_every_kind(
    tmp_path: Path,
) -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    from specle.inventory import discover_skills

    target = tmp_path / "project"
    for kind in ("change", "bugfix", "refactor", "spike"):
        name = f"cancelled-{kind}"
        _write_status(target, name, status="cancelled", archived=True, kind=kind)
        status_path = target / ".specle" / "archive" / name / "status.json"
        status = json.loads(status_path.read_text())
        status["cancelled_at"] = 1_795_252_441
        status_path.write_text(json.dumps(status))

    assert validate_runtime_records(target, discover_skills(root)) == ()


def test_rejects_cancelled_records_without_archive_or_timestamp(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "active", status="cancelled")
    _write_status(target, "missing-timestamp", status="cancelled", archived=True)

    codes = {
        diagnostic.code
        for diagnostic in validate_runtime_records(target, _runtime_skills())
    }

    assert {"cancelled-not-archived", "missing-evidence"} <= codes


def test_accepts_resolved_review_evidence_for_an_approved_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="approved", review_status="resolved")
    _write_review_findings(
        target,
        "example",
        [
            {"decision": "decline"},
            {
                "decision": "accept",
                "dispatch": {"state": "complete"},
            },
            {
                "decision": "vary",
                "dispatch": {"state": "complete"},
            },
        ],
    )

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_accepts_direct_delivery_evidence_for_a_committed_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="committed")
    status_path = target / ".specle" / "changes" / "example" / "status.json"
    status = json.loads(status_path.read_text())
    status["delivery"] = {"branch": "main", "commit": "abcdef0"}
    status_path.write_text(json.dumps(status))

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_rejects_unsettled_or_missing_resolved_review_evidence(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "missing", status="approved", review_status="resolved")
    _write_status(target, "unsettled", status="approved", review_status="resolved")
    _write_review_findings(target, "unsettled", [{"decision": None}])
    _write_status(target, "unreadable", status="approved", review_status="resolved")
    (target / ".specle" / "changes" / "unreadable" / "review-findings.json").mkdir()

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"missing-evidence"}
    assert len(diagnostics) == 3
    assert all("invalid review" in diagnostic.message for diagnostic in diagnostics)


def test_rejects_unsupported_review_evidence_for_an_approved_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="approved", review_status="not-run")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"missing-evidence"}
    assert "invalid review" in diagnostics[0].message


def test_reports_duplicate_change_names_across_active_and_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    _write_status(target, "example", status="complete", archived=True)

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "duplicate change name" in diagnostics[0].message


def test_reports_case_folded_duplicate_change_names(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "Foo", status="defined")
    _write_status(target, "foo", status="complete", archived=True)

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "duplicate change name" in diagnostics[0].message


def test_reports_non_nfc_and_windows_reserved_change_names(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "cafe\u0301", status="defined")
    _write_status(target, "CON", status="defined")

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert len(diagnostics) == 2
    assert all(
        "invalid change directory name" in diagnostic.message
        for diagnostic in diagnostics
    )


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


@pytest.mark.parametrize("required_status", ("approved", "committed"))
def test_discovers_delivery_ready_reciprocal_sidecars_from_parent_only(
    tmp_path: Path, required_status: str
) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "parent",
        status=required_status,
        relationships=[
            {
                "change": "fix-parent",
                "type": "bugfix",
                "delivery": "with-related-change",
            }
        ],
    )
    _write_status(
        target,
        "fix-parent",
        status=required_status,
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            }
        ],
    )
    _write_status(
        target,
        "unrelated-fix",
        status=required_status,
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            }
        ],
    )

    snapshot = read_change_state(target)
    result = discover_delivery_sidecars(
        snapshot, resolve_change(snapshot, "parent"), required_status=required_status
    )

    assert tuple(record.name for record in result.sidecars) == ("fix-parent",)
    assert result.diagnostics == ()


def test_reports_invalid_or_unready_delivery_sidecars(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "parent",
        status="approved",
        relationships=[
            {
                "change": "missing",
                "type": "bugfix",
                "delivery": "with-related-change",
            },
            {
                "change": "wrong-kind",
                "type": "bugfix",
                "delivery": "with-related-change",
            },
            {
                "change": "unready",
                "type": "bugfix",
                "delivery": "with-related-change",
            },
        ],
    )
    _write_status(target, "wrong-kind", status="approved", kind="refactor")
    _write_status(
        target,
        "unready",
        status="building",
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            }
        ],
    )

    snapshot = read_change_state(target)
    result = discover_delivery_sidecars(
        snapshot, resolve_change(snapshot, "parent"), required_status="approved"
    )

    assert result.sidecars == ()
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "missing-sidecar",
        "sidecar-kind-mismatch",
        "sidecar-not-ready",
    }


def test_reports_missing_and_duplicate_reciprocal_relationships(tmp_path: Path) -> None:
    target = tmp_path / "project"
    relationship = {
        "change": "fix-parent",
        "type": "bugfix",
        "delivery": "with-related-change",
    }
    _write_status(
        target,
        "parent",
        status="approved",
        relationships=[
            relationship,
            relationship,
            {
                "change": "fix-missing",
                "type": "bugfix",
                "delivery": "with-related-change",
            },
            {
                "change": "fix-double",
                "type": "bugfix",
                "delivery": "with-related-change",
            },
        ],
    )
    _write_status(
        target,
        "fix-parent",
        status="approved",
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            }
        ],
    )
    _write_status(target, "fix-missing", status="approved", kind="bugfix")
    _write_status(
        target,
        "fix-double",
        status="approved",
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            },
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            },
        ],
    )

    snapshot = read_change_state(target)
    result = discover_delivery_sidecars(
        snapshot, resolve_change(snapshot, "parent"), required_status="approved"
    )

    assert result.sidecars == ()
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "duplicate-sidecar",
        "missing-reciprocal-sidecar",
        "duplicate-reciprocal-sidecar",
    }


def test_rejects_a_reciprocal_relationship_without_origin_role(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "parent",
        status="approved",
        relationships=[
            {
                "change": "fix-parent",
                "type": "bugfix",
                "delivery": "with-related-change",
            }
        ],
    )
    _write_status(
        target,
        "fix-parent",
        status="approved",
        kind="bugfix",
        relationships=[
            {
                "change": "parent",
                "type": "bugfix",
                "delivery": "with-related-change",
            }
        ],
    )

    snapshot = read_change_state(target)
    result = discover_delivery_sidecars(
        snapshot, resolve_change(snapshot, "parent"), required_status="approved"
    )

    assert result.sidecars == ()
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "missing-reciprocal-sidecar"
    }


def test_runtime_validation_reports_malformed_reciprocal_relationship(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "parent",
        status="approved",
        review_status="pass",
        relationships=[
            {
                "change": "fix-parent",
                "type": "bugfix",
                "delivery": "with-related-change",
            }
        ],
    )
    _write_status(
        target,
        "fix-parent",
        status="approved",
        kind="bugfix",
        review_status="pass",
        relationships=[
            {
                "change": "parent",
                "type": "bugfix",
                "delivery": "with-related-change",
            }
        ],
    )

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "invalid-sidecar-relationship",
        "missing-reciprocal-sidecar",
    }


def test_runtime_validation_reports_an_orphaned_sidecar_relationship(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "fix-parent",
        status="approved",
        kind="bugfix",
        review_status="pass",
        relationships=[
            {
                "change": "parent",
                "type": "origin",
                "delivery": "with-related-change",
            }
        ],
    )

    diagnostics = validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "missing-reciprocal-parent"
    }


def test_runtime_validation_preserves_legacy_archived_relationships(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(
        target,
        "legacy-fix",
        status="complete",
        archived=True,
        kind="bugfix",
        relationships=[
            {
                "change": "legacy-parent",
                "type": "completion-review-fix",
                "delivery": "with-related-change",
            }
        ],
    )

    assert validate_runtime_records(target, _runtime_skills()) == ()


def test_records_reciprocal_sidecar_relationships(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "parent", status="building")
    _write_status(target, "fix-parent", status="defined", kind="bugfix")
    snapshot = read_change_state(target)

    record_sidecar_relationship(
        resolve_change(snapshot, "parent"), resolve_change(snapshot, "fix-parent")
    )

    refreshed = read_change_state(target)
    parent = resolve_change(refreshed, "parent")
    sidecar = resolve_change(refreshed, "fix-parent")
    assert parent.status["relationships"] == [
        {
            "change": "fix-parent",
            "type": "bugfix",
            "delivery": "with-related-change",
        }
    ]
    assert sidecar.status["relationships"] == [
        {
            "change": "parent",
            "type": "origin",
            "delivery": "with-related-change",
        }
    ]


def test_relationship_mutation_uses_current_status_records(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "parent", status="building")
    _write_status(target, "fix-parent", status="defined", kind="bugfix")
    snapshot = read_change_state(target)
    parent = resolve_change(snapshot, "parent")
    sidecar = resolve_change(snapshot, "fix-parent")
    parent_path = parent.directory / "status.json"
    current_parent = json.loads(parent_path.read_text())
    current_parent["revision_note"] = "written after snapshot"
    parent_path.write_text(json.dumps(current_parent))

    record_sidecar_relationship(parent, sidecar)

    refreshed = json.loads(parent_path.read_text())
    assert refreshed["revision_note"] == "written after snapshot"
    assert refreshed["relationships"] == [
        {
            "change": "fix-parent",
            "type": "bugfix",
            "delivery": "with-related-change",
        }
    ]


def test_restores_the_parent_record_when_sidecar_linking_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "project"
    _write_status(target, "parent", status="building")
    _write_status(target, "fix-parent", status="defined", kind="bugfix")
    snapshot = read_change_state(target)
    parent = resolve_change(snapshot, "parent")
    sidecar = resolve_change(snapshot, "fix-parent")
    parent_path = parent.directory / "status.json"
    sidecar_path = sidecar.directory / "status.json"
    original_parent = parent_path.read_bytes()
    original_sidecar = sidecar_path.read_bytes()
    replace = sidecars.os.replace

    def fail_sidecar_replacement(source: str | Path, destination: str | Path) -> None:
        if Path(destination) == sidecar_path:
            raise OSError("simulated sidecar replacement failure")
        replace(source, destination)

    monkeypatch.setattr(sidecars.os, "replace", fail_sidecar_replacement)

    with pytest.raises(SidecarRelationshipError, match="could not write"):
        record_sidecar_relationship(parent, sidecar)

    assert parent_path.read_bytes() == original_parent
    assert sidecar_path.read_bytes() == original_sidecar


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
                accepts=("defined", "verified", "approved", "committed"),
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
        _skill(
            "spike",
            LifecycleDeclaration(
                accepts=("defined", "spiking"),
                creates=("defined",),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined", kind="spike"),
                        LifecycleState("spiking", kind="spike"),
                        None,
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
        _skill(
            "cancel",
            LifecycleDeclaration(
                accepts=("defined",),
                creates=(),
                transitions=(
                    LifecycleTransition(
                        LifecycleState("defined"), LifecycleState("cancelled"), None
                    ),
                ),
                terminal=("cancelled",),
            ),
        ),
    )


def _write_status(
    target: Path,
    name: str,
    *,
    status: str,
    archived: bool = False,
    kind: str = "change",
    review_status: str = "not-run",
    relationships: list[dict[str, str]] | None = None,
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
                "created_at": 1_795_252_440,
                "activated_at": None,
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": review_status},
                "delivery": None,
                "relationships": relationships or [],
                "dependencies": [],
            }
        )
    )


def _write_review_findings(
    target: Path, name: str, items: list[dict[str, object]]
) -> None:
    path = target / ".specle" / "changes" / name / "review-findings.json"
    path.write_text(json.dumps({"sources": [], "items": items}))


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
