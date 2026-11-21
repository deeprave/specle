"""Skill inventory metadata and installation support."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import NotRequired, TypedDict

from strictyaml import Enum, Map, Optional, Seq, Str, load
from strictyaml.exceptions import StrictYAMLError

from specle.file_reading import read_regular_bytes, read_regular_text
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
class ResourceChecksum:
    """One package-owned resource identified by a stable relative path and digest."""

    path: Path
    checksum: str


@dataclass(frozen=True, slots=True)
class ManagedSkillInventory:
    """One scanned managed skill with its parsed metadata and resource checksums."""

    metadata: SkillMetadata
    resources: tuple[ResourceChecksum, ...]


@dataclass(frozen=True, slots=True)
class ManagedInventory:
    """A scanned distribution root with managed skills and shared resources."""

    root: Path
    skills: tuple[ManagedSkillInventory, ...]
    resources: tuple[ResourceChecksum, ...]
    unmanaged_skill_files: tuple[Path, ...]
    lifecycle: LifecycleAnalysis
    package_diagnostics: tuple[str, ...]


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


@dataclass(frozen=True, slots=True)
class LifecycleDiagnostic:
    """One lifecycle-contract inconsistency found during inventory inspection."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class LifecycleAnalysis:
    """The reusable lifecycle graph derived from one managed inventory."""

    statuses: frozenset[str]
    created: frozenset[str]
    terminal: frozenset[str]
    edges: tuple[tuple[str, str], ...]
    diagnostics: tuple[LifecycleDiagnostic, ...]


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
    try:
        contents = read_regular_text(path)
    except OSError as error:
        raise SkillMetadataError(f"unable to read {path}: {error}") from error
    return _read_skill_metadata(path, contents)


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
    """Compatibility view of the one inventory inspection for a skills root."""
    return tuple(
        record.metadata
        for record in scan_managed_inventory(
            source_root.expanduser().resolve().parent
        ).skills
    )


def discover_installed_specle_skills(
    target_directory: Path,
) -> tuple[SkillMetadata, ...]:
    """Compatibility view of one installed-inventory inspection."""
    inventory = scan_managed_inventory(
        target_directory.expanduser().resolve() / ".agents"
    )
    return tuple(record.metadata for record in inventory.skills)


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


def analyse_lifecycle(skills: tuple[SkillMetadata, ...]) -> LifecycleAnalysis:
    """Derive the lifecycle graph and all contract diagnostics from one inventory."""
    names = {skill.name for skill in skills}
    owners = tuple(skill for skill in skills if skill.lifecycle is not None)
    diagnostics: list[LifecycleDiagnostic] = []
    statuses: set[str] = set()
    created: set[str] = set()
    terminal: set[str] = set()
    edges: dict[str, set[str]] = defaultdict(set)
    next_by_edge: dict[tuple[LifecycleState, LifecycleState], set[str | None]] = (
        defaultdict(set)
    )

    for skill in owners:
        assert skill.lifecycle is not None
        terminal.update(skill.lifecycle.terminal)

    for skill in owners:
        declaration = skill.lifecycle
        assert declaration is not None
        statuses.update(declaration.accepts)
        statuses.update(declaration.creates)
        statuses.update(declaration.terminal)
        created.update(declaration.creates)

        for transition in declaration.transitions:
            source = transition.source.status
            target = transition.target.status
            statuses.update((source, target))
            edges[source].add(target)
            next_by_edge[transition.source, transition.target].add(
                transition.next_skill
            )
            if source not in declaration.accepts:
                diagnostics.append(
                    LifecycleDiagnostic(
                        "unaccepted-transition-source",
                        f"{skill.path}: transition from {source!r} is not declared in accepts",
                    )
                )
            if transition.next_skill is not None and transition.next_skill not in names:
                diagnostics.append(
                    LifecycleDiagnostic(
                        "missing-next-skill",
                        f"{skill.path}: transition from {source!r} names unavailable skill {transition.next_skill!r}",
                    )
                )
            if target in terminal and transition.next_skill is not None:
                diagnostics.append(
                    LifecycleDiagnostic(
                        "terminal-transition-has-next",
                        f"terminal transition to {target!r} must not name a next skill",
                    )
                )
            if target not in terminal and transition.next_skill is None:
                diagnostics.append(
                    LifecycleDiagnostic(
                        "non-terminal-transition-missing-next",
                        f"non-terminal transition to {target!r} must name a next skill",
                    )
                )

    if not terminal:
        diagnostics.append(
            LifecycleDiagnostic(
                "missing-terminal", "no terminal lifecycle status is declared"
            )
        )
    if not created:
        diagnostics.append(
            LifecycleDiagnostic(
                "missing-created-status", "no lifecycle status is created"
            )
        )

    for (source, target), next_skills in sorted(
        next_by_edge.items(), key=lambda entry: (entry[0][0].status, entry[0][1].status)
    ):
        if len(next_skills) > 1:
            diagnostics.append(
                LifecycleDiagnostic(
                    "contradictory-transition",
                    "transitions from "
                    f"{source.status!r} to {target.status!r} name conflicting next skills",
                )
            )

    for status in sorted(terminal):
        if edges.get(status):
            diagnostics.append(
                LifecycleDiagnostic(
                    "terminal-has-outgoing-transition",
                    f"terminal status {status!r} has an outgoing transition",
                )
            )

    reachable = _reachable_statuses(created, edges)
    for status in sorted(statuses - reachable):
        diagnostics.append(
            LifecycleDiagnostic(
                "unreachable-status",
                f"lifecycle status {status!r} cannot be reached from a created status",
            )
        )

    for status in sorted(statuses - terminal):
        if not edges.get(status):
            diagnostics.append(
                LifecycleDiagnostic(
                    "dead-end-status",
                    f"non-terminal lifecycle status {status!r} has no outgoing transition",
                )
            )
        elif not _can_reach_terminal(status, terminal, edges):
            diagnostics.append(
                LifecycleDiagnostic(
                    "no-terminal-path",
                    f"non-terminal lifecycle status {status!r} cannot reach a terminal status",
                )
            )

    return LifecycleAnalysis(
        frozenset(statuses),
        frozenset(created),
        frozenset(terminal),
        tuple(
            (source, target)
            for source in sorted(edges)
            for target in sorted(edges[source])
        ),
        tuple(diagnostics),
    )


