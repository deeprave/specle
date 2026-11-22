"""Shared immutable records for manifest detection and deployment updates."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VersionConfidence = Literal["exact", "likely", "indeterminate"]
UpdateActionKind = Literal["add", "upgrade", "remove", "replace-skill"]


@dataclass(frozen=True, slots=True)
class ManifestGeneration:
    """One complete release checksum inventory from the append-only manifest."""

    version: str
    resources: Mapping[Path, str]


@dataclass(frozen=True, slots=True)
class VersionDetection:
    """A best-effort identification of a deployment's release generation."""

    version: str | None
    confidence: VersionConfidence
    matched: int
    compared: int


@dataclass(frozen=True, slots=True)
class UpdateAction:
    """One selected managed-content action for a version-aware update."""

    action: UpdateActionKind
    path: Path
    requires_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class UpdatePlan:
    """The non-mutating result of comparing a deployment to package provenance."""

    version: str | None
    confidence: VersionConfidence
    matched: int
    compared: int
    actions: tuple[UpdateAction, ...]
    project_guidance: tuple[str, ...]
    declined: tuple[UpdateAction, ...] = ()

    @property
    def converged(self) -> bool:
        """Whether every planned managed-content action was accepted or unnecessary."""
        return not self.declined
