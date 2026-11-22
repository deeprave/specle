# Add release skill

## Problem

This repository lacks a defined release-preparation workflow. Version updates and manifest provenance need to be applied together, while release commits intentionally include all working-tree changes rather than attempting to classify their relationship to a release.

## Goal

Add a repository-local `release` skill that prepares an authorised release commit only after confirming there is no active Specle work and no open GitHub pull request.

## Direction

The skill accepts a user-supplied version or asks for one, canonicalises it with PEP 440 semantics, validates that the manifest can represent it, and compares it to the checked-out `pyproject.toml` version. It synchronises the configured delivery branch, then updates the version and appends the current blueprint checksum inventory through `uv run specle manifest`. It creates `chore/release_<canonical-version>`, displays the complete release commit contents, receives explicit authorisation, and commits every working-tree change. It does not push, open a PR, publish, tag, or create a GitHub release. The skill is local to this repository and must not enter Specle's managed blueprint or manifest inventory.

## Verification

Review the skill's guards, version comparison, manifest invocation, branch naming, full-tree staging rule, confirmation boundary, and managed-inventory exclusion. Run the repository quality gates appropriate to the change.
