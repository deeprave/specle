"""Packaged JSON Schema contracts for Specle runtime records."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime, tzinfo
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource

SCHEMA_BASE_URI = "https://github.com/deeprave/specle/schemas"
SCHEMA_IDENTIFIERS = {
    "change-status": f"{SCHEMA_BASE_URI}/change-status/1.0",
    "findings": f"{SCHEMA_BASE_URI}/findings/1.0",
    "tracker-links": f"{SCHEMA_BASE_URI}/tracker-links/1.0",
    "skill-index": f"{SCHEMA_BASE_URI}/skill-index/1.0",
}
_RESOURCE_PATHS = {
    **{
        identifier: f"{name}/1.0.json"
        for name, identifier in SCHEMA_IDENTIFIERS.items()
    },
    f"{SCHEMA_BASE_URI}/common/1.0": "common/1.0.json",
}


class SchemaRegistryError(ValueError):
    """Raised when a packaged contract or its instance cannot be used."""


def schema_identifiers() -> tuple[str, ...]:
    """Return the public contract identifiers in stable order."""
    return tuple(SCHEMA_IDENTIFIERS.values())


def load_schema(identifier: str) -> dict[str, Any]:
    """Load one packaged schema by its stable identifier."""
    resource_path = _RESOURCE_PATHS.get(identifier)
    if resource_path is None:
        supported = ", ".join(schema_identifiers())
        raise SchemaRegistryError(
            f"unknown schema {identifier!r}; supported schemas: {supported}"
        )
    resource = files("specle").joinpath("schemas", *resource_path.split("/"))
    try:
        value = json.loads(resource.read_text())
    except (
        FileNotFoundError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise SchemaRegistryError(
            f"schema resource is unavailable for {identifier!r}"
        ) from error
    if not isinstance(value, dict) or value.get("$id") != identifier:
        raise SchemaRegistryError(f"schema resource is invalid for {identifier!r}")
    try:
        Draft202012Validator.check_schema(value)
    except SchemaError as error:
        raise SchemaRegistryError(
            f"schema resource is invalid for {identifier!r}"
        ) from error
    return value


def validate_instance(instance: Mapping[str, object]) -> str:
    """Validate a contract instance and return its schema identifier."""
    instance = dict(instance)
    identifier = instance.get("$schema")
    if not isinstance(identifier, str):
        raise SchemaRegistryError("contract instance is missing string '$schema'")
    if identifier == SCHEMA_IDENTIFIERS["change-status"]:
        for field in ("created_at", "activated_at"):
            value = instance.get(field)
            if value is not None:
                instance[field] = normalize_change_timestamp(value)
    schema = load_schema(identifier)
    validator = Draft202012Validator(
        schema, registry=_registry(), format_checker=FormatChecker()
    )
    try:
        validator.validate(instance)
    except ValidationError as error:
        location = "/".join(str(part) for part in error.absolute_path) or "root"
        raise SchemaRegistryError(
            f"invalid {identifier!r} instance at {location}: failed {error.validator}"
        ) from error
    return identifier


def normalize_change_timestamp(
    value: object, *, local_timezone: tzinfo | None = None
) -> int | float:
    """Normalize supported timestamp input to canonical Unix seconds."""
    if isinstance(value, bool):
        raise SchemaRegistryError("timestamp must not be a boolean")
    if isinstance(value, int):
        magnitude = abs(value)
        if magnitude >= 100_000_000_000_000_000:
            seconds = value / 1_000_000_000
        elif magnitude >= 100_000_000_000:
            seconds = value / 1_000
        else:
            seconds = value
        return _canonical_unix_seconds(seconds)
    if isinstance(value, float):
        return _canonical_unix_seconds(value)
    if not isinstance(value, str) or "T" not in value:
        raise SchemaRegistryError(
            "timestamp must be a full ISO 8601 datetime or numeric Unix epoch"
        )
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise SchemaRegistryError(
            "timestamp must be a full ISO 8601 datetime"
        ) from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=local_timezone or datetime.now().astimezone().tzinfo
        )
    return _canonical_unix_seconds(parsed.timestamp())


def _canonical_unix_seconds(value: float) -> int | float:
    """Validate Unix seconds and collapse whole-second values to integers."""
    try:
        datetime.fromtimestamp(value, tz=UTC)
    except (OverflowError, OSError, ValueError) as error:
        raise SchemaRegistryError("timestamp epoch is out of range") from error
    return int(value) if float(value).is_integer() else value


def export_schemas(destination: Path, *, force: bool = False) -> Path:
    """Export the complete packaged schema tree using atomic replacement."""
    destination = destination.expanduser().resolve()
    if destination.exists() and not force:
        raise SchemaRegistryError(f"schema destination already exists: {destination}")
    temporary = destination.with_name(f".{destination.name}.tmp-{uuid.uuid4().hex}")
    backup = destination.with_name(f".{destination.name}.backup-{uuid.uuid4().hex}")
    try:
        with as_file(files("specle").joinpath("schemas")) as source:
            shutil.copytree(source, temporary)
        (temporary / "registry.json").write_text(
            json.dumps(_RESOURCE_PATHS, indent=2, sort_keys=True) + "\n"
        )
        if destination.exists():
            os.replace(destination, backup)
        os.replace(temporary, destination)
    except OSError as error:
        if backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise SchemaRegistryError(
            f"unable to export schemas to {destination}"
        ) from error
    finally:
        try:
            _remove_path(temporary)
        except OSError as error:
            raise SchemaRegistryError(
                f"unable to clean up schema export staging at {temporary}"
            ) from error
    if backup.exists():
        try:
            _remove_path(backup)
        except OSError as error:
            raise SchemaRegistryError(
                f"unable to clean up schema export backup at {backup}"
            ) from error
    return destination


def _registry() -> Registry:
    return Registry().with_resources(
        (identifier, Resource.from_contents(load_schema(identifier)))
        for identifier in _RESOURCE_PATHS
    )


def _remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
