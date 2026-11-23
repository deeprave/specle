"""Runtime validation built on the shared managed-inventory lifecycle graph."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from specle.change_state import ChangeRecord, ChangeStateSnapshot, read_change_state
from specle.file_reading import read_regular_text
from specle.inventory import (
    LifecycleDiagnostic,
    SkillMetadata,
    SkillMetadataError,
    analyse_lifecycle,
    scan_managed_inventory,
)
from specle.sidecars import CONCURRENT_DELIVERY


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """One buffered read of durable state used by validation and reporting."""

    state: ChangeStateSnapshot
    diagnostics: tuple[LifecycleDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class DeliverySidecars:
    """Explicit, validated sidecars eligible for one parent delivery operation."""

    sidecars: tuple[ChangeRecord, ...]
    diagnostics: tuple[LifecycleDiagnostic, ...]


def discover_delivery_sidecars(
    snapshot: ChangeStateSnapshot,
    parent: ChangeRecord,
    *,
    required_status: str,
) -> DeliverySidecars:
    """Return parent-declared sidecars that reciprocally approve concurrent delivery."""
    diagnostics: list[LifecycleDiagnostic] = []
    sidecars: list[ChangeRecord] = []
    active_by_name = {record.name: record for record in snapshot.active}
    declared_names: set[str] = set()
    relationships = parent.status.get("relationships")
    if not isinstance(relationships, list):
        return DeliverySidecars(
            (),
            (
                _sidecar_diagnostic(
                    parent, "invalid-sidecar-relationship", "relationships"
                ),
            ),
        )

    for relationship in relationships:
        if not isinstance(relationship, dict):
            continue
        if relationship.get("delivery") != CONCURRENT_DELIVERY:
            continue
        name = relationship.get("change")
        relation_kind = relationship.get("type")
        if not isinstance(name, str) or not isinstance(relation_kind, str):
            diagnostics.append(
                _sidecar_diagnostic(
                    parent, "invalid-sidecar-relationship", "relationship"
                )
            )
            continue
        if name in declared_names:
            continue
        declared_names.add(name)
        if _concurrent_declaration_count(relationships, name) != 1:
            diagnostics.append(_sidecar_diagnostic(parent, "duplicate-sidecar", name))
            continue
        sidecar = active_by_name.get(name)
        if sidecar is None:
            diagnostics.append(_sidecar_diagnostic(parent, "missing-sidecar", name))
            continue
        sidecar_kind = sidecar.status.get("kind")
        if sidecar_kind not in {"bugfix", "refactor"} or relation_kind != sidecar_kind:
            diagnostics.append(
                _sidecar_diagnostic(parent, "sidecar-kind-mismatch", name)
            )
            continue
        reciprocal_count = _reciprocal_relationship_count(sidecar, parent.name)
        if reciprocal_count != 1:
            diagnostics.append(
                _sidecar_diagnostic(
                    parent,
                    "duplicate-reciprocal-sidecar"
                    if reciprocal_count > 1
                    else "missing-reciprocal-sidecar",
                    name,
                )
            )
            continue
        if sidecar.status.get("status") != required_status:
            diagnostics.append(_sidecar_diagnostic(parent, "sidecar-not-ready", name))
            continue
        sidecars.append(sidecar)
    return DeliverySidecars(tuple(sidecars), tuple(diagnostics))


def _concurrent_declaration_count(
    relationships: list[object], sidecar_name: str
) -> int:
    return sum(
        isinstance(relationship, dict)
        and relationship.get("change") == sidecar_name
        and relationship.get("delivery") == CONCURRENT_DELIVERY
        for relationship in relationships
    )


def _reciprocal_relationship_count(sidecar: ChangeRecord, parent_name: str) -> int:
    relationships = sidecar.status.get("relationships")
    if not isinstance(relationships, list):
        return 0
    return sum(
        isinstance(relationship, dict)
        and relationship.get("change") == parent_name
        and relationship.get("type") == "origin"
        and relationship.get("delivery") == CONCURRENT_DELIVERY
        for relationship in relationships
    )


def _sidecar_diagnostic(
    parent: ChangeRecord, code: str, detail: str
) -> LifecycleDiagnostic:
    return LifecycleDiagnostic(
        code, f"{parent.directory / 'status.json'}: {code.replace('-', ' ')}: {detail}"
    )


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
    _validate_concurrent_relationships(snapshot.state, diagnostics)
    return tuple(diagnostics)


def _validate_concurrent_relationships(
    snapshot: ChangeStateSnapshot, diagnostics: list[LifecycleDiagnostic]
) -> None:
    for records in (snapshot.active,):
        by_name = {record.name: record for record in records}
        for parent in records:
            if parent.status.get("kind") != "change":
                continue
            relationships = parent.status.get("relationships")
            if not isinstance(relationships, list):
                continue
            for relationship in relationships:
                if not isinstance(relationship, dict):
                    continue
                if relationship.get("delivery") != CONCURRENT_DELIVERY:
                    continue
                name = relationship.get("change")
                relation_kind = relationship.get("type")
                if not isinstance(name, str) or relation_kind not in {
                    "bugfix",
                    "refactor",
                }:
                    diagnostics.append(
                        _sidecar_diagnostic(
                            parent, "invalid-sidecar-relationship", "relationship"
                        )
                    )
                    continue
                sidecar = by_name.get(name)
                if sidecar is None or sidecar.status.get("kind") != relation_kind:
                    diagnostics.append(
                        _sidecar_diagnostic(parent, "missing-sidecar", name)
                    )
                    continue
                reciprocal_count = _reciprocal_relationship_count(sidecar, parent.name)
                if reciprocal_count != 1:
                    diagnostics.append(
                        _sidecar_diagnostic(
                            parent,
                            "duplicate-reciprocal-sidecar"
                            if reciprocal_count > 1
                            else "missing-reciprocal-sidecar",
                            name,
                        )
                    )
        for sidecar in records:
            sidecar_kind = sidecar.status.get("kind")
            if sidecar_kind not in {"bugfix", "refactor"}:
                continue
            relationships = sidecar.status.get("relationships")
            if not isinstance(relationships, list):
                continue
            for relationship in relationships:
                if not isinstance(relationship, dict):
                    continue
                if relationship.get("delivery") != CONCURRENT_DELIVERY:
                    continue
                parent_name = relationship.get("change")
                if (
                    not isinstance(parent_name, str)
                    or relationship.get("type") != "origin"
                ):
                    diagnostics.append(
                        _sidecar_diagnostic(
                            sidecar, "invalid-sidecar-relationship", "relationship"
                        )
                    )
                    continue
                parent = by_name.get(parent_name)
                if parent is None or parent.status.get("kind") != "change":
                    diagnostics.append(
                        _sidecar_diagnostic(
                            sidecar, "missing-reciprocal-parent", parent_name
                        )
                    )
                    continue
                parent_relationships = parent.status.get("relationships")
                if not isinstance(parent_relationships, list) or not any(
                    isinstance(candidate, dict)
                    and candidate.get("change") == sidecar.name
                    and candidate.get("type") == sidecar_kind
                    and candidate.get("delivery") == CONCURRENT_DELIVERY
                    for candidate in parent_relationships
                ):
                    diagnostics.append(
                        _sidecar_diagnostic(
                            sidecar, "missing-reciprocal-parent", parent_name
                        )
                    )


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
    review_status = _nested_status(record, "review")
    if status == "approved" and review_status == "resolved":
        if not _has_settled_resolved_review(path.parent / "review-findings.json"):
            diagnostics.append(_diagnostic(path, "missing-evidence", "review"))
    elif status == "approved" and review_status != "pass":
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


def _has_settled_resolved_review(path: Path) -> bool:
    try:
        value = json.loads(read_regular_text(path))
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(value, dict):
        return False
    items = value.get("items")
    if not isinstance(items, list):
        return False
    return all(_is_terminal_review_item(item) for item in items)


def _is_terminal_review_item(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    decision = item.get("decision")
    if decision in {"decline", "defer", "skip", "duplicate"}:
        return True
    dispatch = item.get("dispatch")
    return (
        decision == "accept"
        and isinstance(dispatch, dict)
        and dispatch.get("state") == "complete"
    )


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
