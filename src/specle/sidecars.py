"""Durable reciprocal relationships for concurrent abbreviated work."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

from specle.change_state import ChangeRecord

CONCURRENT_DELIVERY = "with-related-change"
_SIDECAR_KINDS = frozenset(("bugfix", "refactor"))


class SidecarRelationshipError(ValueError):
    """Raised when a reciprocal sidecar relationship cannot be recorded safely."""


def record_sidecar_relationship(parent: ChangeRecord, sidecar: ChangeRecord) -> None:
    """Record matching concurrent-delivery relationships on two active records.

    Replacement stages both complete JSON documents before either destination changes. If the
    second replacement fails, the first destination is restored from its captured original bytes.
    """
    _require_active_parent(parent)
    sidecar_kind = sidecar.status.get("kind")
    if (
        sidecar.archived
        or not isinstance(sidecar_kind, str)
        or sidecar_kind not in _SIDECAR_KINDS
    ):
        raise SidecarRelationshipError(
            f"{sidecar.directory}: expected an active bugfix or refactor sidecar"
        )

    parent_status = _with_relationship(
        parent.status,
        {"change": sidecar.name, "type": sidecar_kind, "delivery": CONCURRENT_DELIVERY},
        parent.directory / "status.json",
    )
    sidecar_status = _with_relationship(
        sidecar.status,
        {"change": parent.name, "type": "origin", "delivery": CONCURRENT_DELIVERY},
        sidecar.directory / "status.json",
    )
    _replace_statuses_atomically(
        {
            parent.directory / "status.json": parent_status,
            sidecar.directory / "status.json": sidecar_status,
        }
    )


def _require_active_parent(parent: ChangeRecord) -> None:
    if parent.archived or parent.status.get("kind") != "change":
        raise SidecarRelationshipError(
            f"{parent.directory}: expected an active normal parent change"
        )


def _with_relationship(
    status: dict[str, object], relationship: dict[str, str], path: Path
) -> dict[str, object]:
    relationships = status.get("relationships")
    if not isinstance(relationships, list):
        raise SidecarRelationshipError(f"{path}: invalid relationships collection")
    if relationship in relationships:
        raise SidecarRelationshipError(f"{path}: duplicate reciprocal relationship")
    updated = copy.deepcopy(status)
    updated_relationships = updated.get("relationships")
    if not isinstance(updated_relationships, list):
        raise SidecarRelationshipError(f"{path}: invalid relationships collection")
    updated_relationships.append(relationship)
    return updated


def _replace_statuses_atomically(statuses: dict[Path, dict[str, object]]) -> None:
    originals = {path: path.read_bytes() for path in statuses}
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, status in statuses.items():
            staged[path] = _stage_status(path, status)
        for path in statuses:
            os.replace(staged[path], path)
            replaced.append(path)
    except OSError as error:
        recovery_errors = _restore_replaced_statuses(replaced, originals)
        detail = f"could not write reciprocal sidecar records: {error}"
        if recovery_errors:
            detail = f"{detail}; recovery failed: {'; '.join(recovery_errors)}"
        raise SidecarRelationshipError(detail) from error
    finally:
        for staged_path in staged.values():
            try:
                staged_path.unlink()
            except FileNotFoundError:
                pass


def _stage_status(path: Path, status: dict[str, object]) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(status, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _restore_replaced_statuses(
    replaced: list[Path], originals: dict[Path, bytes]
) -> list[str]:
    errors: list[str] = []
    for path in reversed(replaced):
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                dir=path.parent, prefix=f".{path.name}.", suffix=".restore"
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(originals[path])
            os.replace(temporary, path)
        except OSError as error:
            errors.append(f"{path}: {error}")
    return errors
