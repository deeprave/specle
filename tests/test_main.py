from pathlib import Path
from types import SimpleNamespace

import anyio
import pytest

from specle.inventory import SkillInstallationError, SkillMetadataError, UpdateAction
from specle.main import _confirm_update_action, build_parser, main


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
        ["update", "/work/example", "--dry-run", "--force"]
    )

    assert args.command == "update"
    assert args.target_directory == "/work/example"
    assert args.dry_run is True
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
    monkeypatch.setattr("specle.main._confirm_update_action", lambda _action: True)

    anyio.run(main, ["update", str(target)])

    output = capsys.readouterr().out
    assert f"validated {target.resolve()}" in output
    assert "updated deployment" in output


def test_update_confirmation_requires_an_explicit_yes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    action = UpdateAction("upgrade", Path("skills/define/SKILL.md"), True)
    terminal = SimpleNamespace(isatty=lambda: True)
    monkeypatch.setattr("specle.main.sys.stdin", terminal)
    monkeypatch.setattr("specle.main.sys.stdout", terminal)
    monkeypatch.setattr("builtins.input", lambda _prompt: "no")

    assert _confirm_update_action(action) is False

    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")

    assert _confirm_update_action(action) is True


def test_update_confirmation_rejects_non_interactive_streams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    action = UpdateAction("upgrade", Path("skills/define/SKILL.md"), True)
    terminal = SimpleNamespace(isatty=lambda: False)
    monkeypatch.setattr("specle.main.sys.stdin", terminal)
    monkeypatch.setattr("specle.main.sys.stdout", terminal)

    with pytest.raises(
        SkillInstallationError, match="stdin and stdout must both be TTYs"
    ):
        _confirm_update_action(action)


def test_update_refuses_a_conflict_without_interactive_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    anyio.run(main, ["init", str(target)])
    policy = target / ".agents" / "policies" / "testing.md"
    policy.write_text("---\nspecle_policy: true\n---\n\n# Locally modified\n")
    monkeypatch.setattr("specle.main.sys.stdin", SimpleNamespace(isatty=lambda: False))

    with pytest.raises(SystemExit, match="stdin and stdout must both be TTYs"):
        anyio.run(main, ["update", str(target)])

    assert policy.read_text() == "---\nspecle_policy: true\n---\n\n# Locally modified\n"


def test_parser_accepts_an_explicit_validate_target() -> None:
    args = build_parser().parse_args(["validate", "/work/example", "--verbose"])

    assert args.command == "validate"
    assert args.target_directory == "/work/example"
    assert args.verbose is True


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
    def fail_scan(*_args: object) -> None:
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
