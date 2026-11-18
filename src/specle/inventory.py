"""Skill inventory metadata and installation support."""

from __future__ import annotations

import re
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

_SKILL_NAME = re.compile(r"[a-z][a-z0-9-]*")


class SkillMetadataError(ValueError):
    """Raised when a skill's required metadata is invalid."""


class SkillInstallationError(ValueError):
    """Raised when a skill cannot be safely installed."""


@dataclass(frozen=True, slots=True)
class SkillMetadata:
    """The Specle grouping and direct dependencies declared by a skill."""

    name: str
    specle_group: str
    requires: tuple[str, ...]
    path: Path


def packaged_skills_root() -> Traversable:
    """Return the packaged root directory for Specle skill blueprints."""
    root = files("specle").joinpath("skills")
    if not root.is_dir():
        raise SkillMetadataError("the packaged skill inventory is unavailable")
    return root


def read_skill_metadata(path: Path) -> SkillMetadata:
    """Read the constrained Specle metadata from a skill frontmatter block."""
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise SkillMetadataError(f"{path} has no frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise SkillMetadataError(f"{path} has unterminated frontmatter") from error

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        if key not in {"name", "specle_group", "requires"}:
            continue
        if key in values:
            raise SkillMetadataError(f"{path} declares {key!r} more than once")
        values[key] = value.strip()

    name = values.get("name", "")
    specle_group = values.get("specle_group", "")
    if not _SKILL_NAME.fullmatch(name):
        raise SkillMetadataError(f"{path} has an invalid skill name")
    if not specle_group:
        raise SkillMetadataError(f"{path} has no specle_group value")

    return SkillMetadata(
        name=name,
        specle_group=specle_group,
        requires=_parse_requires(values.get("requires", "[]"), path),
        path=path,
    )


def resolve_dependencies(
    source_root: Path, requested_skill: str
) -> tuple[SkillMetadata, ...]:
    """Resolve a managed skill and its requirements in installation order."""
    resolved: list[SkillMetadata] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(skill_name: str) -> None:
        if skill_name in visiting:
            raise SkillMetadataError(f"dependency cycle includes {skill_name!r}")
        if skill_name in visited:
            return

        path = source_root / skill_name / "SKILL.md"
        if not path.is_file():
            raise SkillMetadataError(f"required skill {skill_name!r} does not exist")

        metadata = read_skill_metadata(path)
        if metadata.name != skill_name:
            raise SkillMetadataError(f"{path} does not match its directory name")
        if not metadata.specle_group:
            raise SkillMetadataError(f"{path} has no specle_group marker")

        visiting.add(skill_name)
        for dependency in metadata.requires:
            visit(dependency)
        visiting.remove(skill_name)
        visited.add(skill_name)
        resolved.append(metadata)

    visit(requested_skill)
    return tuple(resolved)


def install_skill(
    source_root: Path,
    target_root: Path,
    requested_skill: str,
) -> tuple[Path, ...]:
    """Install a managed skill and its dependencies without overwriting external skills."""
    metadata = resolve_dependencies(source_root, requested_skill)
    destinations = [
        (skill, target_root / skill.name / "SKILL.md") for skill in metadata
    ]

    for skill, destination in destinations:
        if not destination.exists():
            continue
        try:
            existing = read_skill_metadata(destination)
        except SkillMetadataError as error:
            raise SkillInstallationError(
                f"protected external skill at {destination}"
            ) from error
        if not existing.specle_group:
            raise SkillInstallationError(f"protected external skill at {destination}")

    installed: list[Path] = []
    for skill, destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_bytes(skill.path.read_bytes())
        temporary.replace(destination)
        installed.append(destination)

    return tuple(installed)


def update_skills(
    source_root: Path,
    target_root: Path,
    requested_skill: str | None = None,
) -> tuple[Path, ...]:
    """Update one managed skill or every managed skill in an active inventory."""
    if requested_skill is not None:
        destination = target_root / requested_skill / "SKILL.md"
        _require_managed_destination(destination)
        return install_skill(source_root, target_root, requested_skill)

    updated: list[Path] = []
    for destination in sorted(target_root.glob("*/SKILL.md")):
        try:
            metadata = read_skill_metadata(destination)
        except SkillMetadataError:
            continue
        if metadata.specle_group:
            updated.extend(install_skill(source_root, target_root, metadata.name))
    return tuple(updated)


def _require_managed_destination(destination: Path) -> None:
    if not destination.is_file():
        raise SkillInstallationError(f"managed skill is not installed at {destination}")
    try:
        metadata = read_skill_metadata(destination)
    except SkillMetadataError as error:
        raise SkillInstallationError(
            f"protected external skill at {destination}"
        ) from error
    if not metadata.specle_group:
        raise SkillInstallationError(f"protected external skill at {destination}")


def _parse_requires(value: str, path: Path) -> tuple[str, ...]:
    if not value.startswith("[") or not value.endswith("]"):
        raise SkillMetadataError(f"{path} has an invalid requires value")

    entries = [entry.strip() for entry in value[1:-1].split(",") if entry.strip()]
    if any(not _SKILL_NAME.fullmatch(entry) for entry in entries):
        raise SkillMetadataError(f"{path} has an invalid required skill name")
    return tuple(entries)
