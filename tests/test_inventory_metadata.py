from pathlib import Path

import pytest

from specle.inventory import SkillMetadataError, discover_skills, read_skill_metadata


def test_reads_managed_skill_metadata(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
requires: [onboard, spec]
---

# Sample
"""
    )

    metadata = read_skill_metadata(skill)

    assert metadata.name == "sample"
    assert metadata.specle_group == "Planning"
    assert metadata.description == "A test skill."
    assert metadata.usage == "Use this test skill for metadata coverage."
    assert metadata.requires == ("onboard", "spec")


def test_every_packaged_skill_declares_a_specle_group() -> None:
    source_root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"

    metadata = [read_skill_metadata(path) for path in source_root.glob("*/SKILL.md")]

    assert metadata
    assert all(skill.specle_group for skill in metadata)


def test_rejects_missing_description_or_usage(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
specle_group: Planning
requires: []
---
"""
    )

    with pytest.raises(SkillMetadataError, match="description"):
        read_skill_metadata(skill)


def test_discovers_every_valid_skill_and_rejects_mismatched_names(
    tmp_path: Path,
) -> None:
    valid = tmp_path / "valid" / "SKILL.md"
    valid.parent.mkdir()
    valid.write_text(
        """---
name: valid
description: Valid skill.
usage: Use for discovery tests.
specle_group: Planning
requires: []
---
"""
    )
    invalid = tmp_path / "wrong-name" / "SKILL.md"
    invalid.parent.mkdir()
    invalid.write_text(
        """---
name: different
description: Invalid skill.
usage: Use for discovery tests.
specle_group: Planning
requires: []
---
"""
    )

    with pytest.raises(SkillMetadataError, match="does not match"):
        discover_skills(tmp_path)
