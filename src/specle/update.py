"""Version-aware update planning for a scanned Specle distribution."""

from __future__ import annotations

from pathlib import Path

import anyio

from specle.inventory import DistributionInventory, ManagedSkillInventory
from specle.update_models import (
    ManifestGeneration,
    UpdateAction,
    UpdatePlan,
    VersionDetection,
)


async def build_update_plan(
    blueprint: DistributionInventory,
    installed: DistributionInventory,
    generations: tuple[ManifestGeneration, ...],
    detection: VersionDetection,
    target_directory: Path,
) -> UpdatePlan:
    """Plan an atomic managed-content update from scanned inventory facts."""
    blueprint_skills = {skill.metadata.name: skill for skill in blueprint.skills}
    installed_skills = {skill.metadata.name: skill for skill in installed.skills}
    unmarked_conflicts = {
        Path("skills") / skill_file.parent.name
        for skill_file in installed.unmanaged_skill_files
        if skill_file.parent.name in blueprint_skills
    }
    previous = _generation_resources(generations, detection.version)
    actions: list[UpdateAction] = [
        UpdateAction("replace-skill", path, requires_confirmation=True)
        for path in sorted(unmarked_conflicts)
    ]
    for name in sorted(set(blueprint_skills) | set(installed_skills)):
        path = Path("skills") / name
        if path in unmarked_conflicts:
            continue
        current = blueprint_skills.get(name)
        existing = installed_skills.get(name)
        old = {
            resource_path: checksum
            for resource_path, checksum in previous.items()
            if resource_path.is_relative_to(path)
        }
        if current is None:
            if existing is not None:
                actions.append(
                    UpdateAction(
                        "remove",
                        path,
                        requires_confirmation=_skill_resources(existing) != old,
                    )
                )
        elif existing is None:
            actions.append(UpdateAction("add", path))
        elif _skill_resources(current) != _skill_resources(existing):
            actions.append(
                UpdateAction(
                    "upgrade",
                    path,
                    requires_confirmation=_skill_resources(existing) != old,
                )
            )

    blueprint_resources = {
        resource.path: resource.checksum for resource in blueprint.resources
    }
    installed_resources = {
        resource.path: resource.checksum for resource in installed.resources
    }
    policy_paths = (
        set(blueprint_resources)
        | set(installed_resources)
        | {path for path in previous if path.parts[0] == "policies"}
    )
    unmanaged_resources = set(installed.unmanaged_resources)
    for path in sorted(policy_paths):
        current = blueprint_resources.get(path)
        existing = installed_resources.get(path)
        old = previous.get(path)
        if current is None:
            if existing is not None:
                actions.append(
                    UpdateAction("remove", path, requires_confirmation=old != existing)
                )
        elif existing is None:
            actions.append(
                UpdateAction(
                    "add", path, requires_confirmation=path in unmanaged_resources
                )
            )
        elif existing != current:
            actions.append(
                UpdateAction("upgrade", path, requires_confirmation=old != existing)
            )

    project_root = anyio.Path(target_directory) / ".agents" / "project"
    if await project_root.exists() and not await project_root.is_dir():
        guidance = ("project guidance has an unexpected path type; run onboard",)
    elif not await project_root.is_dir():
        guidance = ("project guidance is missing; run onboard",)
    elif not await (project_root / "README.md").is_file():
        guidance = ("project README is missing; run onboard",)
    else:
        guidance = ()
    return UpdatePlan(
        detection.version,
        detection.confidence,
        detection.matched,
        detection.compared,
        tuple(actions),
        guidance,
    )


def _generation_resources(
    generations: tuple[ManifestGeneration, ...], version: str | None
) -> dict[Path, str]:
    if version is None:
        return {}
    for generation in generations:
        if generation.version == version:
            return dict(generation.resources)
    return {}


def _skill_resources(skill: ManagedSkillInventory) -> dict[Path, str]:
    return {resource.path: resource.checksum for resource in skill.resources}
