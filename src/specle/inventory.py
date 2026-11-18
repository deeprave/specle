"""Skill inventory metadata and installation support."""

from __future__ import annotations

import json
import re
import shutil
import uuid
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TypedDict

_SKILL_NAME = re.compile(r"[a-z][a-z0-9-]*")
_GROUP_ORDER = (
    "Reference",
    "Setup",
    "Coordination",
    "Discovery",
    "Planning",
    "Implementation",
    "Quality",
    "Integration",
    "Alternatives",
    "Reporting",
)


class SkillMetadataError(ValueError):
    """Raised when a skill's required metadata is invalid."""


class SkillInstallationError(ValueError):
    """Raised when a skill cannot be safely installed."""


@dataclass(frozen=True, slots=True)
class SkillMetadata:
    """The Specle grouping and direct dependencies declared by a skill."""

    name: str
    specle_group: str
    description: str
    usage: str
    requires: tuple[str, ...]
    path: Path


class SkillIndexEntry(TypedDict):
    """A skill entry in the generated installed-skill index."""

    name: str
    specle_group: str
    description: str
    usage: str
    resource: str


class SkillIndexGroup(TypedDict):
    """A named group in the generated installed-skill index."""

    name: str
    skills: list[SkillIndexEntry]


class SkillIndex(TypedDict):
    """The generated installed-skill index resource."""

    groups: list[SkillIndexGroup]


def packaged_skills_root() -> Traversable:
    """Return the packaged root directory for Specle skill blueprints."""
    root = files("specle").joinpath("blueprints", "skills")
    if not root.is_dir():
        raise SkillMetadataError("the packaged skill inventory is unavailable")
    return root


def packaged_distribution_root() -> Traversable:
    """Return the packaged root containing both Specle inventories."""
    root = files("specle").joinpath("blueprints")
    if not root.joinpath("skills").is_dir() or not root.joinpath("steering").is_dir():
        raise SkillMetadataError("the packaged Specle distribution is unavailable")
    return root


def packaged_steering_root() -> Traversable:
    """Return the packaged root directory for Specle steering documents."""
    root = files("specle").joinpath("blueprints", "steering")
    if not root.is_dir():
        raise SkillMetadataError("the packaged steering inventory is unavailable")
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

    values = _read_frontmatter_values(lines[1:end], path)

    name = values.get("name", "")
    specle_group = values.get("specle_group", "")
    description = values.get("description", "")
    usage = values.get("usage", "")
    if not _SKILL_NAME.fullmatch(name):
        raise SkillMetadataError(f"{path} has an invalid skill name")
    if not specle_group:
        raise SkillMetadataError(f"{path} has no specle_group value")
    if not description:
        raise SkillMetadataError(f"{path} has no description value")
    if not usage:
        raise SkillMetadataError(f"{path} has no usage value")

    return SkillMetadata(
        name=name,
        specle_group=specle_group,
        description=description,
        usage=usage,
        requires=_parse_requires(values.get("requires", "[]"), path),
        path=path,
    )


def discover_skills(source_root: Path) -> tuple[SkillMetadata, ...]:
    """Discover and validate every packaged skill in stable name order."""
    if not source_root.is_dir():
        raise SkillMetadataError(f"the skill inventory is unavailable at {source_root}")

    skills: list[SkillMetadata] = []
    for path in sorted(source_root.glob("*/SKILL.md")):
        metadata = read_skill_metadata(path)
        if metadata.name != path.parent.name:
            raise SkillMetadataError(f"{path} does not match its directory name")
        skills.append(metadata)

    if not skills:
        raise SkillMetadataError(f"the skill inventory is empty at {source_root}")
    return tuple(skills)


def discover_steering(source_root: Path) -> tuple[Path, ...]:
    """Discover packaged steering Markdown documents in stable name order."""
    if not source_root.is_dir():
        raise SkillMetadataError(
            f"the steering inventory is unavailable at {source_root}"
        )
    steering = tuple(sorted(source_root.glob("*.md")))
    if not steering:
        raise SkillMetadataError(f"the steering inventory is empty at {source_root}")
    return steering


def build_skill_index(
    skills: tuple[SkillMetadata, ...], target_skills_root: Path
) -> SkillIndex:
    """Build the generated installed-skill index from validated metadata."""
    grouped: dict[str, list[SkillMetadata]] = {}
    for skill in skills:
        if skill.specle_group:
            grouped.setdefault(skill.specle_group, []).append(skill)

    order = {group: index for index, group in enumerate(_GROUP_ORDER)}
    groups: list[SkillIndexGroup] = []
    for group_name in sorted(
        grouped, key=lambda name: (order.get(name, len(order)), name)
    ):
        entries: list[SkillIndexEntry] = [
            {
                "name": skill.name,
                "specle_group": skill.specle_group,
                "description": skill.description,
                "usage": skill.usage,
                "resource": (target_skills_root / skill.name / "SKILL.md")
                .resolve()
                .as_uri(),
            }
            for skill in sorted(grouped[group_name], key=lambda skill: skill.name)
        ]
        groups.append({"name": group_name, "skills": entries})
    return {"groups": groups}


