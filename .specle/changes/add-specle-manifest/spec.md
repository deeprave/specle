# Add specle manifest

## Problem

The skill index is a lean agent-discovery resource and cannot identify which complete blueprint generation is installed. Update needs package provenance and checksum history without overloading that index.

## Goal

Create an append-only, versioned text manifest containing complete released managed-resource checksum inventories, with a source-only CLI command and documentation for release preparation.

## Direction

Use `specle.__version__`, obtained through `importlib`, when `specle manifest <output>` is run during release preparation. Create the initial output or append one complete immutable inventory for the new version. Keep the manifest separate from `index.json`, `.agents/`, installed-target validation, and runtime state.

## Verification

Test deterministic manifest-line generation, generated-index exclusion, append-only history behaviour, conflicting-entry rejection, CLI version loading, and the source-only boundary. Run the repository quality gates.
