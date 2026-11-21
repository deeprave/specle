# Requirements: add specle manifest

## Introduction

The generated skill index is intentionally an agent-facing discovery resource, not a record of the exact package content installed into a target. Specle needs a separate blueprint manifest that identifies a package generation, records its managed inventory checksums, and preserves a versioned history of prior blueprint files.

## Glossary

- **Blueprint manifest:** a package-owned, machine-readable record of a Specle blueprint generation.
- **Generation:** the package version declared by `pyproject.toml` and the managed blueprint content associated with it.
- **Manifest entry:** the path and SHA-256 checksum of one package-managed blueprint file.
- **Manifest history:** immutable records of earlier package generations and their entries.

## Requirements

### Requirement 1: Generate a current blueprint manifest

**User Story:** As a Specle maintainer, I want a deterministic manifest for the current blueprints, so tools can identify exactly which managed content belongs to the package generation.

#### Acceptance Criteria

1. Specle SHALL generate a package-owned blueprint manifest from the shared managed-inventory result and the version declared by `pyproject.toml`.
2. The current-generation record SHALL include every managed skill resource and package-owned policy resource by stable relative path and SHA-256 checksum.
3. The manifest SHALL exclude itself and generated resources whose inclusion would create a checksum cycle.
4. Generation SHALL run whenever managed blueprint documents or resources change, and validation SHALL fail when the tracked manifest no longer represents the current blueprint inventory.
5. The agent-facing `skills/specle/index.json` SHALL remain limited to skill discovery data and SHALL not become the checksum manifest.

### Requirement 2: Preserve blueprint generation history

**User Story:** As a maintainer or updater, I want checksum records for prior releases, so I can determine when files were introduced, changed, or removed from the managed inventory.

#### Acceptance Criteria

1. The manifest SHALL retain append-only records for prior released package versions alongside the current generation.
2. Every historical record SHALL retain the version and complete managed-file checksum set for that generation.
3. The manifest data SHALL make it possible to determine the first recorded generation containing a path and compare its checksum across generations.
4. Regenerating the manifest for an unchanged version SHALL update only that version's current development record and SHALL not rewrite prior-version records.
5. A new package version SHALL preserve all prior records before adding its own generation record.

### Requirement 3: Distribute and validate the manifest

**User Story:** As a Specle user, I want an installed manifest, so update and validation can report the installed generation as well as actual content drift.

#### Acceptance Criteria

1. Init SHALL install the package-owned manifest as part of the managed distribution.
2. Installed-target validation SHALL validate the installed manifest's structure and report whether it represents the installed package generation, while continuing to inspect actual managed files rather than trusting the manifest alone.
3. Blueprint validation SHALL validate the manifest against the current shared inventory and package version.
4. The manifest location and ownership semantics SHALL be explicit, and it SHALL be handled by the same staged replacement and recovery mechanism as other managed distribution content.

## Non-Functional Requirements

- The manifest format must be versioned and suitable for schema validation.
- Manifest creation must consume the shared inventory result rather than reparsing blueprint files.
- Historical records are package provenance, not user-project state.
- This change is an explicit prerequisite for `add-specle-update`; update will use the manifest for generation reporting but will still perform live inventory comparison.
