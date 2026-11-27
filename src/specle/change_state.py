"""Durable Specle change records and local selection helpers."""

from __future__ import annotations

import json
import os
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from specle.file_reading import read_regular_text
from specle.schema_registry import (
    SCHEMA_IDENTIFIERS,
    SchemaRegistryError,
    validate_instance,
)

_WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


class ChangeStateError(ValueError):
    """Raised when durable Specle state cannot be read safely."""


@dataclass(frozen=True, slots=True)
class ChangeRecord:
    """One discovered durable change record."""

    name: str
    directory: Path
    status: dict[str, object]
    archived: bool


@dataclass(frozen=True, slots=True)
class ChangeStateSnapshot:
    """A buffered view of durable records and optional local selection."""

    active: tuple[ChangeRecord, ...]
    archived: tuple[ChangeRecord, ...]
    selected_name: str | None
    diagnostics: tuple[str, ...]


def read_change_state(target_directory: Path) -> ChangeStateSnapshot:
    """Read all discoverable state once without changing the target."""
    target = target_directory.expanduser().resolve()
    diagnostics: list[str] = []
    active = _read_change_collection(target / ".specle" / "changes", False, diagnostics)
    archived = _read_change_collection(
        target / ".specle" / "archive", True, diagnostics
    )
    _report_duplicate_names(active, archived, diagnostics)
    selected_name = _read_current_change(
        target / ".specle" / "current-change", diagnostics
    )
    if selected_name is not None and selected_name not in {
        record.name for record in (*active, *archived)
    }:
        diagnostics.append(
            f"{target / '.specle' / 'current-change'}: selected change is not active: {selected_name}"
        )
    return ChangeStateSnapshot(
        tuple(active), tuple(archived), selected_name, tuple(diagnostics)
    )


def resolve_change(
    snapshot: ChangeStateSnapshot, name: str, *, allow_archived: bool = False
) -> ChangeRecord:
    """Resolve a stable name to one record, never guessing on ambiguity."""
    all_matches = [
        record
        for record in (*snapshot.active, *snapshot.archived)
        if record.name == name
    ]
    if len(all_matches) > 1:
        raise ChangeStateError(f"duplicate change name: {name!r}")
    matches = [
        record for record in all_matches if allow_archived or not record.archived
    ]
    if len(matches) != 1:
        location = "active or archived" if allow_archived else "active"
        raise ChangeStateError(f"no unique {location} change named {name!r}")
    return matches[0]


def _read_change_collection(
    root: Path, archived: bool, diagnostics: list[str]
) -> list[ChangeRecord]:
    if not root.exists():
        return []
    if not root.is_dir():
        diagnostics.append(f"{root}: expected a directory")
        return []
    records: list[ChangeRecord] = []
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        if not _is_change_name(directory.name):
            diagnostics.append(f"{directory}: invalid change directory name")
            continue
        status_path = directory / "status.json"
        status = _read_status(status_path, diagnostics)
        if status is not None:
            records.append(ChangeRecord(directory.name, directory, status, archived))
    return records


def _read_status(path: Path, diagnostics: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(read_regular_text(path))
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
        if value.get("$schema") != SCHEMA_IDENTIFIERS["change-status"]:
            raise SchemaRegistryError(
                f"expected schema {SCHEMA_IDENTIFIERS['change-status']!r}"
            )
        validate_instance(value)
    except SchemaRegistryError as error:
        diagnostics.append(f"{path}: invalid contract: {error}")
        return None
    return value


def _read_current_change(path: Path, diagnostics: list[str]) -> str | None:
    try:
        contents = read_regular_text(path)
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        diagnostics.append(f"{path}: unreadable selector: {error}")
        return None
    lines = contents.splitlines()
    if len(lines) != 1 or not _is_change_name(lines[0]):
        diagnostics.append(f"{path}: expected one stable change name")
        return None
    return lines[0]


def _is_change_name(value: str) -> bool:
    """Return whether value is a safe Unicode name with ASCII dash separators."""
    if value in {"", ".", ".."} or "\x00" in value:
        return False
    if os.sep in value or (os.altsep is not None and os.altsep in value):
        return False
    if unicodedata.normalize("NFC", value) != value:
        return False
    if value.casefold() in _WINDOWS_RESERVED_NAMES:
        return False
    return all(
        part
        and all(
            character.isalnum() or unicodedata.category(character).startswith("M")
            for character in part
        )
        for part in value.split("-")
    )


def _report_duplicate_names(
    active: list[ChangeRecord], archived: list[ChangeRecord], diagnostics: list[str]
) -> None:
    seen: set[str] = set()
    for record in (*active, *archived):
        identity = unicodedata.normalize("NFC", record.name).casefold()
        if identity in seen:
            diagnostics.append(f"duplicate change name: {record.name}")
        seen.add(identity)
