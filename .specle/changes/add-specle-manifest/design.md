# Design: add Specle manifest

## Overview

Add an append-only text manifest that records every managed blueprint resource in a released package version. It is release provenance only: separate from the agent-facing skill index, never installed into `.agents/`, and never used as runtime or target state.

## Architecture

```text
shared managed-inventory scan ─> manifest line builder ─> explicit output path
importlib.import_module("specle").__version__ ─> release version
```

The manifest module receives one already-scanned `ManagedInventory` and the package version loaded through `importlib`. It converts skill resources and package policies into stable text lines, so it never performs a second blueprint-tree traversal. The generated skill index is already absent from the inventory resource set and is never represented in the manifest.

`specle manifest <output>` reads the explicit output if it exists, validates its lines, derives the current release inventory, appends only missing resource lines, and atomically replaces the output. It does not inspect, create, copy to, or validate `.agents/`.

## Data format

Each non-empty line has one of these forms:

```text
<version>:skill/<skill>/<path>:<sha256>
<version>:policies/<document>:<sha256>
```

`<version>` is the package `__version__`. `<sha256>` is a lowercase 64-character digest. The line identity is `(version, path)`; an identical existing line is retained without a duplicate, while a different checksum for the same identity is a failure. Filtering all lines by `<version>` reconstructs that release's complete inventory. Comparing paths across versions reveals first appearance and retirement; comparing their checksums reveals changes.

The source repository seeds `src/specle/blueprints/manifest` with the current release inventory. New releases run the CLI as release preparation and commit the appended lines with the version change.

## Error handling

- Fail generation when an existing line is malformed, a resource identity is duplicated, a checksum is invalid, or the same `(version, path)` has a conflicting checksum.
- On failure, leave the existing output unchanged.
- An absent output creates a new manifest. An existing identical line is a no-op and is never rewritten.
- Do not alter init, installed-target validation, user-owned `.agents/project/`, steering content, or any installed target.

## Report/output rendering

Keep command output concise: report the package version, count of appended lines, and output path. Failures identify the output path and offending line or resource identity.

## Test strategy

- Test deterministic text-line construction from a supplied managed inventory, including skill and policy paths and exclusion of generated resources.
- Test parsing, initial-output creation, append from a valid partial manifest, repeated-entry no-op behaviour, conflicting-checksum and duplicate-identity rejection, malformed-line rejection, and preservation of prior lines.
- Test CLI argument handling, `importlib` version loading, output errors, and that init and installed-target validation remain unaffected.
- Add the current initial release inventory under `src/specle/blueprints/` and document release preparation and provenance queries under `docs/`.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, blueprint validation, installed-target validation, and pre-commit.
