import anyio
import pytest

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


def test_parser_requires_an_explicit_validate_target() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["validate"])


def test_parser_accepts_schema_export_destination_and_force() -> None:
    args = build_parser().parse_args(["schemas", "export", "/work/schemas", "--force"])

    assert args.command == "schemas"
    assert args.schemas_command == "export"
    assert args.destination == "/work/schemas"
    assert args.force is True


@pytest.mark.parametrize("command", ["install", "update"])
def test_parser_rejects_retired_commands(command: str) -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([command])


def test_init_uses_the_explicit_target(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_directory = tmp_path / "current"
    target = tmp_path / "target"
    current_directory.mkdir()
    target.mkdir()
    monkeypatch.chdir(current_directory)

    anyio.run(main, ["init", str(target)])

    assert (target / ".agents" / "skills" / "spec" / "SKILL.md").is_file()
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


def test_schema_export_uses_the_explicit_destination(tmp_path, capsys) -> None:
    destination = tmp_path / "schemas"

    anyio.run(main, ["schemas", "export", str(destination)])

    assert (destination / "spec-status" / "1.0.json").is_file()
    assert str(destination) in capsys.readouterr().out
