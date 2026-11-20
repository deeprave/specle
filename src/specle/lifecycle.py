"""Deterministic validation of declared Specle lifecycle transitions."""

from __future__ import annotations

import json
import re
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
from specle.schema_registry import SchemaRegistryError, validate_instance


@dataclass(frozen=True, slots=True)
class LifecycleDiagnostic:
    """One lifecycle-contract inconsistency."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """One buffered read of the runtime records used by validation and reporting."""

    context: dict[str, object] | None
    issue: dict[str, object] | None
    diagnostics: tuple[LifecycleDiagnostic, ...]


_KIND = re.compile(r"[a-z][a-z0-9-]*")


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
    """Validate established runtime fields without rejecting future fields."""
    skills = tuple(skills)
    target = target_directory.expanduser().resolve()
    context_path = target / ".specle" / "context.json"
    issue_path = target / ".specle" / "current-issue.json"
    snapshot = snapshot or read_runtime_snapshot(target)
    diagnostics = list(snapshot.diagnostics)
    context = snapshot.context
    issue = snapshot.issue
    if context is None or issue is None:
        return tuple(diagnostics)
    if not _validate_contract(context, context_path, diagnostics):
        return tuple(diagnostics)
    if not _validate_contract(issue, issue_path, diagnostics):
        return tuple(diagnostics)

    issue_spec_path = issue.get("spec_path")
    if not isinstance(issue_spec_path, str):
        diagnostics.append(_diagnostic(issue_path, "missing-string", "spec_path"))
        return tuple(diagnostics)
    current = context.get("current_spec")
    if not isinstance(current, dict):
        diagnostics.append(_diagnostic(context_path, "missing-object", "current_spec"))
    else:
        _validate_record(
            current,
            "current_spec",
            target,
            _lifecycle_statuses(skills),
            skills,
            diagnostics,
        )
        if current.get("path") != issue_spec_path:
            diagnostics.append(
                LifecycleDiagnostic(
                    "current-path-mismatch",
                    f"{context_path}: current_spec.path does not match {issue_path}",
                )
            )

    queued = context.get("queued_specs", [])
    if not isinstance(queued, list):
        diagnostics.append(_diagnostic(context_path, "invalid-list", "queued_specs"))
    else:
        for index, record in enumerate(queued):
            if not isinstance(record, dict):
                diagnostics.append(
                    _diagnostic(
                        context_path, "invalid-record", f"queued_specs[{index}]"
                    )
                )
                continue
            _validate_record(
                record,
                f"queued_specs[{index}]",
                target,
                _lifecycle_statuses(skills),
                skills,
                diagnostics,
            )
    return tuple(diagnostics)


def read_runtime_snapshot(target_directory: Path) -> RuntimeSnapshot:
    """Read both runtime records once for validation and optional reporting."""
    target = target_directory.expanduser().resolve()
    diagnostics: list[LifecycleDiagnostic] = []
    context = _load_json_object(target / ".specle" / "context.json", diagnostics)
    issue = _load_json_object(target / ".specle" / "current-issue.json", diagnostics)
    return RuntimeSnapshot(context, issue, tuple(diagnostics))


def _load_json_object(
    path: Path, diagnostics: list[LifecycleDiagnostic]
) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        diagnostics.append(
            LifecycleDiagnostic("missing-runtime-file", f"missing {path}")
        )
        return None
    except json.JSONDecodeError as error:
        diagnostics.append(
            LifecycleDiagnostic("malformed-json", f"{path}: {error.msg}")
        )
        return None
    except (OSError, UnicodeDecodeError) as error:
        diagnostics.append(LifecycleDiagnostic("unreadable-json", f"{path}: {error}"))
        return None
    if not isinstance(value, dict):
        diagnostics.append(_diagnostic(path, "invalid-json-object", "root"))
        return None
    return value


def _validate_contract(
    record: dict[str, object], path: Path, diagnostics: list[LifecycleDiagnostic]
) -> bool:
    """Validate a versioned runtime record before applying lifecycle rules."""
    try:
        validate_instance(record)
    except SchemaRegistryError as error:
        diagnostics.append(LifecycleDiagnostic("invalid-contract", f"{path}: {error}"))
        return False
    return True


def _validate_record(
    record: dict[str, object],
    label: str,
    target: Path,
    statuses: set[str],
    skills: tuple[SkillMetadata, ...],
    diagnostics: list[LifecycleDiagnostic],
) -> None:
    name = record.get("name")
    path = record.get("path")
    status = record.get("status")
    kind = record.get("kind", "change")
    next_skill = record.get("next")
    for field, value in (("name", name), ("path", path), ("status", status)):
        if not isinstance(value, str):
            diagnostics.append(
                _diagnostic(
                    target / ".specle" / "context.json",
                    "missing-string",
                    f"{label}.{field}",
                )
            )
    if not isinstance(path, str):
        return
    if isinstance(name, str) and Path(path).name != name:
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json",
                "path-name-mismatch",
                f"{label}.name",
            )
        )
    if not (target / path).is_dir():
        diagnostics.append(
            LifecycleDiagnostic(
                "missing-spec-directory", f"{label}.path does not exist: {path}"
            )
        )
    if not isinstance(kind, str) or not _KIND.fullmatch(kind):
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json", "invalid-kind", f"{label}.kind"
            )
        )
    if not isinstance(status, str) or status not in statuses:
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json", "invalid-status", f"{label}.status"
            )
        )
    allowed_next = _allowed_next_skills(status, kind, skills)
    terminal = _terminal_statuses(skills)
    if status not in terminal and not isinstance(next_skill, str):
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json", "missing-next", f"{label}.next"
            )
        )
    elif next_skill is not None and (
        not isinstance(next_skill, str) or next_skill not in allowed_next
    ):
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json", "invalid-next", f"{label}.next"
            )
        )
    if status == "verified" and _nested_status(record, "verification") != "pass":
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json",
                "missing-evidence",
                f"{label}.verification",
            )
        )
    if status == "approved" and _nested_status(record, "review") != "pass":
        diagnostics.append(
            _diagnostic(
                target / ".specle" / "context.json",
                "missing-evidence",
                f"{label}.review",
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
                    target / ".specle" / "context.json",
                    "missing-evidence",
                    f"{label}.delivery",
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


def _allowed_next_skills(
    status: object, kind: object, skills: Iterable[SkillMetadata]
) -> set[str]:
    """Return commands whose declaration can operate on a record selector."""
    if not isinstance(status, str) or not isinstance(kind, str):
        return set()
    allowed: set[str] = set()
    for skill in skills:
        lifecycle = skill.lifecycle
        if lifecycle is None:
            continue
        if status in lifecycle.accepts:
            allowed.add(skill.name)
        for transition in lifecycle.transitions:
            source = transition.source
            if source.status != status or (
                source.kind is not None and source.kind != kind
            ):
                continue
            if transition.next_skill is not None:
                allowed.add(transition.next_skill)
    return allowed


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
