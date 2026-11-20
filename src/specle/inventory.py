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
from typing import NotRequired, TypedDict

from strictyaml import Enum, Map, Optional, Seq, Str, load
from strictyaml.exceptions import StrictYAMLError

from specle.schema_registry import SCHEMA_IDENTIFIERS

_SKILL_NAME = re.compile(r"[a-z][a-z0-9-]*")
_LIFECYCLE_STATUSES = (
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
    "complete",
)
_LIFECYCLE_KINDS = ("change", "bugfix", "refactor", "spike")
_LIFECYCLE_SCOPES = ("active", "queued", "committed")
_LIFECYCLE_STATE_SCHEMA = Str() | Map(
    {
        "status": Enum(_LIFECYCLE_STATUSES),
        Optional("kind"): Enum(_LIFECYCLE_KINDS),
        Optional("scope"): Enum(_LIFECYCLE_SCOPES),
    }
)
_SKILL_FRONTMATTER_SCHEMA = Map(
    {
        "name": Str(),
        "specle_group": Str(),
        "description": Str(),
        "usage": Str(),
        Optional("requires"): Seq(Str()),
        Optional("lifecycle"): Map(
            {
                Optional("accepts"): Seq(Enum(_LIFECYCLE_STATUSES)),
                Optional("creates"): Seq(Enum(_LIFECYCLE_STATUSES)),
                Optional("transitions"): Seq(
                    Map(
                        {
                            "from": _LIFECYCLE_STATE_SCHEMA,
                            "to": _LIFECYCLE_STATE_SCHEMA,
                            Optional("next"): Str(),
                        }
                    )
                ),
                Optional("terminal"): Seq(Enum(_LIFECYCLE_STATUSES)),
            }
        ),
    }
)
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
    lifecycle: LifecycleDeclaration | None = None


@dataclass(frozen=True, slots=True)
class LifecycleTransition:
    """One declared lifecycle edge owned by a skill."""

    source: LifecycleState
    target: LifecycleState
    next_skill: str | None


@dataclass(frozen=True, slots=True)
class LifecycleState:
    """A lifecycle status with optional kind and scope constraints."""

    status: str
    kind: str | None = None
    scope: str | None = None


@dataclass(frozen=True, slots=True)
class LifecycleDeclaration:
    """The constrained lifecycle metadata a skill exposes to agents and validation."""

    accepts: tuple[str, ...]
    creates: tuple[str, ...]
    transitions: tuple[LifecycleTransition, ...]
    terminal: tuple[str, ...]


class SkillIndexEntry(TypedDict):
    """A skill entry in the generated installed-skill index."""

    name: str
    description: str
    usage: str


class SkillIndexGroup(TypedDict):
    """A named group in the generated installed-skill index."""

    name: str
    skills: list[SkillIndexEntry]


SkillIndex = TypedDict(
    "SkillIndex",
    {"$schema": str, "groups": list[SkillIndexGroup]},
)


class SkillFrontmatter(TypedDict):
    """Schema-validated frontmatter fields for a package-owned skill."""

    name: str
    specle_group: str
    description: str
    usage: str
    requires: NotRequired[list[str]]
    lifecycle: NotRequired[dict[str, object]]


def packaged_skills_root() -> Traversable:
    """Return the packaged root directory for Specle skill blueprints."""
    root = files("specle").joinpath("blueprints", "skills")
    if not root.is_dir():
        raise SkillMetadataError("the packaged skill inventory is unavailable")
    return root


def packaged_distribution_root() -> Traversable:
    """Return the packaged root containing skills and package policy."""
    root = files("specle").joinpath("blueprints")
    if not root.joinpath("skills").is_dir() or not root.joinpath("policies").is_dir():
        raise SkillMetadataError("the packaged Specle distribution is unavailable")
    return root


def packaged_policies_root() -> Traversable:
    """Return the packaged root directory for Specle policy documents."""
    root = files("specle").joinpath("blueprints", "policies")
    if not root.is_dir():
        raise SkillMetadataError("the packaged policy inventory is unavailable")
    return root


def read_skill_metadata(path: Path) -> SkillMetadata:
    """Read schema-validated Specle metadata from a skill frontmatter block."""
    return _read_skill_metadata(path, path.read_text())


