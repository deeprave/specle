# Requirements: add specle manifest

## Introduction

The generated skill index is intentionally an agent-facing discovery resource, not a record of the exact package content installed into a target. Specle needs a separate blueprint manifest that identifies a package generation, records its managed inventory checksums, and preserves a versioned history of prior blueprint files.

## Glossary

- **Blueprint manifest:** a package-owned, line-oriented text record of released Specle blueprint resources.
- **Generation:** one released package version and the managed blueprint content associated with it.
- **Manifest entry:** one immutable text line containing a `version`, blueprint-relative `path`, and SHA-256 `checksum` for a package-managed blueprint file.
- **Manifest history:** the append-only collection of release resource entries.

## Requirements

### Requirement 1: Generate a current blueprint manifest

**User Story:** As a Specle maintainer, I want a deterministic manifest for the current blueprints, so tools can identify exactly which managed content belongs to the package generation.

#### Acceptance Criteria

1. `specle manifest <output>` SHALL append package-owned blueprint manifest lines from the shared managed-inventory result and the package version exposed by `specle.__version__`, loaded through `importlib`.
2. The appended lines SHALL include every managed skill resource as `version:skill/<skill>/<path>:checksum` and every package-owned policy as `version:policies/<document>:checksum`.
3. The manifest SHALL exclude itself and generated resources whose inclusion would create a checksum cycle.
4. Manifest generation SHALL be a release-preparation action. It SHALL create the initial manifest when the output is absent and append only resource entries whose `(version, path)` identity is not already recorded.
5. The agent-facing `skills/specle/index.json` SHALL remain limited to skill discovery data and SHALL not become the checksum manifest.

### Requirement 2: Preserve blueprint generation history

**User Story:** As a maintainer or updater, I want checksum records for prior releases, so I can determine when files were introduced, changed, or removed from the managed inventory.

#### Acceptance Criteria

1. The manifest SHALL retain append-only resource records for released package versions.
2. Every historical record SHALL retain the version and complete managed-file checksum set for that generation.
3. The manifest data SHALL make it possible to determine the first recorded generation containing a path and compare its checksum across generations.
4. Generation SHALL not update or add a line for an already recorded `(version, path)` identity. A different checksum for that identity SHALL fail without modifying the output.
5. A new package version SHALL preserve all prior records before appending its own complete resource inventory.

### Requirement 3: Provide release-manifest tooling and documentation

**User Story:** As a Specle maintainer, I want a clear release-preparation command and reference so I can create immutable blueprint provenance records reliably.

#### Acceptance Criteria

1. The `manifest` CLI command SHALL accept an explicit output path and write atomically without modifying `.agents/` or any installed target.
2. The command SHALL validate existing manifest structure and reject invalid checksums, duplicate resource identities, or a conflicting checksum for an existing `(version, path)` identity before replacing its output.
3. Documentation under `docs/` SHALL explain the release-preparation workflow, entry format, append-only lifecycle, and provenance queries for first appearance, retirement, and checksum changes.
4. The manifest SHALL be a blueprint document only; it SHALL not be installed, copied to `.agents/`, used as runtime state, or used for installed-target drift validation.

## Non-Functional Requirements

- The manifest format must be line-oriented, versioned, and safely parseable without JSON or YAML.
- Manifest creation must consume the shared inventory result rather than reparsing blueprint files.
- Historical records are release provenance, not user-project state or development-state inventory.
- The package SHALL expose `__version__` from `specle.__init__`; manifest generation reads it through `importlib` rather than accepting a version argument.
- This change is an explicit prerequisite for `add-specle-update`; update will use the manifest for generation reporting but will still perform live inventory comparison.
