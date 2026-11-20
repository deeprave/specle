"""Deterministic validation of declared Specle lifecycle transitions."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from specle.inventory import (
    LifecycleState,
    SkillMetadata,
    SkillMetadataError,
    discover_installed_specle_skills,
)
from specle.spec_state import SpecStateSnapshot, read_spec_state


@dataclass(frozen=True, slots=True)
class LifecycleDiagnostic:
    """One lifecycle-contract inconsistency."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """One buffered read of durable state used by validation and reporting."""

    state: SpecStateSnapshot
    diagnostics: tuple[LifecycleDiagnostic, ...]


def validate_installed_skill_inventory(
    target_directory: Path,
) -> tuple[LifecycleDiagnostic, ...]:
    """Validate the marked Specle skill inventory in an explicit target."""
    try:
        skills = discover_installed_specle_skills(target_directory)
    except SkillMetadataError as error:
        return (LifecycleDiagnostic("invalid-installed-inventory", str(error)),)
    return validate_lifecycle_graph(skills)


def validate_runtime_records(
    target_directory: Path,
    skills: Iterable[SkillMetadata],
    snapshot: RuntimeSnapshot | None = None,
) -> tuple[LifecycleDiagnostic, ...]:
    """Validate discovered per-spec records without rejecting future fields."""
    skills = tuple(skills)
    snapshot = snapshot or read_runtime_snapshot(target_directory)
    diagnostics = list(snapshot.diagnostics)
    statuses = _lifecycle_statuses(skills)
    for record in (*snapshot.state.active, *snapshot.state.archived):
        _validate_record(
            record.status,
            record.directory / "status.json",
            statuses,
            diagnostics,
        )
        if record.archived and record.status.get("status") != "complete":
            diagnostics.append(
                LifecycleDiagnostic(
                    "archived-not-complete",
                    f"{record.directory / 'status.json'}: archived spec is not complete",
                )
            )
    return tuple(diagnostics)


def read_runtime_snapshot(target_directory: Path) -> RuntimeSnapshot:
    """Read durable records once for validation and optional reporting."""
    state = read_spec_state(target_directory)
    diagnostics = tuple(
        LifecycleDiagnostic("invalid-runtime-state", message)
        for message in state.diagnostics
    )
    return RuntimeSnapshot(state, diagnostics)


def _validate_record(
    record: dict[str, object],
    path: Path,
    statuses: set[str],
    diagnostics: list[LifecycleDiagnostic],
) -> None:
    status = record.get("status")
    kind = record.get("kind", "change")
    if not isinstance(kind, str):
        diagnostics.append(_diagnostic(path, "invalid-kind", "kind"))
    if not isinstance(status, str) or status not in statuses:
        diagnostics.append(_diagnostic(path, "invalid-status", "status"))
    if status == "verified" and _nested_status(record, "verification") != "pass":
        diagnostics.append(
            _diagnostic(
                path,
                "missing-evidence",
                "verification",
            )
        )
    if status == "approved" and _nested_status(record, "review") != "pass":
        diagnostics.append(
            _diagnostic(
                path,
                "missing-evidence",
                "review",
            )
        )
    if status == "committed":
        delivery = record.get("delivery")
        required_delivery = ("reference", "head_branch", "target_branch")
        if not isinstance(delivery, dict) or not all(
            isinstance(delivery.get(field), str) and delivery[field]
            for field in required_delivery
        ):
            diagnostics.append(
                _diagnostic(
                    path,
                    "missing-evidence",
                    "delivery",
                )
            )


def _nested_status(record: dict[str, object], name: str) -> object:
    value = record.get(name)
    return value.get("status") if isinstance(value, dict) else None


def _lifecycle_statuses(skills: Iterable[SkillMetadata]) -> set[str]:
    statuses: set[str] = set()
    for skill in skills:
        if skill.lifecycle is None:
            continue
        statuses.update(skill.lifecycle.accepts)
        statuses.update(skill.lifecycle.creates)
        statuses.update(skill.lifecycle.terminal)
        for transition in skill.lifecycle.transitions:
            statuses.add(transition.source.status)
            statuses.add(transition.target.status)
    return statuses


def _terminal_statuses(skills: Iterable[SkillMetadata]) -> set[str]:
    """Return every lifecycle status declared terminal by installed skills."""
    return {
        status
        for skill in skills
        if skill.lifecycle is not None
        for status in skill.lifecycle.terminal
    }


def _diagnostic(path: Path, code: str, field: str) -> LifecycleDiagnostic:
    return LifecycleDiagnostic(code, f"{path}: invalid {field}")


def validate_lifecycle_graph(
    skills: Iterable[SkillMetadata],
) -> tuple[LifecycleDiagnostic, ...]:
    """Return deterministic diagnostics for declared lifecycle metadata.

    State selectors may add kind or scope constraints, but graph reachability is
    deliberately assessed at the status level. Constraint-specific runtime
    checks belong to target-state validation.
    """
    skills = tuple(skills)
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
                        f"{skill.path}: transition to terminal status {target!r} must not name a next skill",
                    )
                )
            if target not in terminal and transition.next_skill is None:
                diagnostics.append(
                    LifecycleDiagnostic(
                        "non-terminal-transition-missing-next",
                        f"{skill.path}: transition to non-terminal status {target!r} must name a next skill",
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