def _read_skill_metadata(path: Path, contents: str) -> SkillMetadata:
    """Parse one buffered skill file into validated metadata."""
    values = _read_skill_frontmatter(path, contents)

    name = values["name"]
    specle_group = values["specle_group"]
    description = values["description"]
    usage = values["usage"]
    if not _SKILL_NAME.fullmatch(name):
        raise SkillMetadataError(f"{path} has an invalid skill name")

    return SkillMetadata(
        name=name,
        specle_group=specle_group,
        description=description,
        usage=usage,
        requires=_parse_requires(values.get("requires", []), path),
        lifecycle=_parse_lifecycle(values.get("lifecycle"), path),
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


def discover_installed_specle_skills(
    target_directory: Path,
) -> tuple[SkillMetadata, ...]:
    """Discover marked Specle skills in an installed target inventory.

    Unmarked client or user skills are intentionally outside Specle's managed
    inventory and are ignored. Marked skills must conform to the full package
    frontmatter contract.
    """
    skills_root = target_directory.expanduser().resolve() / ".agents" / "skills"
    if not skills_root.is_dir():
        raise SkillMetadataError(
            f"the installed skill inventory is unavailable at {skills_root}"
        )

    skills: list[SkillMetadata] = []
    names: set[str] = set()
    for directory in sorted(skills_root.iterdir()):
        skill_file = directory / "SKILL.md"
        if not directory.is_dir() or not skill_file.is_file():
            continue
        try:
            contents = skill_file.read_text()
        except OSError as error:
            raise SkillMetadataError(f"unable to read {skill_file}") from error
        if not _has_specle_group_text(contents):
            continue
        metadata = _read_skill_metadata(skill_file, contents)
        if metadata.name != directory.name:
            raise SkillMetadataError(f"{skill_file} does not match its directory name")
        if metadata.name in names:
            raise SkillMetadataError(
                f"{skill_file} duplicates installed skill {metadata.name!r}"
            )
        names.add(metadata.name)
        skills.append(metadata)

    if not skills:
        raise SkillMetadataError(
            f"the installed skill inventory is empty at {skills_root}"
        )
    discovered = tuple(skills)
    _validate_skill_dependencies(discovered)
    return discovered


def discover_policies(source_root: Path) -> tuple[Path, ...]:
    """Discover packaged policy Markdown documents in stable name order."""
    if not source_root.is_dir():
        raise SkillMetadataError(
            f"the policy inventory is unavailable at {source_root}"
        )
    policies = tuple(sorted(source_root.glob("*.md")))
    if not policies:
        raise SkillMetadataError(f"the policy inventory is empty at {source_root}")
    return policies


def build_skill_index(skills: tuple[SkillMetadata, ...]) -> SkillIndex:
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
                "description": skill.description,
                "usage": skill.usage,
            }
            for skill in sorted(grouped[group_name], key=lambda skill: skill.name)
        ]
        groups.append({"name": group_name, "skills": entries})
    return {"$schema": SCHEMA_IDENTIFIERS["skill-index"], "groups": groups}


def initialise_distribution(
    source_root: Path, target_directory: Path, *, force: bool = False
) -> tuple[Path, ...]:
    """Install the packaged skills and policy documents at an explicit target."""
    target_directory = target_directory.expanduser().resolve()
    if not target_directory.is_dir():
        raise SkillInstallationError(
            f"target directory must be an existing directory: {target_directory}"
        )

    source_root = source_root.expanduser().resolve()
    skills = discover_skills(source_root / "skills")
    policies = discover_policies(source_root / "policies")
    _validate_skill_dependencies(skills)
    if not any(skill.name == "specle" for skill in skills):
        raise SkillMetadataError("the packaged skill inventory has no 'specle' skill")

    agents_root = target_directory / ".agents"
    skills_root = agents_root / "skills"
    policies_root = agents_root / "policies"
    skill_destinations = [
        (skill.path.parent, skills_root / skill.name) for skill in skills
    ]
    policy_destinations = [(source, policies_root / source.name) for source in policies]
    index_destination = skills_root / "specle" / "index.json"
    destinations = [
        *(skills_root / skill.name for skill in skills),
        *(destination for _, destination in policy_destinations),
        index_destination,
    ]
    obsolete_skills = _discover_obsolete_managed_skills(
        skills_root, {skill.name for skill in skills}
    )
    obsolete_policies = _discover_obsolete_policies(
        policies_root, {source.name for source in policies}
    )
    collisions = [
        *(destination for destination in destinations if destination.exists()),
        *obsolete_skills,
        *obsolete_policies,
    ]
    if collisions and not force:
        raise SkillInstallationError(
            "distribution-managed destination already exists: "
            + ", ".join(str(destination) for destination in collisions)
        )

    staged: list[tuple[Path, Path]] = []
    index_temporary: Path | None = None
    ignore_temporary: Path | None = None
    ignore_destination = target_directory / ".specle" / ".gitignore"
    try:
        skills_root.mkdir(parents=True, exist_ok=True)
        policies_root.mkdir(parents=True, exist_ok=True)
        for source, destination in skill_destinations:
            temporary = _temporary_sibling(destination)
            shutil.copytree(source, temporary)
            staged.append((temporary, destination))
        for source, destination in policy_destinations:
            temporary = _temporary_sibling(destination)
            shutil.copy2(source, temporary)
            staged.append((temporary, destination))

        index_temporary = _temporary_sibling(skills_root / "index.json")
        index_temporary.write_text(
            json.dumps(build_skill_index(skills), indent=2) + "\n"
        )
        ignore_contents = _local_runtime_ignore_contents(ignore_destination)
        if ignore_contents is not None:
            ignore_destination.parent.mkdir(parents=True, exist_ok=True)
            ignore_temporary = _temporary_sibling(ignore_destination)
            ignore_temporary.write_text(ignore_contents)
    except (OSError, TypeError, ValueError) as error:
        _clean_up_temporary(
            [temporary for temporary, _ in staged], index_temporary, ignore_temporary
        )
        raise SkillInstallationError(
            "unable to stage the Specle distribution"
        ) from error

    backups: list[tuple[Path, Path]] = []
    created_destinations: list[Path] = []
    destination: Path | None = None
    try:
        for destination in obsolete_skills:
            _backup_existing_destination(destination, backups)
        for destination in obsolete_policies:
            _backup_existing_destination(destination, backups)
        for temporary, destination in staged:
            if _replace_staged_destination(temporary, destination, backups):
                created_destinations.append(destination)
        destination = index_destination
        if _replace_staged_destination(index_temporary, index_destination, backups):
            created_destinations.append(index_destination)
        if ignore_temporary is not None:
            destination = ignore_destination
            if _replace_staged_destination(
                ignore_temporary, ignore_destination, backups
            ):
                created_destinations.append(ignore_destination)
    except OSError as error:
        _clean_up_temporary(created_destinations, None)
        unrestored = _restore_backups(backups)
        _clean_up_temporary(
            [temporary for temporary, _ in staged], index_temporary, ignore_temporary
        )
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


