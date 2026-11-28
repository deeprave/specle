import json
from collections.abc import Iterable
from pathlib import Path

import pytest

from specle import inventory
from specle.inventory import SkillMetadataError


@pytest.mark.anyio
async def test_reads_managed_skill_metadata(tmp_path: Path) -> None:
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        """---
name: sample
description: A test skill.
usage: Use this test skill for metadata coverage.
specle_group: Planning
requires:
  - onboard
  - define
---

# Sample
"""
    )

    metadata = _metadata(skill)

    assert metadata.name == "sample"
    assert metadata.specle_group == "Planning"
    assert metadata.description == "A test skill."
    assert metadata.usage == "Use this test skill for metadata coverage."
    assert metadata.requires == ("onboard", "define")


@pytest.mark.anyio
async def test_rejects_a_non_regular_skill_file_before_reading_it(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "skills" / "sample" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.symlink_to(tmp_path, target_is_directory=True)

    with pytest.raises(SkillMetadataError, match="not a regular file"):
        await inventory.scan_managed_inventory(tmp_path)


@pytest.mark.anyio
async def test_every_packaged_skill_declares_a_specle_group() -> None:
    source_root = Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "skills"

    metadata = [_metadata(path) for path in source_root.glob("*/SKILL.md")]

    assert metadata
    assert all(skill.specle_group for skill in metadata)


@pytest.mark.anyio
async def test_lifecycle_owners_declare_lifecycle_metadata() -> None:
    project_root = Path(__file__).parents[1]
    source_root = project_root / "src" / "specle" / "blueprints" / "skills"
    lifecycle_owners = {
        "activate",
        "bugfix",
        "build",
        "cancel",
        "commit",
        "complete",
        "design",
        "estimate",
        "prepare",
        "refactor",
        "resolve",
        "review",
        "revise",
        "define",
        "spike",
        "tasks",
        "triage",
        "verify",
    }

    metadata = {
        skill.name: skill
        for skill in (_metadata(path) for path in source_root.glob("*/SKILL.md"))
    }

    assert lifecycle_owners <= metadata.keys()
    assert all(metadata[name].lifecycle is not None for name in lifecycle_owners)


@pytest.mark.anyio
async def test_cancel_skill_transitions_every_active_state_to_cancelled() -> None:
    project_root = Path(__file__).parents[1]
    skill = _metadata(
        project_root
        / "src"
        / "specle"
        / "blueprints"
        / "skills"
        / "cancel"
        / "SKILL.md"
    )

    assert skill.lifecycle is not None
    assert skill.lifecycle.accepts == (
        "defined",
        "estimated",
        "designed",
        "planned",
        "spiking",
        "building",
        "verified",
        "approved",
        "committed",
        "review-findings",
        "triaged",
    )
    assert {
        transition.source.status for transition in skill.lifecycle.transitions
    } == set(skill.lifecycle.accepts)
    assert {transition.target.status for transition in skill.lifecycle.transitions} == {
        "cancelled"
    }
    assert skill.lifecycle.terminal == ("cancelled",)


@pytest.mark.anyio
async def test_active_managed_skill_metadata_matches_its_blueprint() -> None:
    project_root = Path(__file__).parents[1]
    source_root = project_root / "src" / "specle" / "blueprints" / "skills"
    active_root = project_root / ".agents" / "skills"

    source = _metadata_by_directory(source_root.glob("*/SKILL.md"))
    active = _metadata_by_directory(
        path
        for path in active_root.glob("*/SKILL.md")
        if inventory._has_specle_group_text(path.read_text())
    )

    assert active == source


@pytest.mark.anyio
async def test_pending_change_inventory_excludes_removed_skills() -> None:
    project_root = Path(__file__).parents[1]
    blueprint_root = project_root / "src" / "specle" / "blueprints" / "skills"
    installed_root = project_root / ".agents" / "skills"

    blueprint_names = {
        _metadata(path).name for path in blueprint_root.glob("*/SKILL.md")
    }
    installed_names = {
        _metadata(path).name
        for path in installed_root.glob("*/SKILL.md")
        if inventory._has_specle_group_text(path.read_text())
    }
    index = json.loads((installed_root / "specle" / "index.json").read_text())
    indexed_names = {
        skill["name"] for group in index["groups"] for skill in group["skills"]
    }

    assert "changes" in blueprint_names
    assert "changes" in installed_names
    assert "changes" in indexed_names
    assert "changelist" not in blueprint_names | installed_names | indexed_names
    assert "wrapup" not in blueprint_names | installed_names | indexed_names


@pytest.mark.anyio
async def test_rejects_missing_description_or_usage(tmp_path: Path) -> None:
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
        _metadata(skill)


@pytest.mark.anyio
async def test_reads_cancelled_terminal_lifecycle_metadata(tmp_path: Path) -> None:
    skill = tmp_path / "cancel" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(
        """---
name: cancel
specle_group: Integration
description: Cancel one active change.
usage: Use with an explicit change name.
lifecycle:
  accepts:
    - defined
  transitions:
    - from: defined
      to: cancelled
  terminal:
    - cancelled
---
"""
    )

    metadata = _metadata(skill)

    assert metadata.lifecycle is not None
    assert metadata.lifecycle.terminal == ("cancelled",)


@pytest.mark.anyio
async def test_discovers_every_valid_skill_and_rejects_mismatched_names(
    tmp_path: Path,
) -> None:
    skills_root = tmp_path / "skills"
    valid = skills_root / "valid" / "SKILL.md"
    valid.parent.mkdir(parents=True)
    valid.write_text(
        """---
name: valid
description: Valid skill.
usage: Use for discovery tests.
specle_group: Planning
---
"""
    )
    invalid = skills_root / "wrong-name" / "SKILL.md"
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
        await _distribution_skills(skills_root.parent)


@pytest.mark.anyio
async def test_discovers_only_marked_installed_skills(tmp_path: Path) -> None:
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

    skills = await _installed_skills(target)

    assert [skill.name for skill in skills] == ["managed"]


@pytest.mark.parametrize("target_name", ("directory", "missing"))
@pytest.mark.anyio
async def test_rejects_a_non_regular_candidate_installed_skill_file(
    tmp_path: Path, target_name: str
) -> None:
    target = tmp_path / "project"
    valid = target / ".agents" / "skills" / "managed" / "SKILL.md"
    invalid = target / ".agents" / "skills" / "invalid" / "SKILL.md"
    valid.parent.mkdir(parents=True)
    invalid.parent.mkdir(parents=True)
    valid.write_text(
        """---
name: managed
description: Managed test skill.
usage: Use for installed inventory tests.
specle_group: Planning
---
"""
    )
    target_path = tmp_path / target_name
    if target_name == "directory":
        target_path.mkdir()
    invalid.symlink_to(target_path, target_is_directory=True)

    with pytest.raises(SkillMetadataError, match="not a regular file"):
        await _installed_skills(target)


@pytest.mark.anyio
async def test_rejects_invalid_marked_installed_skill(tmp_path: Path) -> None:
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
        await _installed_skills(target)


@pytest.mark.parametrize(
    ("frontmatter", "message"),
    [
        ("unknown: value", "unexpected key"),
        ("name: [sample]", "disallowed"),
        ("requires: sample", "invalid frontmatter"),
    ],
)
@pytest.mark.anyio
async def test_rejects_invalid_schema_frontmatter(
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
        _metadata(skill)

    assert str(skill) in str(error.value)


@pytest.mark.anyio
async def test_omitted_requires_has_no_dependencies(tmp_path: Path) -> None:
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

    assert _metadata(skill).requires == ()


@pytest.mark.anyio
async def test_reads_lifecycle_declarations(tmp_path: Path) -> None:
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

    lifecycle = _metadata(skill).lifecycle

    assert lifecycle is not None
    assert lifecycle.accepts == ("defined",)
    assert lifecycle.transitions[0].source.status == "defined"
    assert lifecycle.transitions[0].next_skill == "design"
    assert lifecycle.transitions[1].source.kind == "bugfix"
    assert lifecycle.transitions[1].source.scope == "queued"


@pytest.mark.anyio
async def test_rejects_an_unknown_lifecycle_status(tmp_path: Path) -> None:
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
        _metadata(skill)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "Sample", "invalid skill name"),
        ("description", "''", "empty required metadata value"),
    ],
)
@pytest.mark.anyio
async def test_rejects_invalid_required_metadata_values(
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
        _metadata(skill)


@pytest.mark.anyio
async def test_rejects_an_invalid_required_skill_name(tmp_path: Path) -> None:
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
        _metadata(skill)


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
        for skill in (_metadata(path) for path in paths)
    }


def _metadata(path: Path) -> inventory.SkillMetadata:
    return inventory._read_skill_metadata(path, path.read_text())


async def _distribution_skills(root: Path) -> tuple[inventory.SkillMetadata, ...]:
    return tuple(
        record.metadata
        for record in (await inventory.scan_managed_inventory(root)).skills
    )


async def _installed_skills(target: Path) -> tuple[inventory.SkillMetadata, ...]:
    return await _distribution_skills(target / ".agents")
