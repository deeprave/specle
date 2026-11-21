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
