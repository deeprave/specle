import json
import stat
from pathlib import Path

import anyio
import pytest

from specle.inventory import SkillMetadataError
from specle.main import build_parser, main


def test_parser_accepts_init_target_and_force() -> None:
    args = build_parser().parse_args(["init", "/work/example", "--force"])

    assert args.command == "init"
    assert args.target_directory == "/work/example"
    assert args.force is True


def test_parser_requires_an_explicit_init_target() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["init"])


def test_parser_accepts_an_explicit_update_target_with_options() -> None:
    args = build_parser().parse_args(
        ["update", "/work/example", "--dry-run", "--yes", "--force"]
    )

    assert args.command == "update"
    assert args.target_directory == "/work/example"
    assert args.dry_run is True
    assert args.yes is True
    assert args.force is True


def test_update_dry_run_reports_a_valid_deployment_without_writing(
    tmp_path, capsys
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()

    anyio.run(main, ["update", str(target), "--dry-run"])

    output = capsys.readouterr().out
    assert "detected version:" in output
    assert "deployment is already current" in output
    assert "dry run: no changes made" in output


def test_force_dry_run_describes_bypass_as_prospective(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()

    anyio.run(main, ["update", str(target), "--dry-run", "--force"])

    assert "would be bypassed" in capsys.readouterr().out


def test_update_validates_the_target_after_applying_managed_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    (target / ".agents" / "policies" / "testing.md").write_text(
        "---\nspecle_policy: true\n---\n\n# Locally modified\n"
    )
    anyio.run(main, ["update", str(target), "--yes"])

    output = capsys.readouterr().out
    assert f"validated {target.resolve()}" in output
    assert "updated deployment" in output


def test_update_reports_all_conflicts_without_mutating(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    policy = target / ".agents" / "policies" / "testing.md"
    policy.write_text("---\nspecle_policy: true\n---\n\n# Locally modified\n")
    with pytest.raises(SystemExit) as error:
        anyio.run(main, ["update", str(target)])

    assert error.value.code == 1
    assert policy.read_text() == "---\nspecle_policy: true\n---\n\n# Locally modified\n"
    output = capsys.readouterr().out
    assert "confirm upgrade: policies/testing.md" in output
    assert "no changes made" in output


def test_update_yes_applies_a_reported_conflict(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    policy = target / ".agents" / "policies" / "testing.md"
    policy.write_text("---\nspecle_policy: true\n---\n\n# Locally modified\n")

    anyio.run(main, ["update", str(target), "--yes"])

    assert "updated deployment" in capsys.readouterr().out
    assert policy.read_text() != "---\nspecle_policy: true\n---\n\n# Locally modified\n"


def test_parser_accepts_an_explicit_validate_target() -> None:
    args = build_parser().parse_args(["validate", "/work/example", "--verbose"])

    assert args.command == "validate"
    assert args.target_directory == "/work/example"
    assert args.verbose is True


def test_parser_accepts_changes_json_and_archive() -> None:
    args = build_parser().parse_args(["changes", "--archive", "--json", "--pretty"])

    assert args.command == "changes"
    assert args.archive is True
    assert args.json is True
    assert args.pretty is True


def test_parser_requires_an_explicit_index_target() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["index"])


def test_changes_json_reports_active_records(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    change = target / ".specle" / "changes" / "example"
    change.mkdir(parents=True)
    change.joinpath("status.json").write_text(
        """{"$schema":"specle://schemas/change-status/1.0","kind":"change","status":"defined","created_at":1,"activated_at":null,"progress":{},"verification":{"status":"not-run"},"review":{"status":"not-run"},"delivery":null,"relationships":[],"dependencies":[]}"""
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--json"])

    result = json.loads(capsys.readouterr().out)
    assert result["collection"] == "active"
    assert result["changes"] == [
        {
            "name": "example",
            "kind": "change",
            "status": "defined",
            "dependencies": [],
            "timestamp": 1,
            "next_action": "activate",
        }
    ]


def test_changes_pretty_json_uses_two_space_indentation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)

    anyio.run(main, ["changes", "--json", "--pretty"])

    assert (
        capsys.readouterr().out == '{\n  "collection": "active",\n  "changes": []\n}\n'
    )


def test_changes_text_and_csv_use_headered_dates(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "changes" / "active" / "status.json",
        kind="change",
        status="defined",
        created_at=0,
    )
    _write_change_status(
        target / ".specle" / "archive" / "archived" / "status.json",
        kind="change",
        status="complete",
        created_at=0,
        archived_at=86_400,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes"])

    assert capsys.readouterr().out == (
        "name\tdate\tkind\tstatus\tdependencies\tnext_action\n"
        "active\t1970-01-01\tchange\tdefined\t—\tactivate\n"
    )

    anyio.run(main, ["changes", "--archive", "--json"])

    assert json.loads(capsys.readouterr().out) == {
        "collection": "archive",
        "changes": [
            {
                "name": "archived",
                "kind": "change",
                "status": "complete",
                "dependencies": [],
                "timestamp": 86_400,
                "next_action": None,
            }
        ],
    }

    anyio.run(main, ["changes", "--archive", "--csv"])

    assert capsys.readouterr().out == (
        "name,date,kind,status,dependencies,next_action\r\n"
        "archived,1970-01-02,change,complete,,\r\n"
    )


def test_changes_reports_spiking_next_action(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "changes" / "investigate" / "status.json",
        kind="spike",
        status="spiking",
        created_at=0,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--json"])

    assert json.loads(capsys.readouterr().out)["changes"][0]["next_action"] == "spike"


def test_changes_reports_local_sidecars_and_stale_registry(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _write_change_status(
        tmp_path / ".specle/changes/repair/status.json",
        kind="bugfix",
        status="building",
        created_at=0,
    )
    (tmp_path / ".specle/current-sidecars").write_text("repair\nmissing\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["changes", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert result["active_sidecars"] == ["repair"]
    assert result["sidecar_diagnostics"] == ["stale sidecar: missing"]
    anyio.run(main, ["changes", "--csv"])
    output = capsys.readouterr()
    assert "local_active" in output.out
    assert "stale sidecar: missing" in output.err


def test_changes_rejects_invalid_registry_entries_without_echoing_them(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / ".specle").mkdir()
    (tmp_path / ".specle/current-sidecars").write_text("bad\tname\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["changes", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert result["active_sidecars"] == []
    assert result["sidecar_diagnostics"] == ["invalid sidecar registry entry"]


def test_changes_reports_activation_for_prepared_sidecar(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _write_change_status(
        tmp_path / ".specle/changes/repair/status.json",
        kind="bugfix",
        status="planned",
        created_at=0,
    )
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["changes", "--json"])
    assert (
        json.loads(capsys.readouterr().out)["changes"][0]["next_action"] == "activate"
    )


def test_changes_rejects_archive_records_without_archived_at(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    status_path = target / ".specle" / "archive" / "incomplete" / "status.json"
    _write_change_status(
        status_path,
        kind="change",
        status="complete",
        created_at=0,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--archive", "--json"])

    assert json.loads(capsys.readouterr().out)["changes"][0]["timestamp"] is None


def test_changes_does_not_modify_durable_state(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    status_path = target / ".specle" / "changes" / "example" / "status.json"
    _write_change_status(
        status_path,
        kind="change",
        status="defined",
        created_at=0,
    )
    before = status_path.read_text()
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--csv"])

    capsys.readouterr()
    assert status_path.read_text() == before


def test_changes_rejects_combined_csv_and_json() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["changes", "--csv", "--json"])


def test_changes_excludes_complete_records_and_orders_dependencies(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "changes" / "zeta" / "status.json",
        kind="change",
        status="defined",
        created_at=0,
        dependencies=["first", "second"],
    )
    _write_change_status(
        target / ".specle" / "changes" / "alpha" / "status.json",
        kind="change",
        status="defined",
        created_at=0,
    )
    _write_change_status(
        target / ".specle" / "changes" / "complete" / "status.json",
        kind="change",
        status="complete",
        created_at=0,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes"])

    assert capsys.readouterr().out.splitlines() == [
        "name\tdate\tkind\tstatus\tdependencies\tnext_action",
        "alpha\t1970-01-01\tchange\tdefined\t—\tactivate",
        "zeta\t1970-01-01\tchange\tdefined\tfirst,second\tactivate",
    ]


def test_changes_reports_empty_text_and_header_only_csv(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)

    anyio.run(main, ["changes"])

    assert capsys.readouterr().out == "no active changes\n"

    anyio.run(main, ["changes", "--archive", "--csv"])

    assert (
        capsys.readouterr().out == "name,date,kind,status,dependencies,next_action\r\n"
    )


def test_changes_uses_cancelled_at_when_available(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "archive" / "cancelled" / "status.json",
        kind="change",
        status="cancelled",
        created_at=0,
        cancelled_at=86_400,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--archive", "--csv"])

    assert capsys.readouterr().out.endswith(
        "cancelled,1970-01-02,change,cancelled,,\r\n"
    )


def test_changes_reports_non_finite_timestamps_as_diagnostics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    status_path = target / ".specle" / "changes" / "bad" / "status.json"
    _write_change_status(
        status_path,
        kind="change",
        status="defined",
        created_at=float("nan"),
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--csv"])

    assert capsys.readouterr().out.endswith(
        "bad,,change,defined,,activate,invalid created_at\r\n"
    )


def test_changes_reports_malformed_records_alongside_valid_rows(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "changes" / "valid" / "status.json",
        kind="change",
        status="defined",
        created_at=0,
    )
    invalid_path = target / ".specle" / "changes" / "invalid" / "status.json"
    invalid_path.parent.mkdir(parents=True)
    invalid_path.write_text("{")
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--json"])

    rows = json.loads(capsys.readouterr().out)["changes"]
    assert [row["name"] for row in rows] == ["invalid", "valid"]
    assert rows[0]["diagnostic"] == "malformed JSON"
    assert "diagnostic" not in rows[1]


def test_changes_reports_schema_invalid_records_alongside_valid_rows(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle" / "changes" / "valid" / "status.json",
        kind="change",
        status="defined",
        created_at=0,
    )
    invalid_path = target / ".specle" / "changes" / "invalid" / "status.json"
    invalid_path.parent.mkdir(parents=True)
    invalid_path.write_text('{"$schema":"specle://schemas/change-status/1.0"}')
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--json"])

    rows = json.loads(capsys.readouterr().out)["changes"]
    assert [row["name"] for row in rows] == ["invalid", "valid"]
    assert rows[0]["diagnostic"] == "invalid contract"
    assert "diagnostic" not in rows[1]


def test_changes_reports_unrenderable_timestamps_as_diagnostic_rows(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    status_path = target / ".specle" / "changes" / "oversized" / "status.json"
    _write_change_status(
        status_path,
        kind="change",
        status="defined",
        created_at=10**400,
    )
    monkeypatch.chdir(target)

    anyio.run(main, ["changes", "--json"])

    row = json.loads(capsys.readouterr().out)["changes"][0]
    assert row["timestamp"] is None
    assert row["diagnostic"] == "invalid created_at"


def test_index_regenerates_only_the_installed_index(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    index = target / ".agents" / "skills" / "specle" / "index.json"
    skill = target / ".agents" / "skills" / "define" / "SKILL.md"
    skill.write_text(
        skill.read_text().replace(
            "  Create or refine evidence-led, unselected normal change definitions under `.specle/changes/`.",
            "  Local description for this installation.",
        )
    )
    original_skill = skill.read_text()
    index.write_text("{}\n")

    anyio.run(main, ["index", str(target)])

    groups = json.loads(index.read_text())["groups"]
    entries = [entry for group in groups for entry in group["skills"]]
    assert (
        next(entry for entry in entries if entry["name"] == "define")["description"]
        == "Local description for this installation."
    )
    assert skill.read_text() == original_skill
    assert stat.S_IMODE(index.stat().st_mode) == 0o644


def test_index_preserves_existing_index_without_a_managed_specle_skill(
    tmp_path: Path, capsys
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    index = target / ".agents" / "skills" / "specle" / "index.json"
    index.write_text('{"previous": true}\n')
    (target / ".agents" / "skills" / "specle" / "SKILL.md").unlink()

    with pytest.raises(SystemExit):
        anyio.run(main, ["index", str(target)])

    assert index.read_text() == '{"previous": true}\n'


def test_index_preserves_a_colliding_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    directory = target / ".agents" / "skills" / "specle"
    collision = directory / ".index.json.existing.tmp"
    collision.write_text("preserve this\n")
    identifiers = iter(("existing", "fresh"))

    class Identifier:
        def __init__(self, value: str) -> None:
            self.hex = value

    monkeypatch.setattr("specle.main.uuid4", lambda: Identifier(next(identifiers)))
    anyio.run(main, ["index", str(target)])

    assert collision.read_text() == "preserve this\n"


def test_index_preserves_existing_index_with_an_invalid_managed_specle_skill(
    tmp_path: Path, capsys
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    index = target / ".agents" / "skills" / "specle" / "index.json"
    index.write_text('{"previous": true}\n')
    (target / ".agents" / "skills" / "specle" / "SKILL.md").write_text(
        "---\nname: another-skill\nspecle_group: Workflow\n"
        "description: invalid\nusage: invalid\n---\n"
    )

    with pytest.raises(SystemExit):
        anyio.run(main, ["index", str(target)])

    assert index.read_text() == '{"previous": true}\n'


def test_index_rejects_a_directory_destination(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    index = target / ".agents" / "skills" / "specle" / "index.json"
    index.unlink()
    index.mkdir()

    with pytest.raises(SystemExit):
        anyio.run(main, ["index", str(target)])

    assert index.is_dir()


def _write_change_status(
    path: Path,
    *,
    kind: str,
    status: str,
    created_at: float,
    archived_at: float | None = None,
    cancelled_at: float | None = None,
    dependencies: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True)
    record: dict[str, object] = {
        "$schema": "specle://schemas/change-status/1.0",
        "kind": kind,
        "status": status,
        "created_at": created_at,
        "activated_at": None,
        "progress": {},
        "verification": {"status": "not-run"},
        "review": {"status": "not-run"},
        "delivery": None,
        "relationships": [],
        "dependencies": dependencies or [],
    }
    if archived_at is not None:
        record["archived_at"] = archived_at
    if cancelled_at is not None:
        record["cancelled_at"] = cancelled_at
    path.write_text(json.dumps(record))


def test_parser_accepts_blueprint_validate_mode() -> None:
    args = build_parser().parse_args(["validate", "--blueprint", "--verbose"])

    assert args.command == "validate"
    assert args.target_directory is None
    assert args.blueprint is True
    assert args.verbose is True


def test_validate_requires_an_explicit_mode() -> None:
    with pytest.raises(SystemExit):
        anyio.run(main, ["validate"])


def test_validate_blueprint_mode_requires_no_installed_target(capsys) -> None:
    anyio.run(main, ["validate", "--blueprint"])

    assert "validated blueprint" in capsys.readouterr().out


def test_validate_reports_blueprint_inspection_errors_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    async def fail_scan(*_args: object) -> None:
        raise SkillMetadataError("invalid packaged blueprint")

    monkeypatch.setattr("specle.main.scan_managed_inventory", fail_scan)

    with pytest.raises(SystemExit, match="1"):
        anyio.run(main, ["validate", "--blueprint"])

    assert capsys.readouterr().out == "invalid packaged blueprint\n"


def test_validate_rejects_combined_modes() -> None:
    with pytest.raises(SystemExit):
        anyio.run(main, ["validate", "--blueprint", "/work/example"])


def test_parser_accepts_schema_export_destination_and_force() -> None:
    args = build_parser().parse_args(["schemas", "export", "/work/schemas", "--force"])

    assert args.command == "schemas"
    assert args.schemas_command == "export"
    assert args.destination == "/work/schemas"
    assert args.force is True


def test_parser_accepts_manifest_output() -> None:
    args = build_parser().parse_args(["manifest", "/work/manifest"])

    assert args.command == "manifest"
    assert args.output == "/work/manifest"


def test_manifest_writes_an_explicit_output(tmp_path, capsys) -> None:
    output = tmp_path / "manifest"

    anyio.run(main, ["manifest", str(output)])

    assert output.is_file()
    assert "appended" in capsys.readouterr().out


def test_manifest_uses_package_version(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "manifest"
    monkeypatch.setattr("specle.main.__version__", "9.8.7")

    anyio.run(main, ["manifest", str(output)])

    assert output.read_text().startswith("9.8.7:")


def test_init_uses_the_explicit_target(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_directory = tmp_path / "current"
    target = tmp_path / "target"
    current_directory.mkdir()
    target.mkdir()
    monkeypatch.chdir(current_directory)

    anyio.run(main, ["init", str(target)])

    assert (target / ".agents" / "skills" / "define" / "SKILL.md").is_file()
    assert not (target / ".agents" / "manifest").exists()
    assert not (current_directory / ".agents").exists()


def test_validate_reports_an_invalid_target_without_writing(
    tmp_path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "target"
    target.mkdir()

    with pytest.raises(SystemExit, match="1"):
        anyio.run(main, ["validate", str(target)])

    assert "installed skill inventory is unavailable" in capsys.readouterr().out
    assert not (target / ".agents").exists()


def test_validate_ignores_malformed_optional_context(tmp_path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    capsys.readouterr()
    context = target / ".specle" / "context.json"
    context.write_text("not valid json\n")

    anyio.run(main, ["validate", str(target)])

    assert capsys.readouterr().out == f"validated {target.resolve()}\n"


def test_validate_rejects_a_non_regular_generated_index(
    tmp_path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    index = target / ".agents" / "skills" / "specle" / "index.json"
    index.unlink()
    index.symlink_to(tmp_path, target_is_directory=True)

    with pytest.raises(SystemExit, match="1"):
        anyio.run(main, ["validate", str(target)])

    assert "not a regular file" in capsys.readouterr().out


def test_validate_reports_managed_inventory_drift(tmp_path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    (target / ".agents" / "policies" / "testing.md").write_text(
        "---\nspecle_policy: true\n---\n\nmodified\n"
    )

    with pytest.raises(SystemExit, match="1"):
        anyio.run(main, ["validate", str(target)])

    assert "modified managed resource" in capsys.readouterr().out


def test_schema_export_uses_the_explicit_destination(tmp_path, capsys) -> None:
    destination = tmp_path / "schemas"

    anyio.run(main, ["schemas", "export", str(destination)])

    assert (destination / "change-status" / "1.0.json").is_file()
    assert str(destination) in capsys.readouterr().out


def test_init_installs_the_context_policy(tmp_path, capsys) -> None:
    target = tmp_path / "target"
    target.mkdir()

    anyio.run(main, ["init", str(target)])

    source = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    assert (target / ".agents" / "policies" / "context.md").read_text() == (
        source / "policies" / "context.md"
    ).read_text()
    assert (target / ".agents" / "policies" / "external-inputs.md").read_text() == (
        source / "policies" / "external-inputs.md"
    ).read_text()


def test_changes_excludes_invalid_names_and_rejects_invalid_dependencies(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "target"
    _write_change_status(
        target / ".specle/changes/bad\tname/status.json",
        kind="change",
        status="defined",
        created_at=0,
    )
    _write_change_status(
        target / ".specle/changes/valid/status.json",
        kind="change",
        status="defined",
        created_at=0,
        dependencies=["bad\tdependency"],
    )
    monkeypatch.chdir(target)
    anyio.run(main, ["changes"])
    output = capsys.readouterr().out
    assert "bad\tname" not in output
    assert "bad\tdependency" not in output
    assert "valid" in output
    assert "invalid dependencies" in output
    assert str(target) not in output


@pytest.mark.parametrize(
    "relative", [".specle/changes", ".specle/archive", ".agents", ".agents/skills"]
)
def test_changes_preflight_rejects_non_directory(
    tmp_path: Path, monkeypatch, relative: str
) -> None:
    bad = tmp_path / relative
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("not a directory")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="expected a directory"):
        anyio.run(main, ["changes"])


def test_changes_reports_invalid_selector(tmp_path: Path, monkeypatch) -> None:
    selector = tmp_path / ".specle/current-change"
    selector.parent.mkdir()
    selector.write_text("invalid/name\n")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="selector"):
        anyio.run(main, ["changes"])


def test_selected_change_next_action_uses_preparation_artifacts(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    directory = tmp_path / ".specle/changes/example"
    _write_change_status(
        directory / "status.json", kind="change", status="defined", created_at=0
    )
    (tmp_path / ".specle/current-change").write_text("example\n")
    monkeypatch.chdir(tmp_path)
    for filename, contents, expected in [
        (None, "", "estimate"),
        ("estimate.md", "## T-shirt size\n\nS\n", "tasks"),
        ("tasks.md", "- [ ] 1. Work\n", "build"),
    ]:
        if filename:
            (directory / filename).write_text(contents)
        anyio.run(main, ["changes", "--json"])
        assert (
            json.loads(capsys.readouterr().out)["changes"][0]["next_action"] == expected
        )


@pytest.mark.parametrize(
    "status,field,value",
    [
        ("complete", "archived_at", "invalid"),
        ("cancelled", "cancelled_at", 10**400),
        ("building", "archived_at", 100),
    ],
)
def test_archive_invalid_or_inapplicable_dates_are_empty(
    tmp_path: Path, monkeypatch, capsys, status: str, field: str, value: object
) -> None:
    status_path = tmp_path / ".specle/archive/example/status.json"
    _write_change_status(status_path, kind="change", status=status, created_at=0)
    record = json.loads(status_path.read_text())
    record[field] = value
    status_path.write_text(json.dumps(record))
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["changes", "--archive", "--json"])
    row = json.loads(capsys.readouterr().out)["changes"][0]
    assert row["timestamp"] is None
    assert "diagnostic" not in row


def test_index_force_reports_lifecycle_diagnostics_and_regenerates(
    tmp_path: Path, capsys
) -> None:
    anyio.run(main, ["init", str(tmp_path)])
    capsys.readouterr()
    skill = tmp_path / ".agents/skills/activate/SKILL.md"
    skill.write_text(
        skill.read_text().replace("      next: estimate", "      next: missing-skill")
    )
    index = tmp_path / ".agents/skills/specle/index.json"
    index.write_text("{}")
    with pytest.raises(SystemExit):
        anyio.run(main, ["index", str(tmp_path)])
    assert index.read_text() == "{}"
    captured = capsys.readouterr()
    assert "missing-skill" in captured.err
    anyio.run(main, ["index", str(tmp_path), "--force"])
    captured = capsys.readouterr()
    assert "missing-skill" in captured.err
    assert json.loads(index.read_text())["groups"]
