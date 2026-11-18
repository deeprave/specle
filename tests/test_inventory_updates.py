from pathlib import Path

from specle.inventory import update_skills


def test_updates_named_managed_skill_without_touching_external_skill(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_skill(source_root, "release", body="# New release\n")
    _write_skill(target_root, "release", body="# Old release\n")
    external = target_root / "external" / "SKILL.md"
    external.parent.mkdir(parents=True)
    external.write_text("# External\n")

    updated = update_skills(source_root, target_root, "release")

    assert updated == (target_root / "release" / "SKILL.md",)
    assert (target_root / "release" / "SKILL.md").read_text() == (
        source_root / "release" / "SKILL.md"
    ).read_text()
    assert external.read_text() == "# External\n"


def test_updates_all_managed_skills_and_ignores_external_skills(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_skill(source_root, "first", body="# New first\n")
    _write_skill(source_root, "second", body="# New second\n")
    _write_skill(target_root, "first", body="# Old first\n")
    _write_skill(target_root, "second", body="# Old second\n")
    external = target_root / "external" / "SKILL.md"
    external.parent.mkdir(parents=True)
    external.write_text("# External\n")

    updated = update_skills(source_root, target_root)

    assert updated == (
        target_root / "first" / "SKILL.md",
        target_root / "second" / "SKILL.md",
    )
    assert (target_root / "first" / "SKILL.md").read_text() == (
        source_root / "first" / "SKILL.md"
    ).read_text()
    assert (target_root / "second" / "SKILL.md").read_text() == (
        source_root / "second" / "SKILL.md"
    ).read_text()
    assert external.read_text() == "# External\n"


def _write_skill(root: Path, name: str, *, body: str) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"""---
name: {name}
specle_group: Testing
requires: []
---

{body}"""
    )
