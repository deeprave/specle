import json
from pathlib import Path

import pytest

from specle.change_state import ChangeRecord, read_change_state, resolve_change
from specle.inventory import (
    LifecycleDeclaration,
    LifecycleState,
    LifecycleTransition,
    SkillMetadata,
    analyse_lifecycle,
    scan_managed_inventory,
)
from specle.lifecycle import next_lifecycle_action, validate_runtime_records
from specle.schema_registry import SCHEMA_IDENTIFIERS


@pytest.mark.anyio
async def test_packaged_lifecycle_has_no_graph_diagnostics() -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    assert (await scan_managed_inventory(root.parent)).lifecycle.diagnostics == ()


@pytest.mark.anyio
async def test_next_lifecycle_action_uses_kind_and_selection_context() -> None:
    planned_change = ChangeRecord(
        "normal",
        Path("normal"),
        {"kind": "change", "status": "planned"},
        False,
    )
    planned_bugfix = ChangeRecord(
        "repair",
        Path("repair"),
        {"kind": "bugfix", "status": "planned"},
        False,
    )

    assert await next_lifecycle_action(planned_change, None) == "activate"
    assert await next_lifecycle_action(planned_change, "normal") == "estimate"
    assert await next_lifecycle_action(planned_bugfix, None) == "activate"


@pytest.mark.anyio
@pytest.mark.parametrize("kind", ["bugfix", "refactor"])
async def test_abbreviated_next_action_uses_task_completion(
    tmp_path: Path, kind: str
) -> None:
    record = ChangeRecord(
        "example", tmp_path, {"kind": kind, "status": "building"}, False
    )
    assert await next_lifecycle_action(record, None) == "build"
    (tmp_path / "tasks.md").write_text("# Tasks\n")
    assert await next_lifecycle_action(record, None) == "build"
    (tmp_path / "tasks.md").write_text("```markdown\n- [x] Example\n```\n")
    assert await next_lifecycle_action(record, None) == "build"
    (tmp_path / "tasks.md").write_text("- [x] Done\n- [ ] Remaining\n")
    assert await next_lifecycle_action(record, None) == "build"
    (tmp_path / "tasks.md").write_text("- [x] Done\n")
    assert await next_lifecycle_action(record, None) == "verify"


@pytest.mark.anyio
async def test_defined_spike_next_action_depends_on_selection() -> None:
    spike = ChangeRecord(
        "investigate",
        Path("investigate"),
        {"kind": "spike", "status": "defined"},
        False,
    )
    assert await next_lifecycle_action(spike, None) == "activate"
    assert await next_lifecycle_action(spike, "investigate") == "spike"


@pytest.mark.anyio
@pytest.mark.parametrize("kind", ["docs", "release", "unknown-kind"])
async def test_unsupported_kind_does_not_offer_activation(kind: str) -> None:
    record = ChangeRecord(
        "example", Path("example"), {"kind": kind, "status": "defined"}, False
    )
    assert await next_lifecycle_action(record, None) is None


@pytest.mark.anyio
async def test_archived_delivery_allows_only_completion_resumption() -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    skills = {
        record.metadata.name: record.metadata
        for record in (await scan_managed_inventory(root.parent)).skills
    }

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


@pytest.mark.anyio
async def test_reports_missing_next_skill_and_dead_end() -> None:
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

    codes = {diagnostic.code for diagnostic in analyse_lifecycle(skills).diagnostics}

    assert {"missing-next-skill", "missing-terminal", "dead-end-status"} <= codes


@pytest.mark.anyio
async def test_nested_selectors_participate_in_status_graph() -> None:
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

    assert analyse_lifecycle(skills).diagnostics == ()


@pytest.mark.anyio
async def test_reports_unreachable_and_contradictory_transitions() -> None:
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

    codes = {diagnostic.code for diagnostic in analyse_lifecycle(skills).diagnostics}

    assert {
        "contradictory-transition",
        "unreachable-status",
        "dead-end-status",
    } <= codes


