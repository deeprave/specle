from pathlib import Path

import pytest

from specle.inventory import SkillInstallationError, install_skill


def test_protected_destination_prevents_all_installation_writes(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_skill(source_root, "base", requires="[]")
    _write_skill(source_root, "release", requires="[base]")
    protected = target_root / "release" / "SKILL.md"
    protected.parent.mkdir(parents=True)
    protected.write_text("# External skill\n")

    with pytest.raises(SkillInstallationError, match="protected"):
        install_skill(source_root, target_root, "release")

    assert not (target_root / "base" / "SKILL.md").exists()
    assert protected.read_text() == "# External skill\n"


def test_installs_requested_skill_and_dependencies_unchanged(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_skill(source_root, "base", requires="[]")
    _write_skill(source_root, "release", requires="[base]")

    installed = install_skill(source_root, target_root, "release")

    assert installed == (
        target_root / "base" / "SKILL.md",
        target_root / "release" / "SKILL.md",
    )
    assert (target_root / "base" / "SKILL.md").read_text() == (
        source_root / "base" / "SKILL.md"
    ).read_text()
    assert (target_root / "release" / "SKILL.md").read_text() == (
        source_root / "release" / "SKILL.md"
    ).read_text()


def _write_skill(root: Path, name: str, *, requires: str) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"""---
name: {name}
specle_group: Testing
requires: {requires}
---

# {name}
"""
    )