def scan_managed_inventory(distribution_root: Path) -> ManagedInventory:
    """Scan one blueprint or installed `.agents` root into managed inventory records."""
    root = distribution_root.expanduser().resolve()
    skills_root = root / "skills"
    if not skills_root.is_dir():
        label = (
            "installed skill inventory" if root.name == ".agents" else "skill inventory"
        )
        raise SkillMetadataError(f"the {label} is unavailable at {skills_root}")

    skills: list[ManagedSkillInventory] = []
    names: set[str] = set()
    unmanaged: list[Path] = []
    for directory in sorted(skills_root.iterdir()):
        if not directory.is_dir():
            continue
        skill_file = directory / "SKILL.md"
        if not skill_file.exists() and not skill_file.is_symlink():
            continue
        try:
            contents = read_regular_text(skill_file)
        except (FileNotFoundError, OSError) as error:
            raise SkillMetadataError(f"unable to read {skill_file}: {error}") from error
        if not _has_specle_group_text(contents):
            unmanaged.append(skill_file)
            continue
        metadata = _read_skill_metadata(skill_file, contents)
        if metadata.name != directory.name:
            raise SkillMetadataError(f"{skill_file} does not match its directory name")
        if metadata.name in names:
            raise SkillMetadataError(
                f"{skill_file} duplicates managed skill {metadata.name!r}"
            )
        names.add(metadata.name)
        skills.append(
            ManagedSkillInventory(
                metadata,
                _checksum_resources(
                    directory,
                    Path("skills") / metadata.name,
                    exclude_generated_index=True,
                ),
            )
        )
    metadata = tuple(record.metadata for record in skills)
    _validate_skill_dependencies(metadata)
    policy_resources = _scan_managed_policies(root)
    return ManagedInventory(
        root,
        tuple(skills),
        policy_resources,
        tuple(unmanaged),
        analyse_lifecycle(metadata),
        _package_completeness_diagnostics(root, tuple(skills), policy_resources),
    )


def _package_completeness_diagnostics(
    root: Path,
    skills: tuple[ManagedSkillInventory, ...],
    resources: tuple[ResourceChecksum, ...],
) -> tuple[str, ...]:
    """Derive package completeness diagnostics during inventory inspection."""
    diagnostics: list[str] = []
    if not skills:
        diagnostics.append("the packaged managed skill inventory is empty")
    elif not any(record.metadata.name == "specle" for record in skills):
        diagnostics.append("the packaged skill inventory has no 'specle' skill")
    if not resources:
        diagnostics.append(f"the policy inventory is empty at {root / 'policies'}")
    return tuple(diagnostics)


def compare_managed_inventories(
    blueprint: ManagedInventory, installed: ManagedInventory
) -> tuple[str, ...]:
    """Report managed skill and resource drift between scanned inventories."""
    diagnostics: list[str] = []
    expected_skills = {record.metadata.name: record for record in blueprint.skills}
    installed_skills = {record.metadata.name: record for record in installed.skills}
    for name in sorted(expected_skills.keys() - installed_skills.keys()):
        diagnostics.append(f"missing managed skill (requires update): {name}")
    for name in sorted(installed_skills.keys() - expected_skills.keys()):
        diagnostics.append(f"unexpected managed skill (requires update): {name}")
    for name in sorted(expected_skills.keys() & installed_skills.keys()):
        diagnostics.extend(
            _compare_resources(
                expected_skills[name].resources,
                installed_skills[name].resources,
                "managed",
            )
        )
    diagnostics.extend(
        _compare_resources(blueprint.resources, installed.resources, "managed")
    )
    return tuple(sorted(diagnostics))