def _parse_requires(value: list[str], path: Path) -> tuple[str, ...]:
    if any(not _SKILL_NAME.fullmatch(entry) for entry in value):
        raise SkillMetadataError(f"{path} has an invalid required skill name")
    return tuple(value)


def _parse_lifecycle(value: object, path: Path) -> LifecycleDeclaration | None:
    """Convert schema-validated lifecycle metadata into typed declarations."""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise SkillMetadataError(f"{path} has an invalid lifecycle value")

    def statuses(name: str) -> tuple[str, ...]:
        entries = value.get(name, [])
        if not isinstance(entries, list) or not all(
            isinstance(entry, str) for entry in entries
        ):
            raise SkillMetadataError(f"{path} has an invalid lifecycle {name}")
        return tuple(entries)

    transitions_value = value.get("transitions", [])
    if not isinstance(transitions_value, list):
        raise SkillMetadataError(f"{path} has invalid lifecycle transitions")
    transitions: list[LifecycleTransition] = []
    for entry in transitions_value:
        if not isinstance(entry, dict):
            raise SkillMetadataError(f"{path} has invalid lifecycle transitions")
        source = _parse_lifecycle_state(entry.get("from"), path)
        target = _parse_lifecycle_state(entry.get("to"), path)
        next_skill = entry.get("next")
        if next_skill is not None and not isinstance(next_skill, str):
            raise SkillMetadataError(f"{path} has invalid lifecycle transitions")
        transitions.append(LifecycleTransition(source, target, next_skill))
    return LifecycleDeclaration(
        accepts=statuses("accepts"),
        creates=statuses("creates"),
        transitions=tuple(transitions),
        terminal=statuses("terminal"),
    )


def _parse_lifecycle_state(value: object, path: Path) -> LifecycleState:
    """Normalise compact and nested lifecycle state declarations."""
    if isinstance(value, str):
        state = LifecycleState(value)
    elif not isinstance(value, dict):
        raise SkillMetadataError(f"{path} has invalid lifecycle transitions")
    else:
        status = value.get("status")
        kind = value.get("kind")
        scope = value.get("scope")
        if not isinstance(status, str) or any(
            item is not None and not isinstance(item, str) for item in (kind, scope)
        ):
            raise SkillMetadataError(f"{path} has invalid lifecycle transitions")
        state = LifecycleState(status, kind, scope)
    if state.status not in _LIFECYCLE_STATUSES:
        raise SkillMetadataError(f"{path} has an unsupported lifecycle status")
    if state.kind is not None and state.kind not in _LIFECYCLE_KINDS:
        raise SkillMetadataError(f"{path} has an unsupported lifecycle kind")
    if state.scope is not None and state.scope not in _LIFECYCLE_SCOPES:
        raise SkillMetadataError(f"{path} has an unsupported lifecycle scope")
    return state


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
        _backup_existing_destination(destination, backups)
    temporary.replace(destination)
    return not existed


