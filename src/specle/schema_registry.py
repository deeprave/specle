"""Packaged JSON Schema contracts for Specle runtime records."""

from __future__ import annotations

import json
import uuid
from collections.abc import Mapping
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

import anyio
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource

SCHEMA_BASE_URI = "specle://schemas"
SCHEMA_IDENTIFIERS = {
    "change-status": f"{SCHEMA_BASE_URI}/change-status/1.0",
    "context": f"{SCHEMA_BASE_URI}/context/1.0",
    "findings": f"{SCHEMA_BASE_URI}/findings/1.0",
    "tracker-links": f"{SCHEMA_BASE_URI}/tracker-links/1.0",
    "skill-index": f"{SCHEMA_BASE_URI}/skill-index/1.0",
}
_RESOURCE_PATHS = {
    **{
        identifier: f"{name}/1.0.json"
        for name, identifier in SCHEMA_IDENTIFIERS.items()
    },
}


class SchemaRegistryError(ValueError):
    """Raised when a packaged contract or its instance cannot be used."""


def schema_identifiers() -> tuple[str, ...]:
    """Return the public contract identifiers in stable order."""
    return tuple(SCHEMA_IDENTIFIERS.values())


async def load_schema(identifier: str) -> dict[str, Any]:
    """Load one packaged schema by its stable identifier."""
    resource_path = _RESOURCE_PATHS.get(identifier)
    if resource_path is None:
        supported = ", ".join(schema_identifiers())
        raise SchemaRegistryError(
            f"unknown schema {identifier!r}; supported schemas: {supported}"
        )
    resource = files("specle").joinpath("schemas", *resource_path.split("/"))
    try:
        with as_file(resource) as resource_path:
            value = json.loads(await anyio.Path(resource_path).read_text())
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


async def validate_instance(instance: Mapping[str, object]) -> str:
    """Validate a contract instance and return its schema identifier."""
    instance = dict(instance)
    identifier = instance.get("$schema")
    if not isinstance(identifier, str):
        raise SchemaRegistryError("contract instance is missing string '$schema'")
    schema = await load_schema(identifier)
    validator = Draft202012Validator(schema, registry=await _registry())
    try:
        validator.validate(instance)
    except ValidationError as error:
        location = "/".join(str(part) for part in error.absolute_path) or "root"
        raise SchemaRegistryError(
            f"invalid {identifier!r} instance at {location}: failed {error.validator}"
        ) from error
    return identifier


async def export_schemas(destination: Path, *, force: bool = False) -> Path:
    """Asynchronously export the packaged schema tree with atomic replacement."""
    resolved = await anyio.Path(destination).expanduser()
    resolved = await resolved.resolve()
    if await resolved.exists() and not force:
        raise SchemaRegistryError(f"schema destination already exists: {resolved}")
    temporary = resolved.with_name(f".{resolved.name}.tmp-{uuid.uuid4().hex}")
    backup = resolved.with_name(f".{resolved.name}.backup-{uuid.uuid4().hex}")
    try:
        with as_file(files("specle").joinpath("schemas")) as source:
            await _copy_tree(anyio.Path(source), temporary)
        await (temporary / "registry.json").write_text(
            json.dumps(_RESOURCE_PATHS, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with anyio.CancelScope(shield=True):
            if await resolved.exists():
                await resolved.replace(backup)
            await temporary.replace(resolved)
            if await backup.exists():
                try:
                    await _remove_path(backup)
                except OSError as error:
                    raise SchemaRegistryError(
                        f"unable to clean up schema export backup at {backup}"
                    ) from error
    except OSError as error:
        if await backup.exists() and not await resolved.exists():
            await backup.replace(resolved)
        raise SchemaRegistryError(f"unable to export schemas to {resolved}") from error
    finally:
        with anyio.CancelScope(shield=True):
            try:
                await _remove_path(temporary)
            except OSError as error:
                raise SchemaRegistryError(
                    f"unable to clean up schema export staging at {temporary}"
                ) from error
    return Path(resolved)


async def _registry() -> Registry:
    resources = []
    for identifier in _RESOURCE_PATHS:
        resources.append(
            (identifier, Resource.from_contents(await load_schema(identifier)))
        )
    return Registry().with_resources(resources)


async def _copy_tree(source: anyio.Path, destination: anyio.Path) -> None:
    await destination.mkdir(parents=True)
    async for child in source.iterdir():
        target = destination / child.name
        if await child.is_dir():
            await _copy_tree(child, target)
        else:
            await target.write_bytes(await child.read_bytes())


async def _remove_path(path: anyio.Path) -> None:
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
