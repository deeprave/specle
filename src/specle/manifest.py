"""Append-only release provenance manifest helpers."""

from __future__ import annotations

import re
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import anyio

if TYPE_CHECKING:
    from specle.inventory import DistributionInventory

from specle.update_models import ManifestGeneration, VersionDetection

_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]*")
_LINE = re.compile(
    r"(?P<version>[A-Za-z0-9][A-Za-z0-9.+-]*):"
    r"(?P<path>skill/[a-z][a-z0-9-]*/[^:\n]+|policies/[^:\n]+):"
    r"(?P<checksum>[0-9a-f]{64})"
)


class ManifestError(ValueError):
    """Raised when a release manifest cannot be safely constructed."""


def build_manifest_lines(
    inventory: DistributionInventory, version: str
) -> tuple[str, ...]:
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


async def append_manifest(
    output: Path, inventory: DistributionInventory, version: str
) -> int:
    """Asynchronously append missing release lines without changing identities."""
    path = anyio.Path(output)
    existing = await _read_manifest_lines(path)
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
    temporary: anyio.Path | None = None
    try:
        for _ in range(10):
            candidate = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
            try:
                handle = await candidate.open("x", encoding="utf-8")
            except FileExistsError:
                continue
            temporary = candidate
            async with handle:
                await handle.write("\n".join((*existing, *additions)) + "\n")
            break
        else:
            raise ManifestError(f"unable to create temporary manifest: {path}")
        await temporary.replace(path)
    except OSError as error:
        if temporary is not None:
            with suppress(OSError):
                await temporary.unlink()
        raise ManifestError(f"unable to write manifest: {path}") from error
    return len(additions)


async def _read_manifest_lines(path: anyio.Path) -> tuple[str, ...]:
    if not await path.exists():
        return ()
    try:
        lines = tuple(line for line in (await path.read_text()).splitlines() if line)
    except (OSError, UnicodeDecodeError) as error:
        raise ManifestError(f"unable to read manifest: {path}") from error
    identities: set[tuple[str, str]] = set()
    for line in lines:
        identity = _line_identity(line)
        if identity in identities:
            raise ManifestError(f"duplicate manifest entry {identity}")
        identities.add(identity)
    return lines


async def read_manifest_generations(
    path: Path,
) -> tuple[ManifestGeneration, ...]:
    """Asynchronously read complete release inventories."""
    return _manifest_generations(await _read_manifest_lines(anyio.Path(path)))


def _manifest_generations(
    lines: tuple[str, ...],
) -> tuple[ManifestGeneration, ...]:
    grouped: dict[str, dict[Path, str]] = {}
    for line in lines:
        match = _LINE.fullmatch(line)
        if match is None:
            raise ManifestError(f"invalid manifest line: {line!r}")
        version = match.group("version")
        manifest_path = Path(match.group("path"))
        if manifest_path.parts[0] == "skill":
            deployed = Path("skills", *manifest_path.parts[1:])
        else:
            deployed = manifest_path
        grouped.setdefault(version, {})[deployed] = match.group("checksum")
    return tuple(
        ManifestGeneration(version, resources) for version, resources in grouped.items()
    )


def detect_installed_version(
    installed: dict[Path, str], generations: tuple[ManifestGeneration, ...]
) -> VersionDetection:
    """Identify the best-supported manifest generation for installed checksums."""
    exact = [
        generation
        for generation in generations
        if dict(generation.resources) == installed
    ]
    if exact:
        generation = exact[-1]
        return VersionDetection(
            generation.version, "exact", len(installed), len(installed)
        )
    scores = []
    for generation in generations:
        expected = generation.resources
        shared_paths = installed.keys() & expected.keys()
        matched = sum(installed[path] == expected[path] for path in shared_paths)
        mismatched = len(shared_paths) - matched
        missing = len(expected.keys() - installed.keys())
        unexpected = len(installed.keys() - expected.keys())
        scores.append((generation, (matched, -mismatched, -missing, -unexpected)))
    if not scores:
        return VersionDetection(None, "indeterminate", 0, len(installed))
    best_score = max(score for _, score in scores)
    best = [generation for generation, score in scores if score == best_score]
    matched = best_score[0]
    if matched == 0 or len(best) != 1:
        return VersionDetection(None, "indeterminate", matched, len(installed))
    generation = best[0]
    return VersionDetection(
        generation.version,
        "likely",
        matched,
        len(installed),
    )


def _line_identity(line: str) -> tuple[str, str]:
    match = _LINE.fullmatch(line)
    if match is None:
        raise ManifestError(f"invalid manifest line: {line!r}")
    return match.group("version"), match.group("path")
