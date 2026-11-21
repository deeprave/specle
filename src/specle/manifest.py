"""Append-only release provenance manifest helpers."""

from __future__ import annotations

import re
from pathlib import Path

from specle.inventory import ManagedInventory

_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]*")
_LINE = re.compile(
    r"(?P<version>[A-Za-z0-9][A-Za-z0-9.+-]*):"
    r"(?P<path>skill/[a-z][a-z0-9-]*/[^:\n]+|policies/[^:\n]+):"
    r"(?P<checksum>[0-9a-f]{64})"
)


class ManifestError(ValueError):
    """Raised when a release manifest cannot be safely constructed."""


def build_manifest_lines(inventory: ManagedInventory, version: str) -> tuple[str, ...]:
    """Build stable text manifest lines from one shared managed inventory."""
    if not _VERSION.fullmatch(version):
        raise ManifestError(f"invalid manifest version: {version!r}")
    lines: list[str] = []
    for skill in inventory.skills:
        for resource in skill.resources:
            parts = resource.path.parts
            relative = "/".join(parts[2:])
            lines.append(
                f"{version}:skill/{skill.metadata.name}/{relative}:{resource.checksum}"
            )
    for resource in inventory.resources:
        relative = "/".join(resource.path.parts[1:])
        lines.append(f"{version}:policies/{relative}:{resource.checksum}")
    return tuple(sorted(lines))


def append_manifest(output: Path, inventory: ManagedInventory, version: str) -> int:
    """Append missing release lines without changing existing identities."""
    existing = _read_manifest_lines(output)
    identities = {_line_identity(line): line for line in existing}
    additions: list[str] = []
    for line in build_manifest_lines(inventory, version):
        identity = _line_identity(line)
        previous = identities.get(identity)
        if previous is None:
            additions.append(line)
        elif previous != line:
            raise ManifestError(f"conflicting checksum for manifest entry {identity}")
    if not additions:
        return 0
    temporary = output.with_name(f".{output.name}.tmp")
    try:
        temporary.write_text("\n".join((*existing, *additions)) + "\n")
        temporary.replace(output)
    except OSError as error:
        raise ManifestError(f"unable to write manifest: {output}") from error
    return len(additions)


def _read_manifest_lines(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()
    try:
        lines = tuple(line for line in path.read_text().splitlines() if line)
    except OSError as error:
        raise ManifestError(f"unable to read manifest: {path}") from error
    identities: set[tuple[str, str]] = set()
    for line in lines:
        identity = _line_identity(line)
        if identity in identities:
            raise ManifestError(f"duplicate manifest entry {identity}")
        identities.add(identity)
    return lines


def _line_identity(line: str) -> tuple[str, str]:
    match = _LINE.fullmatch(line)
    if match is None:
        raise ManifestError(f"invalid manifest line: {line!r}")
    return match.group("version"), match.group("path")
