import anyio
import pytest

from specle.main import build_parser, main


def test_parser_accepts_install_command() -> None:
    args = build_parser().parse_args(["install", "release"])

    assert args.command == "install"
    assert args.skill == "release"


def test_install_reports_protected_active_skill(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protected = tmp_path / ".agents" / "skills" / "spec" / "SKILL.md"
    protected.parent.mkdir(parents=True)
    protected.write_text("# External skill\n")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit, match="protected external skill"):
        anyio.run(main, ["install", "spec"])
