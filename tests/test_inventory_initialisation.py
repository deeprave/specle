import json
import shutil
from pathlib import Path

import pytest

from specle import inventory
from specle.inventory import SkillInstallationError, initialise_distribution


def test_initialises_a_fresh_project_target_and_generates_an_index(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()

    installed = initialise_distribution(source_root, target)

    skills_root = target / ".agents" / "skills"
    assert (skills_root / "spec" / "SKILL.md").is_file()
    assert (skills_root / "verify" / "SKILL.md").is_file()
    assert (skills_root / "specle" / "resource.json").is_file()
    assert (target / ".agents" / "steering" / "testing.md").is_file()
    index = json.loads((skills_root / "specle" / "index.json").read_text())
    indexed_skills = [skill for group in index["groups"] for skill in group["skills"]]
    assert (
        next(skill for skill in indexed_skills if skill["name"] == "spec")["resource"]
        == (skills_root / "spec" / "SKILL.md").as_uri()
    )
    assert installed[-1] == skills_root / "specle" / "index.json"


def test_initialises_a_home_like_target_without_project_state(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    home = tmp_path / "home"
    home.mkdir()

    initialise_distribution(source_root, home)

    assert (home / ".agents" / "skills" / "spec" / "SKILL.md").is_file()
    assert not (home / ".agents" / "project").exists()
    assert not (home / ".specle").exists()


def test_rejects_a_missing_target_without_creating_any_paths(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "missing"

    with pytest.raises(SkillInstallationError, match="existing directory"):
        initialise_distribution(source_root, target)

    assert not target.exists()


def test_uses_the_explicit_target_not_the_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    current_directory = tmp_path / "current"
    target = tmp_path / "target"
    current_directory.mkdir()
    target.mkdir()
    monkeypatch.chdir(current_directory)

    initialise_distribution(source_root, target)

    assert (target / ".agents" / "skills" / "spec" / "SKILL.md").is_file()
    assert not (current_directory / ".agents").exists()


def test_preserves_project_owned_content_and_unrelated_skills(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    project_document = target / ".agents" / "project" / "README.md"
    runtime_context = target / ".specle" / "context.json"
    external_skill = target / ".agents" / "skills" / "external" / "SKILL.md"
    project_document.parent.mkdir(parents=True)
    runtime_context.parent.mkdir(parents=True)
    external_skill.parent.mkdir(parents=True)
    project_document.write_text("# Project guidance\n")
    runtime_context.write_text("{}\n")
    external_skill.write_text("# External skill\n")

    initialise_distribution(source_root, target)

    assert project_document.read_text() == "# Project guidance\n"
    assert runtime_context.read_text() == "{}\n"
    assert external_skill.read_text() == "# External skill\n"


def test_collision_preflight_makes_no_writes_without_force(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    existing = target / ".agents" / "skills" / "spec" / "SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Existing spec\n")

    with pytest.raises(SkillInstallationError, match="destination already exists"):
        initialise_distribution(source_root, target)

    assert existing.read_text() == "# Existing spec\n"
    assert not (target / ".agents" / "skills" / "verify").exists()
    assert not (target / ".agents" / "steering").exists()


def test_force_replaces_only_exact_managed_destinations(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    managed_skill = target / ".agents" / "skills" / "spec" / "SKILL.md"
    managed_steering = target / ".agents" / "steering" / "testing.md"
    old_index = target / ".agents" / "skills" / "specle" / "index.json"
    old_specle_resource = target / ".agents" / "skills" / "specle" / "resource.json"
    external_skill = target / ".agents" / "skills" / "external" / "SKILL.md"
    project_document = target / ".agents" / "project" / "README.md"
    for path, contents in (
        (managed_skill, "# Old spec\n"),
        (managed_steering, "# Old testing\n"),
        (old_index, "{}\n"),
        (old_specle_resource, '{"version": "old"}\n'),
        (external_skill, "# External skill\n"),
        (project_document, "# Project guidance\n"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    (source_root / "skills" / "specle" / "resource.json").write_text(
        '{"version": "new"}\n'
    )

    initialise_distribution(source_root, target, force=True)

    assert (
        managed_skill.read_text()
        == (source_root / "skills" / "spec" / "SKILL.md").read_text()
    )
    assert (
        managed_steering.read_text()
        == (source_root / "steering" / "testing.md").read_text()
    )
    assert old_index.read_text() != "{}\n"
    assert old_specle_resource.read_text() == '{"version": "new"}\n'
    assert external_skill.read_text() == "# External skill\n"
    assert project_document.read_text() == "# Project guidance\n"


def test_force_prunes_obsolete_managed_skills_but_preserves_unmanaged_skills(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    _write_skill(source_root / "skills", "retired", "Planning")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    retired = target / ".agents" / "skills" / "retired"
    external = target / ".agents" / "skills" / "external" / "SKILL.md"
    external.parent.mkdir(parents=True)
    external.write_text("# External skill\n")
    shutil.rmtree(source_root / "skills" / "retired")

    with pytest.raises(SkillInstallationError, match="retired"):
        initialise_distribution(source_root, target)

    initialise_distribution(source_root, target, force=True)

    assert not retired.exists()
    assert external.read_text() == "# External skill\n"


def test_force_prunes_an_obsolete_skill_with_legacy_flow_style_metadata(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    obsolete = target / ".agents" / "skills" / "retired" / "SKILL.md"
    obsolete.parent.mkdir(parents=True)
    obsolete.write_text("---\nspecle_group: Planning\nrequires: [verify]\n---\n")

    initialise_distribution(source_root, target, force=True)

    assert not obsolete.exists()


def test_staging_failure_preserves_existing_content_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    existing = target / ".agents" / "skills" / "spec" / "SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Existing spec\n")

    def fail_copytree(*args: object, **kwargs: object) -> None:
        raise OSError("copy failed")

    monkeypatch.setattr(inventory.shutil, "copytree", fail_copytree)

    with pytest.raises(SkillInstallationError, match="unable to stage"):
        initialise_distribution(source_root, target, force=True)

    assert existing.read_text() == "# Existing spec\n"
    assert not list((target / ".agents").rglob(".specle-tmp-*"))


def test_index_generation_failure_preserves_the_previous_index_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    index_path = target / ".agents" / "skills" / "specle" / "index.json"
    previous_index = index_path.read_text()

    def fail_index(*args: object, **kwargs: object) -> inventory.SkillIndex:
        raise ValueError("index failed")

    monkeypatch.setattr(inventory, "build_skill_index", fail_index)

    with pytest.raises(SkillInstallationError, match="unable to stage"):
        initialise_distribution(source_root, target, force=True)

    assert index_path.read_text() == previous_index
    assert not list((target / ".agents").rglob(".specle-tmp-*"))


def test_replacement_failure_reports_its_destination_and_preserves_the_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    index_path = target / ".agents" / "skills" / "specle" / "index.json"
    previous_index = index_path.read_text()
    original_replace = inventory._replace_staged_destination

    def fail_first_skill(
        temporary: Path | None,
        destination: Path,
        backups: list[tuple[Path, Path]],
    ) -> None:
        if destination.name == "spec":
            raise OSError("rename failed")
        original_replace(temporary, destination, backups)

    monkeypatch.setattr(inventory, "_replace_staged_destination", fail_first_skill)

    with pytest.raises(SkillInstallationError, match=r"destination.*skills/spec"):
        initialise_distribution(source_root, target, force=True)

    assert index_path.read_text() == previous_index
    assert not list((target / ".agents").rglob(".specle-tmp-*"))


def test_replacement_failure_restores_every_managed_skill_resource_and_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    skills_root = target / ".agents" / "skills"
    spec_directory = skills_root / "spec"
    specle_directory = skills_root / "specle"
    index_path = specle_directory / "index.json"
    previous_spec_resource = (spec_directory / "resource.json").read_text()
    specle_resource = specle_directory / "resource.json"
    previous_specle_resource = '{"version": "old"}\n'
    specle_resource.write_text(previous_specle_resource)
    previous_index = '{"previous": true}\n'
    index_path.write_text(previous_index)
    (source_root / "skills" / "spec" / "resource.json").write_text(
        '{"version": "new"}\n'
    )
    (source_root / "skills" / "specle" / "resource.json").write_text(
        '{"version": "new"}\n'
    )
    original_replace = Path.replace

    def fail_specle_rename(path: Path, destination: Path) -> Path:
        if destination == specle_directory and path.name.startswith(".specle-tmp-"):
            raise OSError("rename failed")
        return original_replace(path, destination)

    monkeypatch.setattr(Path, "replace", fail_specle_rename)

    with pytest.raises(SkillInstallationError, match=r"destination.*skills/specle"):
        initialise_distribution(source_root, target, force=True)

    assert (spec_directory / "resource.json").read_text() == previous_spec_resource
    assert specle_resource.read_text() == previous_specle_resource
    assert index_path.read_text() == previous_index
    assert not list((target / ".agents").rglob(".specle-tmp-*"))
    assert not list((target / ".agents").rglob(".specle-backup-*"))


def test_rollback_failure_retains_and_reports_the_recovery_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    skills_root = target / ".agents" / "skills"
    specle_directory = skills_root / "specle"
    index_path = specle_directory / "index.json"
    previous_specle_resource = '{"version": "old"}\n'
    previous_index = '{"previous": true}\n'
    (specle_directory / "resource.json").write_text(previous_specle_resource)
    index_path.write_text(previous_index)
    steering_path = target / ".agents" / "steering" / "testing.md"
    original_replace = Path.replace

    def fail_replacement_and_restore(path: Path, destination: Path) -> Path:
        if destination == steering_path and path.name.startswith(
            ".specle-tmp-testing.md-"
        ):
            raise OSError("replacement failed")
        if destination == specle_directory and path.name.startswith(
            ".specle-backup-specle-"
        ):
            raise OSError("restore failed")
        return original_replace(path, destination)

    monkeypatch.setattr(Path, "replace", fail_replacement_and_restore)

    with pytest.raises(SkillInstallationError, match="recovery backup") as error:
        initialise_distribution(source_root, target, force=True)

    backups = list(skills_root.glob(".specle-backup-specle-*"))
    assert len(backups) == 1
    assert str(backups[0]) in str(error.value)
    assert (backups[0] / "resource.json").read_text() == previous_specle_resource
    assert (backups[0] / "index.json").read_text() == previous_index


def test_replacement_failure_removes_new_managed_destinations_before_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    steering_path = target / ".agents" / "steering" / "testing.md"
    original_replace = Path.replace

    def fail_steering_replacement(path: Path, destination: Path) -> Path:
        if destination == steering_path and path.name.startswith(
            ".specle-tmp-testing.md-"
        ):
            raise OSError("replacement failed")
        return original_replace(path, destination)

    monkeypatch.setattr(Path, "replace", fail_steering_replacement)

    with pytest.raises(SkillInstallationError, match=r"destination.*steering/testing"):
        initialise_distribution(source_root, target, force=True)

    skills_root = target / ".agents" / "skills"
    assert not (skills_root / "spec").exists()
    assert not (skills_root / "specle").exists()
    assert not (skills_root / "verify").exists()
    assert not list((target / ".agents").rglob(".specle-tmp-*"))

    monkeypatch.setattr(Path, "replace", original_replace)
    initialise_distribution(source_root, target)

    assert (skills_root / "spec" / "SKILL.md").is_file()


def _write_distribution(root: Path) -> Path:
    _write_skill(root / "skills", "spec", "Planning")
    _write_skill(root / "skills", "specle", "Reference")
    _write_skill(root / "skills", "verify", "Quality")
    steering = root / "steering"
    steering.mkdir(parents=True)
    (steering / "testing.md").write_text("# Testing\n")
    return root


def _write_skill(root: Path, name: str, group: str) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"""---
name: {name}
description: {name.title()} skill.
usage: Use {name} for tests.
specle_group: {group}
---

# {name.title()}
"""
    )
    (path.parent / "resource.json").write_text('{"version": "old"}\n')