def initialise_distribution(
    source_root: Path, target_directory: Path, *, force: bool = False
) -> tuple[Path, ...]:
    """Install the packaged skills and steering documents at an explicit target."""
    target_directory = target_directory.expanduser().resolve()
    if not target_directory.is_dir():
        raise SkillInstallationError(
            f"target directory must be an existing directory: {target_directory}"
        )

    source_root = source_root.expanduser().resolve()
    skills = discover_skills(source_root / "skills")
    steering = discover_steering(source_root / "steering")
    _validate_skill_dependencies(skills)
    if not any(skill.name == "specle" for skill in skills):
        raise SkillMetadataError("the packaged skill inventory has no 'specle' skill")

    agents_root = target_directory / ".agents"
    skills_root = agents_root / "skills"
    steering_root = agents_root / "steering"
    skill_destinations = [
        (skill.path.parent, skills_root / skill.name) for skill in skills
    ]
    steering_destinations = [
        (source, steering_root / source.name) for source in steering
    ]
    index_destination = skills_root / "specle" / "index.json"
    destinations = [
        *(skills_root / skill.name for skill in skills),
        *(destination for _, destination in steering_destinations),
        index_destination,
    ]
    collisions = [destination for destination in destinations if destination.exists()]
    if collisions and not force:
        raise SkillInstallationError(
            "distribution-managed destination already exists: "
            + ", ".join(str(destination) for destination in collisions)
        )

    staged: list[tuple[Path, Path]] = []
    index_temporary: Path | None = None
    try:
        skills_root.mkdir(parents=True, exist_ok=True)
        steering_root.mkdir(parents=True, exist_ok=True)
        for source, destination in skill_destinations:
            temporary = _temporary_sibling(destination)
            shutil.copytree(source, temporary)
            staged.append((temporary, destination))
        for source, destination in steering_destinations:
            temporary = _temporary_sibling(destination)
            shutil.copy2(source, temporary)
            staged.append((temporary, destination))

        index_temporary = _temporary_sibling(skills_root / "index.json")
        index_temporary.write_text(
            json.dumps(build_skill_index(skills, skills_root), indent=2) + "\n"
        )
    except (OSError, TypeError, ValueError) as error:
        _clean_up_temporary([temporary for temporary, _ in staged], index_temporary)
        raise SkillInstallationError(
            "unable to stage the Specle distribution"
        ) from error

    backups: list[tuple[Path, Path]] = []
    created_destinations: list[Path] = []
    destination: Path | None = None
    try:
        for temporary, destination in staged:
            if _replace_staged_destination(temporary, destination, backups):
                created_destinations.append(destination)
        destination = index_destination
        if _replace_staged_destination(index_temporary, index_destination, backups):
            created_destinations.append(index_destination)
    except OSError as error:
        _clean_up_temporary(created_destinations, None)
        unrestored = _restore_backups(backups)
        _clean_up_temporary([temporary for temporary, _ in staged], index_temporary)
        recovery = ""
        if unrestored:
            recovery = "; retained recovery backup(s): " + ", ".join(
                str(backup) for backup in unrestored
            )
        raise SkillInstallationError(
            f"unable to replace managed destination: {destination}{recovery}"
        ) from error
    _clean_up_temporary([backup for _, backup in backups], None)
    return tuple(destinations)


def _parse_requires(value: str, path: Path) -> tuple[str, ...]:
    if not value.startswith("[") or not value.endswith("]"):
        raise SkillMetadataError(f"{path} has an invalid requires value")

    entries = [entry.strip() for entry in value[1:-1].split(",") if entry.strip()]
    if any(not _SKILL_NAME.fullmatch(entry) for entry in entries):
        raise SkillMetadataError(f"{path} has an invalid required skill name")
    return tuple(entries)


def _validate_skill_dependencies(skills: tuple[SkillMetadata, ...]) -> None:
    """Ensure every declared direct dependency is present in the distribution."""
    names = {skill.name for skill in skills}
    for skill in skills:
        for requirement in skill.requires:
            if requirement not in names:
                raise SkillMetadataError(
                    f"{skill.path} requires missing skill {requirement!r}"
                )


def _temporary_sibling(destination: Path) -> Path:
    """Return a unique temporary path in the destination's parent directory."""
    return destination.parent / f".specle-tmp-{destination.name}-{uuid.uuid4().hex}"


def _backup_sibling(destination: Path) -> Path:
    """Return a unique backup path in the destination's parent directory."""
    return destination.parent / f".specle-backup-{destination.name}-{uuid.uuid4().hex}"


def _replace_staged_destination(
    temporary: Path | None,
    destination: Path,
    backups: list[tuple[Path, Path]],
) -> bool:
    """Install a staged item, retaining an existing destination as a backup."""
    if temporary is None:
        raise SkillInstallationError(f"missing staged destination for {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    existed = destination.exists()
    if existed:
        backup = _backup_sibling(destination)
        destination.replace(backup)
        backups.append((destination, backup))
    temporary.replace(destination)
    return not existed


def _restore_backups(backups: list[tuple[Path, Path]]) -> tuple[Path, ...]:
    """Restore retained destinations and return backups that could not be restored."""
    unrestored: list[Path] = []
    for destination, backup in reversed(backups):
        try:
            if destination.is_dir():
                shutil.rmtree(destination)
            elif destination.exists():
                destination.unlink()
            if backup.exists():
                backup.replace(destination)
        except OSError:
            if backup.exists():
                unrestored.append(backup)
    return tuple(unrestored)


def _clean_up_temporary(staged: list[Path], index_temporary: Path | None) -> None:
    """Remove staging paths after a preparation failure."""
    for temporary in (*staged, index_temporary):
        if temporary is None:
            continue
        try:
            if temporary.is_dir():
                shutil.rmtree(temporary)
            elif temporary.exists():
                temporary.unlink()
        except OSError:
            continue


def _read_frontmatter_values(lines: list[str], path: Path) -> dict[str, str]:
    """Read simple scalar and folded scalar values without a YAML dependency."""
    values: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        if key in values:
            raise SkillMetadataError(f"{path} declares {key!r} more than once")
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            folded: list[str] = []
            while index < len(lines) and (
                not lines[index] or lines[index][0].isspace()
            ):
                if lines[index].strip():
                    folded.append(lines[index].strip())
                index += 1
            value = " ".join(folded)
        values[key] = value
    return values
