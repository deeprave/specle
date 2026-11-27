import json
import shutil
from pathlib import Path

import pytest

from specle import inventory
from specle.inventory import (
    SkillInstallationError,
    build_skill_index,
    compare_managed_inventories,
    initialise_distribution,
    managed_resource_checksums,
    scan_managed_inventory,
    update_distribution,
)
from specle.manifest import (
    append_manifest,
    detect_installed_version,
    read_manifest_generations,
)


def test_initialises_a_fresh_project_target_and_generates_an_index(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()

    installed = initialise_distribution(source_root, target)

    skills_root = target / ".agents" / "skills"
    assert (skills_root / "define" / "SKILL.md").is_file()
    assert (skills_root / "verify" / "SKILL.md").is_file()
    assert (skills_root / "specle" / "resource.json").is_file()
    assert (target / ".agents" / "policies" / "testing.md").is_file()
    assert (
        target / ".specle" / ".gitignore"
    ).read_text() == "/current-change\n/context.json\n"
    index = json.loads((skills_root / "specle" / "index.json").read_text())
    indexed_skills = [skill for group in index["groups"] for skill in group["skills"]]
    assert next(skill for skill in indexed_skills if skill["name"] == "define") == {
        "name": "define",
        "description": "Define skill.",
        "usage": "Use define for tests.",
    }
    assert installed[-1] == skills_root / "specle" / "index.json"


def test_initialises_a_home_like_target_without_project_state(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    home = tmp_path / "home"
    home.mkdir()

    initialise_distribution(source_root, home)

    assert (home / ".agents" / "skills" / "define" / "SKILL.md").is_file()
    assert not (home / ".agents" / "project").exists()
    assert (home / ".specle" / ".gitignore").is_file()


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

    assert (target / ".agents" / "skills" / "define" / "SKILL.md").is_file()
    assert not (current_directory / ".agents").exists()


def test_preserves_project_owned_content_and_unrelated_skills(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    project_document = target / ".agents" / "project" / "README.md"
    runtime_context = target / ".specle" / "context.json"
    steering_document = target / ".agents" / "steering" / "local.md"
    external_skill = target / ".agents" / "skills" / "external" / "SKILL.md"
    project_document.parent.mkdir(parents=True)
    runtime_context.parent.mkdir(parents=True)
    steering_document.parent.mkdir(parents=True)
    external_skill.parent.mkdir(parents=True)
    project_document.write_text("# Project guidance\n")
    runtime_context.write_text("{}\n")
    steering_document.write_text("# Local steering\n")
    external_skill.write_text("# External skill\n")

    initialise_distribution(source_root, target)

    assert project_document.read_text() == "# Project guidance\n"
    assert runtime_context.read_text() == "{}\n"
    assert steering_document.read_text() == "# Local steering\n"
    assert external_skill.read_text() == "# External skill\n"


def test_collision_preflight_makes_no_writes_without_force(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    existing = target / ".agents" / "skills" / "define" / "SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Existing define\n")

    with pytest.raises(SkillInstallationError, match="destination already exists"):
        initialise_distribution(source_root, target)

    assert existing.read_text() == "# Existing define\n"
    assert not (target / ".agents" / "skills" / "verify").exists()
    assert not (target / ".agents" / "policies").exists()


def test_initialisation_preserves_existing_runtime_ignore_rules(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    runtime_ignore = target / ".specle" / ".gitignore"
    runtime_ignore.parent.mkdir(parents=True)
    runtime_ignore.write_text("/agent-cache\n/current-change\n")

    initialise_distribution(source_root, target)

    assert (
        runtime_ignore.read_text() == "/agent-cache\n/current-change\n/context.json\n"
    )


def test_compares_an_installed_distribution_to_its_package_source(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    context = target / ".specle" / "context.json"
    context.write_text('{"local": true}\n')

    assert _compare_distribution(source_root, target) == ()


def test_version_aware_update_previews_and_applies_safe_resource_changes(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    old_inventory = scan_managed_inventory(source_root)
    append_manifest(manifest, old_inventory, "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    context = target / ".specle" / "context.json"
    context.write_text('{"local": true}\n')
    changed = source_root / "skills" / "define" / "resource.json"
    changed.write_text('{"version": "new"}\n')
    (source_root / "policies" / "new.md").write_text(
        "---\nspecle_policy: true\n---\n\n# New\n"
    )
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    preview = update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
        dry_run=True,
    )

    assert {action.action for action in preview.actions} == {"add", "upgrade"}
    assert all(action.requires_confirmation is False for action in preview.actions)
    assert preview.project_guidance == ("project guidance is missing; run onboard",)
    assert (target / ".agents" / "policies" / "new.md").exists() is False
    update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
    )
    assert (target / ".agents" / "skills" / "define" / "resource.json").read_text() == (
        '{"version": "new"}\n'
    )
    assert (target / ".agents" / "policies" / "new.md").is_file()
    assert context.read_text() == '{"local": true}\n'
    assert _compare_distribution(source_root, target) == ()


def test_update_reports_an_unexpected_project_overlay_path_type(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    (target / ".agents" / "project").write_text("not a directory\n")
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    plan = update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
        dry_run=True,
    )

    assert plan.project_guidance == (
        "project guidance has an unexpected path type; run onboard",
    )


def test_version_aware_update_removes_an_unchanged_retired_resource(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    retired_source = source_root / "policies" / "retired.md"
    retired_source.write_text("---\nspecle_policy: true\n---\n\n# Retired\n")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    retired_source.unlink()
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    plan = update_distribution(
        source_root, target, blueprint, installed, generations, detection
    )

    assert any(action.action == "remove" for action in plan.actions)
    assert not (target / ".agents" / "policies" / "retired.md").exists()


def test_retired_skill_with_a_modified_resource_is_removed_atomically(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    skill_directory = target / ".agents" / "skills" / "define"
    (skill_directory / "resource.json").write_text('{"version": "local"}\n')
    shutil.rmtree(source_root / "skills" / "define")
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    result = update_distribution(
        source_root, target, blueprint, installed, generations, detection
    )

    assert result.converged is False
    assert (skill_directory / "SKILL.md").is_file()
    assert (skill_directory / "resource.json").read_text() == '{"version": "local"}\n'


def test_version_aware_update_requires_confirmation_for_unmanaged_policy(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    policy = target / ".agents" / "policies" / "new.md"
    policy.write_text("# Local policy\n")
    (source_root / "policies" / "new.md").write_text(
        "---\nspecle_policy: true\n---\n\n# Package policy\n"
    )
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    declined = update_distribution(
        source_root, target, blueprint, installed, generations, detection
    )

    assert declined.converged is False
    assert policy.read_text() == "# Local policy\n"


def test_version_aware_update_preserves_modified_managed_resources(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    context = target / ".specle" / "context.json"
    context.write_text('{"local": true}\n')
    installed_resource = target / ".agents" / "skills" / "define" / "resource.json"
    installed_resource.write_text('{"version": "local"}\n')
    (source_root / "skills" / "define" / "resource.json").write_text(
        '{"version": "new"}\n'
    )
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    plan = update_distribution(
        source_root, target, blueprint, installed, generations, detection
    )

    assert any(action.requires_confirmation for action in plan.actions)
    assert installed_resource.read_text() == '{"version": "local"}\n'

    update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
        force=True,
    )

    assert installed_resource.read_text() == '{"version": "new"}\n'
    assert context.read_text() == '{"local": true}\n'


def test_conflicted_update_does_not_apply_safe_actions_until_yes(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    installed_skill = target / ".agents" / "skills" / "define" / "SKILL.md"
    installed_skill.write_text(
        installed_skill.read_text().replace("Define skill.", "Local define skill.")
    )
    installed = scan_managed_inventory(target / ".agents")
    index_path = target / ".agents" / "skills" / "specle" / "index.json"
    index_path.write_text(
        json.dumps(
            build_skill_index(tuple(record.metadata for record in installed.skills)),
            indent=2,
        )
        + "\n"
    )
    source_skill = source_root / "skills" / "define" / "SKILL.md"
    source_skill.write_text(
        source_skill.read_text().replace("Define skill.", "Updated define skill.")
    )
    (source_root / "policies" / "new.md").write_text(
        "---\nspecle_policy: true\n---\n\n# New\n"
    )
    blueprint = scan_managed_inventory(source_root)
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    result = update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
    )

    assert result.converged is False
    assert not (target / ".agents" / "policies" / "new.md").exists()
    assert json.loads(index_path.read_text()) == build_skill_index(
        tuple(record.metadata for record in installed.skills)
    )
    accepted = update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
        approve_conflicts=True,
    )

    assert accepted.converged is True
    assert (target / ".agents" / "policies" / "new.md").is_file()


def test_version_aware_update_requires_confirmation_for_an_unmarked_skill(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    shutil.rmtree(source_root / "skills" / "define")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    unmarked_skill = target / ".agents" / "skills" / "define" / "SKILL.md"
    unmarked_skill.parent.mkdir(parents=True)
    unmarked_skill.write_text("# Local skill\n")
    _write_skill(source_root / "skills", "define", "Planning")
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        {
            resource.path: resource.checksum
            for skill in installed.skills
            for resource in skill.resources
        }
        | {resource.path: resource.checksum for resource in installed.resources},
        generations,
    )

    declined = update_distribution(
        source_root, target, blueprint, installed, generations, detection
    )

    assert declined.converged is False
    assert unmarked_skill.read_text() == "# Local skill\n"
    accepted = update_distribution(
        source_root,
        target,
        blueprint,
        installed,
        generations,
        detection,
        approve_conflicts=True,
    )
    assert accepted.converged is True
    assert "specle_group: Planning" in unmarked_skill.read_text()
    assert _compare_distribution(source_root, target) == ()


def test_reports_each_missing_skill_for_an_empty_installed_inventory(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    (target / ".agents" / "skills").mkdir(parents=True)

    diagnostics = _compare_distribution(source_root, target)

    assert diagnostics == (
        "missing managed resource (requires update): policies/testing.md",
        "missing managed skill (requires update): define",
        "missing managed skill (requires update): specle",
        "missing managed skill (requires update): verify",
    )


def test_scans_package_and_installed_roots_into_matching_records(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)

    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")

    assert [record.metadata.name for record in installed.skills] == [
        record.metadata.name for record in blueprint.skills
    ]
    assert [record.resources for record in installed.skills] == [
        record.resources for record in blueprint.skills
    ]
    assert installed.resources == blueprint.resources


def test_inventory_scan_returns_lifecycle_analysis(tmp_path: Path) -> None:
    inventory = scan_managed_inventory(_write_distribution(tmp_path / "source"))

    assert "defined" not in inventory.lifecycle.statuses
    assert {diagnostic.code for diagnostic in inventory.lifecycle.diagnostics} == {
        "missing-created-status",
        "missing-terminal",
    }


def test_inventory_scan_returns_package_completeness_diagnostics(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    shutil.rmtree(source_root / "skills" / "specle")
    (source_root / "policies" / "testing.md").unlink()

    inventory = scan_managed_inventory(source_root)

    assert inventory.package_diagnostics == (
        "the packaged skill inventory has no 'specle' skill",
        f"the policy inventory is empty at {source_root / 'policies'}",
    )


@pytest.mark.parametrize(
    ("relative_path", "expected"),
    [
        (("skills", "define", "resource.json"), "modified managed resource"),
        (("skills", "define", "resource.json"), "missing managed resource"),
        (("policies", "testing.md"), "modified managed resource"),
    ],
)
def test_reports_missing_or_modified_managed_resources(
    tmp_path: Path, relative_path: tuple[str, ...], expected: str
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    target_path = target / ".agents" / relative_path[0] / relative_path[1]
    if len(relative_path) == 3:
        target_path /= relative_path[2]
    if expected.startswith("missing"):
        target_path.unlink()
    else:
        if target_path.suffix == ".md":
            target_path.write_text("---\nspecle_policy: true\n---\n\nmodified\n")
        else:
            target_path.write_text("modified\n")

    diagnostics = _compare_distribution(source_root, target)

    assert any(expected in diagnostic for diagnostic in diagnostics)


def test_reports_unexpected_managed_resources_but_ignores_unmarked_skills(
    tmp_path: Path,
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    unexpected = target / ".agents" / "skills" / "define" / "extra.json"
    unmarked = target / ".agents" / "skills" / "external" / "SKILL.md"
    unexpected.write_text("{}\n")
    unmarked.parent.mkdir()
    unmarked.write_text("# Local skill\n")

    diagnostics = _compare_distribution(source_root, target)

    assert any(
        "unexpected managed resource" in diagnostic for diagnostic in diagnostics
    )
    assert all("external" not in diagnostic for diagnostic in diagnostics)


def test_reports_a_marker_stripped_expected_skill(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    skill_file = target / ".agents" / "skills" / "define" / "SKILL.md"
    skill_file.write_text("---\nname: define\n---\n")

    diagnostics = _compare_distribution(source_root, target)

    assert any("missing managed skill" in diagnostic for diagnostic in diagnostics)


def test_compares_binary_managed_resources(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    binary_resource = source_root / "skills" / "define" / "resource.bin"
    binary_resource.write_bytes(b"\x00\xff")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)

    assert _compare_distribution(source_root, target) == ()


def test_force_replaces_only_exact_managed_destinations(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    managed_skill = target / ".agents" / "skills" / "define" / "SKILL.md"
    managed_policy = target / ".agents" / "policies" / "testing.md"
    old_index = target / ".agents" / "skills" / "specle" / "index.json"
    old_specle_resource = target / ".agents" / "skills" / "specle" / "resource.json"
    external_skill = target / ".agents" / "skills" / "external" / "SKILL.md"
    project_document = target / ".agents" / "project" / "README.md"
    for path, contents in (
        (managed_skill, "# Old define\n"),
        (managed_policy, "# Old testing\n"),
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
        == (source_root / "skills" / "define" / "SKILL.md").read_text()
    )
    assert (
        managed_policy.read_text()
        == (source_root / "policies" / "testing.md").read_text()
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


def test_force_prunes_obsolete_distributed_policies(tmp_path: Path) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    retired = target / ".agents" / "policies" / "retired.md"
    retired.write_text("---\nspecle_policy: true\n---\n\n# Retired guidance\n")

    with pytest.raises(SkillInstallationError, match="retired.md"):
        initialise_distribution(source_root, target)

    initialise_distribution(source_root, target, force=True)

    assert not retired.exists()


def test_staging_failure_preserves_existing_content_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    existing = target / ".agents" / "skills" / "define" / "SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Existing define\n")

    def fail_copytree(*args: object, **_kwargs: object) -> None:
        raise OSError("copy failed")

    monkeypatch.setattr(inventory.shutil, "copytree", fail_copytree)

    with pytest.raises(SkillInstallationError, match="unable to stage"):
        initialise_distribution(source_root, target, force=True)

    assert existing.read_text() == "# Existing define\n"
    assert not list((target / ".agents").rglob(".specle-tmp-*"))


def test_update_staging_failure_removes_a_partially_created_temporary_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    manifest = tmp_path / "manifest"
    append_manifest(manifest, scan_managed_inventory(source_root), "1.0")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    source_resource = source_root / "skills" / "define" / "resource.json"
    source_resource.write_text('{"version": "new"}\n')
    blueprint = scan_managed_inventory(source_root)
    installed = scan_managed_inventory(target / ".agents")
    generations = read_manifest_generations(manifest)
    detection = detect_installed_version(
        managed_resource_checksums(installed), generations
    )

    def fail_after_creating_destination(source: Path, destination: Path) -> None:
        destination.mkdir()
        raise OSError("copy failed")

    monkeypatch.setattr(inventory.shutil, "copytree", fail_after_creating_destination)

    with pytest.raises(SkillInstallationError, match="unable to stage"):
        update_distribution(
            source_root, target, blueprint, installed, generations, detection
        )

    assert not list((target / ".agents").rglob(".specle-tmp-*"))


def test_apply_failure_removes_directories_created_for_staged_resources(
    tmp_path: Path,
) -> None:
    root = tmp_path / ".agents"
    destination = root / "skills" / "new" / "resource.json"
    destination.parent.mkdir(parents=True)
    temporary = inventory._temporary_sibling(destination)
    temporary.write_text("new\n")

    def fail_after_apply() -> None:
        raise OSError("index generation failed")

    with pytest.raises(SkillInstallationError, match="unable to replace"):
        inventory._apply_staged_changes(
            [(temporary, destination)],
            [],
            after_apply=fail_after_apply,
            cleanup_directories=[destination.parent, destination.parent.parent],
        )

    assert not (root / "skills").exists()


def test_index_generation_failure_preserves_the_previous_index_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = _write_distribution(tmp_path / "source")
    target = tmp_path / "project"
    target.mkdir()
    initialise_distribution(source_root, target)
    index_path = target / ".agents" / "skills" / "specle" / "index.json"
    previous_index = index_path.read_text()

    def fail_index(*args: object, **_kwargs: object) -> inventory.SkillIndex:
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
        if destination.name == "define":
            raise OSError("rename failed")
        original_replace(temporary, destination, backups)

    monkeypatch.setattr(inventory, "_replace_staged_destination", fail_first_skill)

    with pytest.raises(SkillInstallationError, match=r"destination.*skills/define"):
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
    define_directory = skills_root / "define"
    specle_directory = skills_root / "specle"
    index_path = specle_directory / "index.json"
    previous_define_resource = (define_directory / "resource.json").read_text()
    specle_resource = specle_directory / "resource.json"
    previous_specle_resource = '{"version": "old"}\n'
    specle_resource.write_text(previous_specle_resource)
    previous_index = '{"previous": true}\n'
    index_path.write_text(previous_index)
    (source_root / "skills" / "define" / "resource.json").write_text(
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

    assert (define_directory / "resource.json").read_text() == previous_define_resource
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
    policy_path = target / ".agents" / "policies" / "testing.md"
    original_replace = Path.replace

    def fail_replacement_and_restore(path: Path, destination: Path) -> Path:
        if destination == policy_path and path.name.startswith(
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
    policy_path = target / ".agents" / "policies" / "testing.md"
    original_replace = Path.replace

    def fail_policy_replacement(path: Path, destination: Path) -> Path:
        if destination == policy_path and path.name.startswith(
            ".specle-tmp-testing.md-"
        ):
            raise OSError("replacement failed")
        return original_replace(path, destination)

    monkeypatch.setattr(Path, "replace", fail_policy_replacement)

    with pytest.raises(SkillInstallationError, match=r"destination.*policies/testing"):
        initialise_distribution(source_root, target, force=True)

    skills_root = target / ".agents" / "skills"
    assert not (skills_root / "define").exists()
    assert not (skills_root / "specle").exists()
    assert not (skills_root / "verify").exists()
    assert not list((target / ".agents").rglob(".specle-tmp-*"))

    monkeypatch.setattr(Path, "replace", original_replace)
    initialise_distribution(source_root, target)

    assert (skills_root / "define" / "SKILL.md").is_file()


def _write_distribution(root: Path) -> Path:
    _write_skill(root / "skills", "define", "Planning")
    _write_skill(root / "skills", "specle", "Reference")
    _write_skill(root / "skills", "verify", "Quality")
    policies = root / "policies"
    policies.mkdir(parents=True)
    (policies / "testing.md").write_text("---\nspecle_policy: true\n---\n\n# Testing\n")
    return root


def _compare_distribution(source_root: Path, target: Path) -> tuple[str, ...]:
    return compare_managed_inventories(
        scan_managed_inventory(source_root),
        scan_managed_inventory(target / ".agents"),
    )


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