def _discover_obsolete_managed_skills(
    skills_root: Path, incoming_names: set[str]
) -> tuple[Path, ...]:
    """Return installed Specle skill directories absent from an incoming inventory."""
    if not skills_root.is_dir():
        return ()

    obsolete: list[Path] = []
    for directory in sorted(skills_root.iterdir()):
        if not directory.is_dir() or directory.name in incoming_names:
            continue
        skill_file = directory / "SKILL.md"
        if skill_file.is_file() and _has_specle_group(skill_file):
            obsolete.append(directory)
    return tuple(obsolete)


def _discover_obsolete_policies(
    policies_root: Path, incoming_names: set[str]
) -> tuple[Path, ...]:
    """Return owned policy files absent from the incoming inventory."""
    if not policies_root.is_dir():
        return ()
    return tuple(
        path
        for path in sorted(policies_root.glob("*.md"))
        if path.name not in incoming_names
    )


def _local_runtime_ignore_contents(destination: Path) -> str | None:
    """Return merged local-runtime ignore content, or None when already current."""
    required = ("/current-spec", "/context.json")
    try:
        existing = destination.read_text()
    except FileNotFoundError:
        return "\n".join(required) + "\n"

    lines = existing.splitlines()
    missing = [entry for entry in required if entry not in lines]
    if not missing:
        return None
    separator = "" if not existing or existing.endswith("\n") else "\n"
    return existing + separator + "\n".join(missing) + "\n"


def _has_specle_group(path: Path) -> bool:
    """Return whether a skill frontmatter block declares the Specle marker."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return False
    return _has_specle_group_text("\n".join(lines))


def _has_specle_group_text(contents: str) -> bool:
    """Classify a buffered skill file by its lightweight Specle marker."""
    lines = contents.splitlines()
    if not lines or lines[0] != "---":
        return False
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("specle_group:"):
            return True
    return False


def _backup_existing_destination(
    destination: Path,
    backups: list[tuple[Path, Path]],
) -> None:
    """Move an existing destination to a same-parent recovery backup."""
    backup = _backup_sibling(destination)
    destination.replace(backup)
    backups.append((destination, backup))


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


def _clean_up_temporary(
    staged: list[Path],
    index_temporary: Path | None,
    ignore_temporary: Path | None = None,
) -> None:
    """Remove staging paths after a preparation failure."""
    for temporary in (*staged, index_temporary, ignore_temporary):
        if temporary is None:
            continue
        try:
            if temporary.is_dir():
                shutil.rmtree(temporary)
            elif temporary.exists():
                temporary.unlink()
        except OSError:
            continue


def _read_skill_frontmatter(path: Path, contents: str) -> SkillFrontmatter:
    """Load constrained, schema-validated metadata from one package-owned skill."""
    try:
        values = load(_frontmatter_text(path, contents), _SKILL_FRONTMATTER_SCHEMA).data
    except StrictYAMLError as error:
        detail = getattr(error, "problem", str(error).splitlines()[0])
        raise SkillMetadataError(f"{path} has invalid frontmatter: {detail}") from error

    name = values.get("name")
    specle_group = values.get("specle_group")
    description = values.get("description")
    usage = values.get("usage")
    requires = values.get("requires")
    lifecycle = values.get("lifecycle")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, specle_group, description, usage)
    ):
        raise SkillMetadataError(f"{path} has an empty required metadata value")
    if requires is not None and (
        not isinstance(requires, list)
        or not all(isinstance(requirement, str) for requirement in requires)
    ):
        raise SkillMetadataError(f"{path} has an invalid requires value")
    if lifecycle is not None and not isinstance(lifecycle, dict):
        raise SkillMetadataError(f"{path} has an invalid lifecycle value")
    frontmatter: SkillFrontmatter = {
        "name": name,
        "specle_group": specle_group,
        "description": description,
        "usage": usage,
    }
    if requires is not None:
        frontmatter["requires"] = requires
    if lifecycle is not None:
        frontmatter["lifecycle"] = lifecycle
    return frontmatter


def _frontmatter_text(path: Path, contents: str | None = None) -> str:
    """Return delimited frontmatter text or raise a path-specific metadata error."""
    lines = (path.read_text() if contents is None else contents).splitlines()
    if not lines or lines[0] != "---":
        raise SkillMetadataError(f"{path} has no frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise SkillMetadataError(f"{path} has unterminated frontmatter") from error
    return "\n".join(lines[1:end])
