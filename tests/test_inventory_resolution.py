from pathlib import Path

import pytest

from specle.inventory import (
    SkillMetadataError,
    packaged_skills_root,
    resolve_dependencies,
)


def test_resolves_required_skills_before_requested_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, "base", requires="[]")
    _write_skill(tmp_path, "release", requires="[base]")

    resolved = resolve_dependencies(tmp_path, "release")

    assert [skill.name for skill in resolved] == ["base", "release"]


def test_locates_packaged_skill_inventory() -> None:
    root = packaged_skills_root()

    assert root.joinpath("spec", "SKILL.md").is_file()


def test_rejects_unknown_required_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, "release", requires="[missing]")

    with pytest.raises(SkillMetadataError, match="does not exist"):
        resolve_dependencies(tmp_path, "release")


def test_rejects_dependency_cycle(tmp_path: Path) -> None:
    _write_skill(tmp_path, "first", requires="[second]")
    _write_skill(tmp_path, "second", requires="[first]")

    with pytest.raises(SkillMetadataError, match="dependency cycle"):
        resolve_dependencies(tmp_path, "first")


def _write_skill(root: Path, name: str, *, requires: str) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir()
    path.write_text(
        f"""---
name: {name}
specle_group: Testing
requires: {requires}
---

# {name}
"""
    )
