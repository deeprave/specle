from pathlib import Path

from specle.inventory import read_skill_metadata


def test_reads_managed_skill_metadata(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
specle_group: Planning
requires: [onboard, spec]
---

# Sample
"""
    )

    metadata = read_skill_metadata(skill)

    assert metadata.name == "sample"
    assert metadata.specle_group == "Planning"
    assert metadata.requires == ("onboard", "spec")


def test_every_packaged_skill_declares_a_specle_group() -> None:
    source_root = Path(__file__).parents[1] / "src" / "specle" / "skills"

    metadata = [read_skill_metadata(path) for path in source_root.glob("*/SKILL.md")]

    assert metadata
    assert all(skill.specle_group for skill in metadata)
