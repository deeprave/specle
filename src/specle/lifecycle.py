"""Runtime validation built on the shared managed-inventory lifecycle graph."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from specle.change_state import ChangeStateSnapshot, read_change_state
from specle.inventory import (
    LifecycleDiagnostic,
    SkillMetadata,
    SkillMetadataError,
    analyse_lifecycle,
    scan_managed_inventory,
)


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """One buffered read of durable state used by validation and reporting."""

    state: ChangeStateSnapshot
    diagnostics: tuple[LifecycleDiagnostic, ...]


def validate_installed_skill_inventory(
    target_directory: Path,
) -> tuple[LifecycleDiagnostic, ...]:
    """Return lifecycle diagnostics from one shared installed-inventory inspection."""
    try:
        inventory = scan_managed_inventory(
            target_directory.expanduser().resolve() / ".agents"
        )
    except SkillMetadataError as error:
        return (LifecycleDiagnostic("invalid-installed-inventory", str(error)),)
    return inventory.lifecycle.diagnostics


def validate_runtime_records(
    target_directory: Path,
    skills: Iterable[SkillMetadata],
    snapshot: RuntimeSnapshot | None = None,
) -> tuple[LifecycleDiagnostic, ...]:
    """Validate discovered per-change records without rejecting future fields."""
    skills = tuple(skills)
    snapshot = snapshot or read_runtime_snapshot(target_directory)
    diagnostics = list(snapshot.diagnostics)
    for record in (*snapshot.state.active, *snapshot.state.archived):
        _validate_record(
            record.status,
            record.directory / "status.json",
            _lifecycle_statuses_for_kind(skills, record.status.get("kind")),
            diagnostics,
        )
        if record.archived and record.status.get("status") != "complete":
            diagnostics.append(
                LifecycleDiagnostic(
                    "archived-not-complete",
                    f"{record.directory / 'status.json'}: archived change is not complete",
                )
            )
    return tuple(diagnostics)


def read_runtime_snapshot(target_directory: Path) -> RuntimeSnapshot:
    """Read durable records once for validation and optional reporting."""
    state = read_change_state(target_directory)
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
        diagnostics.append(_diagnostic(path, "missing-evidence", "verification"))
    if status == "approved" and _nested_status(record, "review") not in {
        "pass",
        "resolved",
    }:
        diagnostics.append(_diagnostic(path, "missing-evidence", "review"))
    if status == "committed":
        delivery = record.get("delivery")
        required_delivery = ("reference", "head_branch", "target_branch")
        if not isinstance(delivery, dict) or not all(
            isinstance(delivery.get(field), str) and delivery[field]
            for field in required_delivery
        ):
            diagnostics.append(_diagnostic(path, "missing-evidence", "delivery"))


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


def _lifecycle_statuses_for_kind(
    skills: Iterable[SkillMetadata], kind: object
) -> set[str]:
    """Return lifecycle statuses that can apply to one persisted change kind."""
    statuses = _lifecycle_statuses(skills)
    if kind != "spike":
        return statuses

    spike_statuses: set[str] = set()
    for skill in skills:
        if skill.lifecycle is None:
            continue
        for transition in skill.lifecycle.transitions:
            for state in (transition.source, transition.target):
                if state.kind == "spike":
                    spike_statuses.add(state.status)
    return spike_statuses


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
    """Compatibility view of the shared inventory lifecycle analysis."""
    return analyse_lifecycle(tuple(skills)).diagnostics
