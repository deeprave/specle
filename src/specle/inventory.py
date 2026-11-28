"""Skill inventory metadata and installation support."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import dataclass, replace
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import NotRequired, TypedDict

import anyio
from strictyaml import Enum, Map, Optional, Seq, Str, load
from strictyaml.exceptions import StrictYAMLError

from specle.file_reading import read_regular_bytes, read_regular_text
from specle.schema_registry import SCHEMA_IDENTIFIERS
from specle.update_models import (
    ManifestGeneration,
    UpdateAction,
    UpdatePlan,
    VersionDetection,
)

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
    "cancelled",
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
class DistributionInventory:
    """A scanned distribution root with managed skills and shared resources."""

    root: Path
    skills: tuple[ManagedSkillInventory, ...]
    resources: tuple[ResourceChecksum, ...]
    unmanaged_skill_files: tuple[Path, ...]
    unmanaged_resources: tuple[Path, ...]
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


async def packaged_distribution_root() -> Traversable:
    """Return the packaged root containing skills and package policy."""
    root = files("specle").joinpath("blueprints")
    with as_file(root) as root_path:
        path = anyio.Path(root_path)
        if (
            not await (path / "skills").is_dir()
            or not await (path / "policies").is_dir()
        ):
            raise SkillMetadataError("the packaged Specle distribution is unavailable")
    return root


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


async def scan_managed_inventory(
    distribution_root: Path,
) -> DistributionInventory:
    """Asynchronously scan one blueprint or installed `.agents` root."""
    root = await anyio.Path(distribution_root).expanduser()
    root = await root.resolve()
    skills_root = root / "skills"
    if not await skills_root.is_dir():
        label = (
            "installed skill inventory" if root.name == ".agents" else "skill inventory"
        )
        raise SkillMetadataError(f"the {label} is unavailable at {skills_root}")
    skills: list[ManagedSkillInventory] = []
    names: set[str] = set()
    unmanaged: list[Path] = []
    directories = [path async for path in skills_root.iterdir() if await path.is_dir()]
    for directory in sorted(directories, key=lambda path: path.name):
        skill_file = directory / "SKILL.md"
        if not await skill_file.exists() and not await skill_file.is_symlink():
            continue
        try:
            contents = await read_regular_text(skill_file)
        except (FileNotFoundError, OSError) as error:
            raise SkillMetadataError(f"unable to read {skill_file}: {error}") from error
        if not _has_specle_group_text(contents):
            unmanaged.append(Path(skill_file))
            continue
        metadata = _read_skill_metadata(Path(skill_file), contents)
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
                await _checksum_resources(
                    directory,
                    Path("skills") / metadata.name,
                    exclude_generated_index=True,
                ),
            )
        )
    metadata = tuple(record.metadata for record in skills)
    _validate_skill_dependencies(metadata)
    policy_resources, unmanaged_resources = await _scan_managed_policies(root)
    root_path = Path(root)
    return DistributionInventory(
        root_path,
        tuple(skills),
        policy_resources,
        tuple(unmanaged),
        unmanaged_resources,
        analyse_lifecycle(metadata),
        _package_completeness_diagnostics(root_path, tuple(skills), policy_resources),
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
    blueprint: DistributionInventory, installed: DistributionInventory
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


def managed_resource_checksums(inventory: DistributionInventory) -> dict[Path, str]:
    """Flatten one already-scanned inventory into stable managed resource checksums."""
    resources = {
        resource.path: resource.checksum
        for skill in inventory.skills
        for resource in skill.resources
    }
    resources.update(
        {resource.path: resource.checksum for resource in inventory.resources}
    )
    return resources


async def build_update_plan(
    blueprint: DistributionInventory,
    installed: DistributionInventory,
    generations: tuple[ManifestGeneration, ...],
    detection: VersionDetection,
    target_directory: Path,
) -> UpdatePlan:
    """Compatibility entrypoint for the dedicated update planner."""
    from specle.update import build_update_plan as plan_update

    return await plan_update(
        blueprint, installed, generations, detection, target_directory
    )


async def update_distribution(
    source_root: Path,
    target_directory: Path,
    blueprint: DistributionInventory,
    installed: DistributionInventory,
    generations: tuple[ManifestGeneration, ...],
    detection: VersionDetection,
    *,
    plan: UpdatePlan | None = None,
    force: bool = False,
    dry_run: bool = False,
    approve_conflicts: bool = False,
) -> UpdatePlan:
    """Asynchronously update a valid target using supplied provenance."""
    target = await anyio.Path(target_directory).expanduser()
    target = await target.resolve()
    source = await anyio.Path(source_root).expanduser()
    source = await source.resolve()
    if not await target.is_dir():
        raise SkillInstallationError(
            f"target directory must be an existing directory: {target}"
        )
    if plan is None:
        await _validate_installed_index(target, installed)
        plan = await build_update_plan(
            blueprint, installed, generations, detection, Path(target)
        )
    if dry_run:
        return plan
    if force:
        await initialise_distribution(Path(source), Path(target), force=True)
        return plan
    conflicts = tuple(action for action in plan.actions if action.requires_confirmation)
    if conflicts and not approve_conflicts:
        return replace(plan, declined=conflicts)
    approved = list(plan.actions)
    if not approved:
        return replace(plan)
    index_skills = _projected_skill_metadata(blueprint, installed, approved)
    agents_root = target / ".agents"
    staged: list[tuple[anyio.Path, anyio.Path]] = []
    temporary_paths: list[anyio.Path] = []
    removals: list[anyio.Path] = []
    staging_directories: list[anyio.Path] = []
    try:
        for action in approved:
            destination = agents_root / action.path
            if action.path.parts[0] == "skills" and action.action != "remove":
                temporary = _temporary_sibling(destination)
                temporary_paths.append(temporary)
                staging_directories.extend(
                    await _missing_parent_directories(temporary.parent, agents_root)
                )
                await temporary.parent.mkdir(parents=True, exist_ok=True)
                await _copy_tree(source / action.path, temporary)
                staged.append((temporary, destination))
            elif action.action in {"add", "upgrade"}:
                temporary = _temporary_sibling(destination)
                temporary_paths.append(temporary)
                staging_directories.extend(
                    await _missing_parent_directories(temporary.parent, agents_root)
                )
                await _copy_file(source / action.path, temporary)
                staged.append((temporary, destination))
            elif action.action == "remove":
                removals.append(destination)
    except (OSError, TypeError, ValueError) as error:
        await _clean_up_paths(temporary_paths)
        await _remove_empty_directories(staging_directories)
        raise SkillInstallationError("unable to stage the Specle update") from error
    except BaseException:
        with anyio.CancelScope(shield=True):
            await _clean_up_paths(temporary_paths)
            await _remove_empty_directories(staging_directories)
        raise
    index_destination = agents_root / "skills" / "specle" / "index.json"
    removals.append(index_destination)

    async def generate_index() -> None:
        await index_destination.parent.mkdir(parents=True, exist_ok=True)
        await index_destination.write_text(
            json.dumps(
                build_skill_index(
                    tuple(index_skills[name] for name in sorted(index_skills))
                ),
                indent=2,
            )
            + "\n"
        )

    with anyio.CancelScope(shield=True):
        await _apply_staged_changes(
            staged,
            removals,
            after_apply=generate_index,
            cleanup_directories=staging_directories,
        )
        await _remove_empty_parents(removals, agents_root)
    return replace(plan)


def _projected_skill_metadata(
    blueprint: DistributionInventory,
    installed: DistributionInventory,
    approved: list[UpdateAction],
) -> dict[str, SkillMetadata]:
    """Return managed skill metadata for the post-update installed inventory."""
    result = {record.metadata.name: record.metadata for record in installed.skills}
    blueprint_skills = {
        record.metadata.name: record.metadata for record in blueprint.skills
    }
    for action in approved:
        parts = action.path.parts
        if len(parts) < 2 or parts[0] != "skills":
            continue
        name = parts[1]
        if action.action == "remove":
            result.pop(name, None)
        else:
            result[name] = blueprint_skills[name]
    return result


async def _validate_installed_index(
    target_directory: anyio.Path, installed: DistributionInventory
) -> None:
    index_path = target_directory / ".agents" / "skills" / "specle" / "index.json"
    try:
        index = json.loads(await read_regular_text(index_path))
    except (
        FileNotFoundError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise SkillInstallationError(
            f"invalid generated skill index: {index_path}: {error}"
        ) from error
    if index != build_skill_index(
        tuple(record.metadata for record in installed.skills)
    ):
        raise SkillInstallationError(f"invalid generated skill index: {index_path}")


async def _checksum_resources(
    directory: anyio.Path, prefix: Path, *, exclude_generated_index: bool = False
) -> tuple[ResourceChecksum, ...]:
    if not await directory.is_dir():
        return ()
    resources: list[ResourceChecksum] = []
    paths = [path async for path in directory.rglob("*") if await path.is_file()]
    for path in sorted(paths, key=lambda candidate: str(candidate)):
        relative = prefix / Path(path).relative_to(Path(directory))
        if (
            exclude_generated_index
            and relative == Path("skills") / "specle" / "index.json"
        ):
            continue
        try:
            contents = await read_regular_bytes(path)
        except OSError as error:
            raise SkillMetadataError(f"unable to read {path}: {error}") from error
        resources.append(
            ResourceChecksum(relative, hashlib.sha256(contents).hexdigest())
        )
    return tuple(resources)


async def _scan_managed_policies(
    root: anyio.Path,
) -> tuple[tuple[ResourceChecksum, ...], tuple[Path, ...]]:
    policies_root = root / "policies"
    if not await policies_root.is_dir():
        return (), ()
    resources: list[ResourceChecksum] = []
    unmanaged: list[Path] = []
    paths = [path async for path in policies_root.glob("*.md")]
    for path in sorted(paths, key=lambda candidate: candidate.name):
        try:
            contents = await read_regular_text(path)
        except (FileNotFoundError, OSError) as error:
            raise SkillMetadataError(f"unable to read {path}: {error}") from error
        if not _has_specle_policy_text(contents):
            unmanaged.append(Path("policies") / path.name)
            continue
        try:
            checksum = hashlib.sha256(await read_regular_bytes(path)).hexdigest()
        except OSError as error:
            raise SkillMetadataError(f"unable to read {path}: {error}") from error
        resources.append(ResourceChecksum(Path("policies") / path.name, checksum))
    return tuple(resources), tuple(unmanaged)


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


async def initialise_distribution(
    source_root: Path, target_directory: Path, *, force: bool = False
) -> tuple[Path, ...]:
    """Asynchronously install packaged skills and policy documents."""
    target = await anyio.Path(target_directory).expanduser()
    target = await target.resolve()
    if not await target.is_dir():
        raise SkillInstallationError(
            f"target directory must be an existing directory: {target}"
        )
    source = await anyio.Path(source_root).expanduser()
    source = await source.resolve()
    inventory = await scan_managed_inventory(Path(source))
    if inventory.package_diagnostics:
        raise SkillMetadataError(inventory.package_diagnostics[0])
    skills = tuple(record.metadata for record in inventory.skills)
    agents_root = target / ".agents"
    skills_root = agents_root / "skills"
    policies_root = agents_root / "policies"
    skill_destinations = [
        (source / "skills" / skill.name, skills_root / skill.name) for skill in skills
    ]
    policy_destinations = [
        (source / resource.path, agents_root / resource.path)
        for resource in inventory.resources
    ]
    index_destination = skills_root / "specle" / "index.json"
    destinations = [
        *(skills_root / skill.name for skill in skills),
        *(destination for _, destination in policy_destinations),
        index_destination,
    ]
    obsolete_skills = await _discover_obsolete_managed_skills(
        skills_root, {skill.name for skill in skills}
    )
    obsolete_policies = await _discover_obsolete_policies(
        policies_root, {resource.path.name for resource in inventory.resources}
    )
    collisions = [
        destination for destination in destinations if await destination.exists()
    ]
    collisions.extend((*obsolete_skills, *obsolete_policies))
    if collisions and not force:
        raise SkillInstallationError(
            "distribution-managed destination already exists: "
            + ", ".join(str(path) for path in collisions)
        )
    staged: list[tuple[anyio.Path, anyio.Path]] = []
    temporary_paths: list[anyio.Path] = []
    try:
        await skills_root.mkdir(parents=True, exist_ok=True)
        await policies_root.mkdir(parents=True, exist_ok=True)
        for source_path, destination in skill_destinations:
            temporary = _temporary_sibling(destination)
            temporary_paths.append(temporary)
            await _copy_tree(source_path, temporary)
            staged.append((temporary, destination))
        for source_path, destination in policy_destinations:
            temporary = _temporary_sibling(destination)
            temporary_paths.append(temporary)
            await _copy_file(source_path, temporary)
            staged.append((temporary, destination))
        index_temporary = _temporary_sibling(skills_root / "index.json")
        temporary_paths.append(index_temporary)
        await index_temporary.parent.mkdir(parents=True, exist_ok=True)
        await index_temporary.write_text(
            json.dumps(build_skill_index(skills), indent=2) + "\n"
        )
        staged.append((index_temporary, index_destination))
        ignore_destination = target / ".specle" / ".gitignore"
        ignore_contents = await _local_runtime_ignore_contents(ignore_destination)
        if ignore_contents is not None:
            temporary = _temporary_sibling(ignore_destination)
            temporary_paths.append(temporary)
            await temporary.parent.mkdir(parents=True, exist_ok=True)
            await temporary.write_text(ignore_contents)
            staged.append((temporary, ignore_destination))
    except (OSError, TypeError, ValueError) as error:
        await _clean_up_paths(temporary_paths)
        raise SkillInstallationError(
            "unable to stage the Specle distribution"
        ) from error
    except BaseException:
        with anyio.CancelScope(shield=True):
            await _clean_up_paths(temporary_paths)
        raise
    with anyio.CancelScope(shield=True):
        await _apply_staged_changes(staged, [*obsolete_skills, *obsolete_policies])
    return tuple(Path(path) for path in destinations)


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


async def _copy_file(source: anyio.Path, destination: anyio.Path) -> None:
    """Copy one file through AnyIO paths, creating its destination parent."""
    await destination.parent.mkdir(parents=True, exist_ok=True)
    await destination.write_bytes(await source.read_bytes())
    await destination.chmod((await source.stat()).st_mode & 0o7777)


def _temporary_sibling(destination: anyio.Path) -> anyio.Path:
    return destination.parent / f".specle-tmp-{destination.name}-{uuid.uuid4().hex}"


async def _copy_tree(source: anyio.Path, destination: anyio.Path) -> None:
    """Copy one directory tree through AnyIO paths."""
    await destination.mkdir(parents=True)
    async for child in source.iterdir():
        target = destination / child.name
        if await child.is_dir():
            await _copy_tree(child, target)
        else:
            await _copy_file(child, target)


async def _remove_path(path: anyio.Path) -> None:
    """Remove a file or directory tree through AnyIO paths when present."""
    if await path.is_symlink():
        await path.unlink()
        return
    if not await path.exists():
        return
    if await path.is_dir():
        async for child in path.iterdir():
            await _remove_path(child)
        await path.rmdir()
    else:
        await path.unlink()


async def _clean_up_paths(paths: list[anyio.Path]) -> None:
    for path in paths:
        with suppress(OSError):
            await _remove_path(path)


async def _missing_parent_directories(
    directory: anyio.Path, root: anyio.Path
) -> list[anyio.Path]:
    missing: list[anyio.Path] = []
    while directory != root and not await directory.exists():
        missing.append(directory)
        directory = directory.parent
    return missing


async def _remove_empty_directories(directories: list[anyio.Path]) -> None:
    for directory in sorted(
        set(directories), key=lambda path: len(path.parts), reverse=True
    ):
        with suppress(OSError):
            await directory.rmdir()


async def _remove_empty_parents(removals: list[anyio.Path], root: anyio.Path) -> None:
    for removed in removals:
        parent = removed.parent
        while parent != root:
            try:
                await parent.rmdir()
            except OSError:
                break
            parent = parent.parent


async def _apply_staged_changes(
    staged: list[tuple[anyio.Path, anyio.Path]],
    removals: list[anyio.Path],
    *,
    after_apply: Callable[[], Awaitable[None]] | None = None,
    cleanup_directories: list[anyio.Path] | None = None,
) -> None:
    """Atomically replace staged destinations with recoverable backups."""
    backups: list[tuple[anyio.Path, anyio.Path]] = []
    created: list[anyio.Path] = []
    destination: anyio.Path | None = None
    try:
        for destination in removals:
            if await destination.exists():
                backup = (
                    destination.parent
                    / f".specle-backup-{destination.name}-{uuid.uuid4().hex}"
                )
                await destination.replace(backup)
                backups.append((destination, backup))
        for temporary, destination in staged:
            await destination.parent.mkdir(parents=True, exist_ok=True)
            if await destination.exists():
                backup = (
                    destination.parent
                    / f".specle-backup-{destination.name}-{uuid.uuid4().hex}"
                )
                await destination.replace(backup)
                backups.append((destination, backup))
            else:
                created.append(destination)
            await temporary.replace(destination)
        if after_apply is not None:
            await after_apply()
    except OSError as error:
        failed_destination = destination
        await _clean_up_paths(created)
        await _remove_empty_directories(cleanup_directories or [])
        unrestored: list[anyio.Path] = []
        for destination, backup in reversed(backups):
            try:
                await _remove_path(destination)
                if await backup.exists():
                    await backup.replace(destination)
            except OSError:
                if await backup.exists():
                    unrestored.append(backup)
        await _clean_up_paths([temporary for temporary, _ in staged])
        recovery = ""
        if unrestored:
            recovery = "; retained recovery backup(s): " + ", ".join(
                str(backup) for backup in unrestored
            )
        raise SkillInstallationError(
            f"unable to replace managed destination: {failed_destination}{recovery}"
        ) from error
    await _clean_up_paths([backup for _, backup in backups])


async def _local_runtime_ignore_contents(destination: anyio.Path) -> str | None:
    required = ("/current-change", "/context.json")
    try:
        existing = await destination.read_text()
    except FileNotFoundError:
        return "\n".join(required) + "\n"
    missing = [entry for entry in required if entry not in existing.splitlines()]
    if not missing:
        return None
    return (
        existing
        + ("" if not existing or existing.endswith("\n") else "\n")
        + "\n".join(missing)
        + "\n"
    )


async def _discover_obsolete_managed_skills(
    skills_root: anyio.Path, incoming_names: set[str]
) -> tuple[anyio.Path, ...]:
    if not await skills_root.is_dir():
        return ()
    obsolete: list[anyio.Path] = []
    async for directory in skills_root.iterdir():
        if not await directory.is_dir() or directory.name in incoming_names:
            continue
        try:
            contents = await read_regular_text(directory / "SKILL.md")
        except (FileNotFoundError, OSError):
            continue
        if _has_specle_group_text(contents):
            obsolete.append(directory)
    return tuple(sorted(obsolete, key=lambda path: path.name))


async def _discover_obsolete_policies(
    policies_root: anyio.Path, incoming_names: set[str]
) -> tuple[anyio.Path, ...]:
    if not await policies_root.is_dir():
        return ()
    obsolete: list[anyio.Path] = []
    async for path in policies_root.glob("*.md"):
        if path.name in incoming_names:
            continue
        try:
            contents = await read_regular_text(path)
        except (FileNotFoundError, OSError):
            continue
        if _has_specle_policy_text(contents):
            obsolete.append(path)
    return tuple(sorted(obsolete, key=lambda path: path.name))


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


def _frontmatter_text(path: Path, contents: str) -> str:
    """Return delimited frontmatter text or raise a path-specific metadata error."""
    lines = contents.splitlines()
    if not lines or lines[0] != "---":
        raise SkillMetadataError(f"{path} has no frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise SkillMetadataError(f"{path} has unterminated frontmatter") from error
    return "\n".join(lines[1:end])
