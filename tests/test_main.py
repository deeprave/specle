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
