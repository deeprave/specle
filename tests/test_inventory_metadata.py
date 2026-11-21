from collections.abc import Iterable
from pathlib import Path

import pytest

from specle import inventory
from specle.inventory import (
    SkillMetadataError,
    discover_installed_specle_skills,
    discover_skills,
    read_skill_metadata,
)


def test_reads_managed_skill_metadata(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
requires:
  - onboard
  - spec
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


def test_rejects_a_non_regular_skill_file_before_reading_it(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.symlink_to(tmp_path, target_is_directory=True)

    with pytest.raises(SkillMetadataError, match="not a regular file"):
        read_skill_metadata(skill)


def test_every_packaged_skill_declares_a_specle_group() -> None:
    source_root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"

    metadata = [read_skill_metadata(path) for path in source_root.glob("*/SKILL.md")]

    assert metadata
    assert all(skill.specle_group for skill in metadata)


def test_lifecycle_owners_declare_lifecycle_metadata() -> None:
    project_root = Path(__file__).parents[1]
    source_root = project_root / "src" / "specle" / "blueprints" / "skills"
    lifecycle_owners = {
        "activate",
        "bugfix",
        "build",
        "commit",
        "complete",
        "design",
        "estimate",
        "prepare",
        "refactor",
        "resolve",
        "review",
        "revise",
        "spec",
        "spike",
        "tasks",
        "triage",
        "verify",
    }

    metadata = {
        skill.name: skill
        for skill in (
            read_skill_metadata(path) for path in source_root.glob("*/SKILL.md")
        )
    }

    assert lifecycle_owners <= metadata.keys()
    assert all(metadata[name].lifecycle is not None for name in lifecycle_owners)


def test_active_managed_skill_metadata_matches_its_blueprint() -> None:
    project_root = Path(__file__).parents[1]
    source_root = project_root / "src" / "specle" / "blueprints" / "skills"
    active_root = project_root / ".agents" / "skills"

    source = _metadata_by_directory(source_root.glob("*/SKILL.md"))
    active = _metadata_by_directory(
        path
        for path in active_root.glob("*/SKILL.md")
        if inventory._has_specle_group(path)
    )

    assert active == source


def test_rejects_missing_description_or_usage(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
specle_group: Planning
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
---
"""
    )

    with pytest.raises(SkillMetadataError, match="does not match"):
        discover_skills(tmp_path)


def test_discovers_only_marked_installed_skills(tmp_path: Path) -> None:
    target = tmp_path / "project"
    marked = target / ".agents" / "skills" / "managed" / "SKILL.md"
    external = target / ".agents" / "skills" / "external" / "SKILL.md"
    marked.parent.mkdir(parents=True)
    external.parent.mkdir(parents=True)
    marked.write_text(
        """---
name: managed
description: Managed test skill.
usage: Use for installed inventory tests.
specle_group: Planning
---
"""
    )
    external.write_text("# External skill\n")

    skills = discover_installed_specle_skills(target)

    assert [skill.name for skill in skills] == ["managed"]


def test_rejects_invalid_marked_installed_skill(tmp_path: Path) -> None:
    target = tmp_path / "project"
    skill = target / ".agents" / "skills" / "managed" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        """---
name: managed
specle_group: Planning
unknown: value
---
"""
    )

    with pytest.raises(SkillMetadataError, match="invalid frontmatter"):
        discover_installed_specle_skills(target)


@pytest.mark.parametrize(
    ("frontmatter", "message"),
    [
        ("unknown: value", "unexpected key"),
        ("name: [sample]", "disallowed"),
        ("requires: sample", "invalid frontmatter"),
    ],
)
def test_rejects_invalid_schema_frontmatter(
    tmp_path: Path, frontmatter: str, message: str
) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        f"""---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
{frontmatter}
---
"""
    )

    with pytest.raises(SkillMetadataError, match=message) as error:
        read_skill_metadata(skill)

    assert str(skill) in str(error.value)


def test_omitted_requires_has_no_dependencies(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
---
"""
    )

    assert read_skill_metadata(skill).requires == ()


def test_reads_lifecycle_declarations(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
lifecycle:
  accepts:
    - defined
  transitions:
    - from: defined
      to: estimated
      next: design
    - from:
        status: planned
        kind: bugfix
        scope: queued
      to: building
      next: verify
---
"""
    )

    lifecycle = read_skill_metadata(skill).lifecycle

    assert lifecycle is not None
    assert lifecycle.accepts == ("defined",)
    assert lifecycle.transitions[0].source.status == "defined"
    assert lifecycle.transitions[0].next_skill == "design"
    assert lifecycle.transitions[1].source.kind == "bugfix"
    assert lifecycle.transitions[1].source.scope == "queued"


def test_rejects_an_unknown_lifecycle_status(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
lifecycle:
  terminal:
    - abandoned
---
"""
    )

    with pytest.raises(SkillMetadataError, match="invalid frontmatter"):
        read_skill_metadata(skill)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "Sample", "invalid skill name"),
        ("description", "''", "empty required metadata value"),
    ],
)
def test_rejects_invalid_required_metadata_values(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    fields = {
        "name": "sample",
        "description": "A test skill.",
        "usage": "Use this test skill for metadata coverage.",
        "specle_group": "Planning",
    }
    fields[field] = value
    skill.write_text(
        "---\n"
        + "\n".join(f"{key}: {item}" for key, item in fields.items())
        + "\n---\n"
    )

    with pytest.raises(SkillMetadataError, match=message):
        read_skill_metadata(skill)


def test_rejects_an_invalid_required_skill_name(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
requires:
  - Invalid
---
"""
    )

    with pytest.raises(SkillMetadataError, match="invalid required skill name"):
        read_skill_metadata(skill)


def _metadata_by_directory(
    paths: Iterable[Path],
) -> dict[str, tuple[str, str, str, str, tuple[str, ...], object | None]]:
    return {
        skill.path.parent.name: (
            skill.name,
            skill.specle_group,
            skill.description,
            skill.usage,
            skill.requires,
            skill.lifecycle,
        )
        for skill in (read_skill_metadata(path) for path in paths)
    }