@pytest.mark.anyio
async def test_validates_per_change_state_and_ignored_selection(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    selector = target / ".specle" / "current-change"
    selector.write_text("example\n")

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_ignores_malformed_local_context_when_resolving_runtime_state(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    (target / ".specle" / "context.json").write_text("not valid json\n")

    snapshot = await read_change_state(target)

    assert resolve_change(snapshot, "example").name == "example"
    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_accepts_a_selected_archived_change_awaiting_completion_resumption(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="complete", archived=True)
    (target / ".specle" / "current-change").write_text("example\n")

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_accepts_unicode_change_names_with_ascii_hyphen_separators(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "révision-東京", status="defined")
    (target / ".specle" / "current-change").write_text("révision-東京\n")

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_reports_non_ascii_dash_in_a_change_name(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "révision—東京", status="defined")

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "invalid change directory name" in diagnostics[0].message


@pytest.mark.anyio
async def test_reports_noncanonical_durable_timestamp(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    status_path = target / ".specle" / "changes" / "example" / "status.json"
    status = json.loads(status_path.read_text())
    status["created_at"] = "2026-11-21T20:14:00+11:00"
    status_path.write_text(json.dumps(status))

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "failed type" in diagnostics[0].message


@pytest.mark.anyio
async def test_reports_invalid_status_and_archived_non_completion(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="unknown")
    _write_status(target, "archived", status="defined", archived=True)

    codes = {
        diagnostic.code
        for diagnostic in await validate_runtime_records(target, _runtime_skills())
    }

    assert {"invalid-status", "archived-not-complete"} <= codes


@pytest.mark.anyio
async def test_accepts_archived_cancelled_change(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "cancelled", status="cancelled", archived=True)

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_accepts_archived_cancelled_spike(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(
        target, "cancelled-spike", status="cancelled", archived=True, kind="spike"
    )

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_packaged_runtime_accepts_archived_cancelled_records_for_every_kind(
    tmp_path: Path,
) -> None:
    root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"
    target = tmp_path / "project"
    for kind in ("change", "bugfix", "refactor", "spike"):
        name = f"cancelled-{kind}"
        _write_status(target, name, status="cancelled", archived=True, kind=kind)

    skills = tuple(
        record.metadata for record in (await scan_managed_inventory(root.parent)).skills
    )
    assert await validate_runtime_records(target, skills) == ()


@pytest.mark.anyio
async def test_rejects_active_cancelled_record(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "active", status="cancelled")

    codes = {
        diagnostic.code
        for diagnostic in await validate_runtime_records(target, _runtime_skills())
    }

    assert codes == {"cancelled-not-archived"}


@pytest.mark.anyio
async def test_accepts_resolved_review_evidence_for_an_approved_change(
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

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_accepts_direct_delivery_evidence_for_a_committed_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="committed")
    status_path = target / ".specle" / "changes" / "example" / "status.json"
    status = json.loads(status_path.read_text())
    status["delivery"] = {"branch": "main", "commit": "abcdef0"}
    status_path.write_text(json.dumps(status))

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_rejects_unsettled_or_missing_resolved_review_evidence(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "missing", status="approved", review_status="resolved")
    _write_status(target, "unsettled", status="approved", review_status="resolved")
    _write_review_findings(target, "unsettled", [{"decision": None}])
    _write_status(target, "unreadable", status="approved", review_status="resolved")
    (target / ".specle" / "changes" / "unreadable" / "review-findings.json").mkdir()

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"missing-evidence"}
    assert len(diagnostics) == 3
    assert all("invalid review" in diagnostic.message for diagnostic in diagnostics)


@pytest.mark.anyio
async def test_rejects_unsupported_review_evidence_for_an_approved_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="approved", review_status="not-run")

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"missing-evidence"}
    assert "invalid review" in diagnostics[0].message


@pytest.mark.anyio
async def test_reports_duplicate_change_names_across_active_and_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    _write_status(target, "example", status="complete", archived=True)

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "duplicate change name" in diagnostics[0].message


@pytest.mark.anyio
async def test_reports_case_folded_duplicate_change_names(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "Foo", status="defined")
    _write_status(target, "foo", status="complete", archived=True)

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "duplicate change name" in diagnostics[0].message


@pytest.mark.anyio
async def test_reports_non_nfc_and_windows_reserved_change_names(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    _write_status(target, "cafe\u0301", status="defined")
    _write_status(target, "CON", status="defined")

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert len(diagnostics) == 2
    assert all(
        "invalid change directory name" in diagnostic.message
        for diagnostic in diagnostics
    )


@pytest.mark.anyio
async def test_reports_an_implementation_status_for_a_spike(tmp_path: Path) -> None:
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

    diagnostics = await validate_runtime_records(target, skills)

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-status"}


@pytest.mark.anyio
async def test_reports_malformed_status_and_invalid_local_selector(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project"
    directory = target / ".specle" / "changes" / "example"
    directory.mkdir(parents=True)
    (directory / "status.json").write_text("{")
    (target / ".specle" / "current-change").write_text("not-a-change\nsecond\n")

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "malformed JSON" in diagnostics[0].message


@pytest.mark.anyio
async def test_accepts_a_status_symlink_to_a_regular_file(tmp_path: Path) -> None:
    target = tmp_path / "project"
    name = "example"
    _write_status(target, name, status="defined")
    status_path = target / ".specle" / "changes" / name / "status.json"
    source = tmp_path / "status-source.json"
    source.write_text(status_path.read_text())
    status_path.unlink()
    status_path.symlink_to(source)

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_reports_a_non_regular_status_before_reading_it(tmp_path: Path) -> None:
    target = tmp_path / "project"
    name = "example"
    directory = target / ".specle" / "changes" / name
    directory.mkdir(parents=True)
    (directory / "status.json").symlink_to(tmp_path, target_is_directory=True)

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {"invalid-runtime-state"}
    assert "not a regular file" in diagnostics[0].message


@pytest.mark.anyio
async def test_runtime_validation_reports_malformed_reciprocal_relationship(
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

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "invalid-sidecar-relationship",
        "missing-reciprocal-sidecar",
    }


@pytest.mark.anyio
async def test_runtime_validation_reports_an_orphaned_sidecar_relationship(
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

    diagnostics = await validate_runtime_records(target, _runtime_skills())

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "missing-reciprocal-parent"
    }


@pytest.mark.anyio
async def test_runtime_validation_preserves_legacy_archived_relationships(
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

    assert await validate_runtime_records(target, _runtime_skills()) == ()


@pytest.mark.anyio
async def test_reports_a_broken_current_change_symlink(tmp_path: Path) -> None:
    target = tmp_path / "project"
    _write_status(target, "example", status="defined")
    selector = target / ".specle" / "current-change"
    selector.symlink_to(tmp_path / "missing-current-change")

    diagnostics = await validate_runtime_records(target, _runtime_skills())

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
