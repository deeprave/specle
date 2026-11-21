# Add specle manifest

## Problem

The skill index is a lean agent-discovery resource and cannot identify which complete blueprint generation is installed. Update needs package provenance and checksum history without overloading that index.

## Goal

Create, distribute, and validate a separate versioned blueprint manifest containing current managed-resource checksums and historical package-generation records.

## Direction

Generate the current record from the shared managed inventory and `pyproject.toml` version whenever managed blueprints change. Preserve complete prior-version checksum maps so file introduction, change, and removal can be derived. Keep the manifest separate from `index.json`, validate it against live scans, and distribute it through init's transactional managed-content path.

## Verification

Test deterministic current-manifest generation, stale-manifest detection, version-history preservation, path-introduction history, install/update distribution, and live-file drift validation. Run the repository quality gates.
