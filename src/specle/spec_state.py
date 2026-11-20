"""Durable Specle spec records and local selection helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from specle.schema_registry import (
    SCHEMA_IDENTIFIERS,
    SchemaRegistryError,
    validate_instance,
)

_SPEC_NAME = re.compile(r"\d{12}-[a-z0-9][a-z0-9-]*")


class SpecStateError(ValueError):
    """Raised when durable Specle state cannot be read safely."""


@dataclass(frozen=True, slots=True)
class SpecRecord:
    """One discovered durable spec record."""

    name: str
    directory: Path
    status: dict[str, object]
    archived: bool


@dataclass(frozen=True, slots=True)
class SpecStateSnapshot:
    """A buffered view of durable records and optional local selection."""

    active: tuple[SpecRecord, ...]
    archived: tuple[SpecRecord, ...]
    selected_name: str | None
    diagnostics: tuple[str, ...]


def read_spec_state(target_directory: Path) -> SpecStateSnapshot:
    """Read all discoverable state once without changing the target."""
    target = target_directory.expanduser().resolve()
    diagnostics: list[str] = []
    active = _read_spec_collection(target / ".specle" / "specs", False, diagnostics)
    archived = _read_spec_collection(target / ".specle" / "archive", True, diagnostics)
    _report_duplicate_names(active, archived, diagnostics)
    selected_name = _read_current_spec(target / ".specle" / "current-spec", diagnostics)
    if selected_name is not None and selected_name not in {
        record.name for record in active
    }:
        diagnostics.append(
            f"{target / '.specle' / 'current-spec'}: selected spec is not active: {selected_name}"
        )
    return SpecStateSnapshot(
        tuple(active), tuple(archived), selected_name, tuple(diagnostics)
    )


def resolve_spec(
    snapshot: SpecStateSnapshot, name: str, *, allow_archived: bool = False
) -> SpecRecord:
    """Resolve a stable name to one record, never guessing on ambiguity."""
    records = (*snapshot.active, *(snapshot.archived if allow_archived else ()))
    matches = [record for record in records if record.name == name]
    if len(matches) != 1:
        location = "active or archived" if allow_archived else "active"
        raise SpecStateError(f"no unique {location} spec named {name!r}")
    return matches[0]


def selected_spec(snapshot: SpecStateSnapshot) -> SpecRecord | None:
    """Return the selected active record when a local selector exists."""
    if snapshot.selected_name is None:
        return None
    return resolve_spec(snapshot, snapshot.selected_name)


def _read_spec_collection(
    root: Path, archived: bool, diagnostics: list[str]
) -> list[SpecRecord]:
    if not root.exists():
        return []
    if not root.is_dir():
        diagnostics.append(f"{root}: expected a directory")
        return []
    records: list[SpecRecord] = []
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        if not _SPEC_NAME.fullmatch(directory.name):
            diagnostics.append(f"{directory}: invalid spec directory name")
            continue
        status_path = directory / "status.json"
        status = _read_status(status_path, diagnostics)
        if status is not None:
            records.append(SpecRecord(directory.name, directory, status, archived))
    return records


def _read_status(path: Path, diagnostics: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        diagnostics.append(f"missing {path}")
        return None
    except json.JSONDecodeError as error:
        diagnostics.append(f"{path}: malformed JSON: {error.msg}")
        return None
    except (OSError, UnicodeDecodeError) as error:
        diagnostics.append(f"{path}: unreadable JSON: {error}")
        return None
    if not isinstance(value, dict):
        diagnostics.append(f"{path}: expected a JSON object")
        return None
    try:
        if value.get("$schema") != SCHEMA_IDENTIFIERS["spec-status"]:
            raise SchemaRegistryError(
                f"expected schema {SCHEMA_IDENTIFIERS['spec-status']!r}"
            )
        validate_instance(value)
    except SchemaRegistryError as error:
        diagnostics.append(f"{path}: invalid contract: {error}")
        return None
    return value


def _read_current_spec(path: Path, diagnostics: list[str]) -> str | None:
    try:
        contents = path.read_text()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        diagnostics.append(f"{path}: unreadable selector: {error}")
        return None
    lines = contents.splitlines()
    if len(lines) != 1 or not _SPEC_NAME.fullmatch(lines[0]):
        diagnostics.append(f"{path}: expected one stable spec name")
        return None
    return lines[0]


def _report_duplicate_names(
    active: list[SpecRecord], archived: list[SpecRecord], diagnostics: list[str]
) -> None:
    seen: set[str] = set()
    for record in (*active, *archived):
        if record.name in seen:
            diagnostics.append(f"duplicate spec name: {record.name}")
        seen.add(record.name)