def compare_installed_distribution(
    source_root: Path, target_directory: Path
) -> tuple[str, ...]:
    """Report content drift between a package distribution and an installed target."""
    return compare_managed_inventories(
        scan_managed_inventory(source_root),
        scan_managed_inventory(target_directory.expanduser().resolve() / ".agents"),
    )


def _checksum_resources(
    directory: Path, prefix: Path, *, exclude_generated_index: bool = False
) -> tuple[ResourceChecksum, ...]:
    """Checksum every regular resource below a package-owned directory."""
    if not directory.is_dir():
        return ()
    resources: list[ResourceChecksum] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        relative = prefix / path.relative_to(directory)
        if (
            exclude_generated_index
            and relative == Path("skills") / "specle" / "index.json"
        ):
            continue
        try:
            contents = read_regular_bytes(path)
        except OSError as error:
            raise SkillMetadataError(f"unable to read {path}: {error}") from error
        resources.append(
            ResourceChecksum(relative, hashlib.sha256(contents).hexdigest())
        )
    return tuple(resources)


def _scan_managed_policies(root: Path) -> tuple[ResourceChecksum, ...]:
    """Return checksums for marker-owned top-level Markdown policy documents."""
    policies_root = root / "policies"
    if not policies_root.is_dir():
        return ()
    resources: list[ResourceChecksum] = []
    for path in sorted(policies_root.glob("*.md")):
        try:
            contents = read_regular_text(path)
        except (FileNotFoundError, OSError) as error:
            raise SkillMetadataError(f"unable to read {path}: {error}") from error
        if not _has_specle_policy_text(contents):
            continue
        resources.append(
            ResourceChecksum(Path("policies") / path.name, _checksum_path(path))
        )
    return tuple(resources)


def _checksum_path(path: Path) -> str:
    """Return the SHA-256 checksum of one already-classified regular file."""
    try:
        return hashlib.sha256(read_regular_bytes(path)).hexdigest()
    except OSError as error:
        raise SkillMetadataError(f"unable to read {path}: {error}") from error


def _compare_resources(
    expected: tuple[ResourceChecksum, ...],
    actual: tuple[ResourceChecksum, ...],
    subject: str,
) -> tuple[str, ...]:
    """Compare resource collections by relative path and stable checksum."""
    expected_by_path = {resource.path: resource for resource in expected}
    actual_by_path = {resource.path: resource for resource in actual}
    diagnostics: list[str] = []
    for path in sorted(expected_by_path.keys() - actual_by_path.keys()):
        diagnostics.append(f"missing {subject} resource (requires update): {path}")
    for path in sorted(actual_by_path.keys() - expected_by_path.keys()):
        diagnostics.append(f"unexpected {subject} resource (requires update): {path}")
    for path in sorted(expected_by_path.keys() & actual_by_path.keys()):
        if expected_by_path[path].checksum != actual_by_path[path].checksum:
            diagnostics.append(f"modified {subject} resource (requires update): {path}")
    return tuple(diagnostics)


def _reachable_statuses(created: set[str], edges: dict[str, set[str]]) -> set[str]:
    """Return statuses reachable from any declared creation point."""
    reachable = set(created)
    pending = deque(created)
    while pending:
        source = pending.popleft()
        for target in edges.get(source, ()):
            if target not in reachable:
                reachable.add(target)
                pending.append(target)
    return reachable


def _can_reach_terminal(
    start: str, terminal: set[str], edges: dict[str, set[str]]
) -> bool:
    """Return whether a status has any directed path to a terminal state."""
    seen = {start}
    pending = deque([start])
    while pending:
        source = pending.popleft()
        for target in edges.get(source, ()):
            if target in terminal:
                return True
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return False


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
    inventory = scan_managed_inventory(source_root)
    if inventory.package_diagnostics:
        raise SkillMetadataError(inventory.package_diagnostics[0])
    skills = tuple(record.metadata for record in inventory.skills)
    policies = tuple(source_root / resource.path for resource in inventory.resources)

    agents_root = target_directory / ".agents"
    skills_root = agents_root / "skills"
    policies_root = agents_root / "policies"
    skill_destinations = [
        (skill.path.parent, skills_root / skill.name) for skill in skills
    ]
    policy_destinations = [
        (source, agents_root / source.relative_to(source_root)) for source in policies
    ]
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
        if path.name not in incoming_names and _has_specle_policy(path)
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


def _has_specle_policy(path: Path) -> bool:
    """Return whether a policy frontmatter block declares Specle ownership."""
    try:
        return _has_specle_policy_text(read_regular_text(path))
    except (FileNotFoundError, OSError):
        return False


def _has_specle_policy_text(contents: str) -> bool:
    """Classify a buffered policy document by its ownership marker."""
    lines = contents.splitlines()
    if not lines or lines[0] != "---":
        return False
    for line in lines[1:]:
        if line == "---":
            break
        if line == "specle_policy: true":
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
