# Requirements: support blueprint validate

## Introduction

`specle validate <target-directory>` is a public command for an installed Specle target. It currently validates the target’s marked skills, generated index, lifecycle declarations, and runtime state. The repository’s document-validation workflow invokes that installed-target mode against the tracked `.agents/` mirror, while blueprint lifecycle coherence is separately covered by tests.

Specle needs an explicit blueprint-validation mode so source workflow declarations can be checked directly and installed targets can additionally be checked for unexpected drift.

## Glossary

- **Installed target:** a directory containing an `.agents/` inventory and optional `.specle/` runtime state.
- **Blueprint:** the packaged `src/specle/blueprints/` distribution source.
- **Managed skill:** a skill marked with `specle_group`; unmarked skills remain user or project owned.
- **Inventory record:** one managed skill and its package-owned resources, represented by its name, parsed metadata, stable checksums for every enclosed resource, and the shared lifecycle analysis derived from the full record collection.

## Requirements

### Requirement 1: Preserve installed-target validation as the default

**User Story:** As an installer or repository owner, I want `specle validate` to validate an installed target by default, so I can detect a stale, overwritten, missing, or locally modified managed inventory.

#### Acceptance Criteria

1. `specle validate <target-directory>` SHALL continue to validate the target’s managed inventory, generated index, lifecycle graph, and runtime state.
2. The command SHALL scan its installed `.agents/` inventory through the same inventory-scanning function used for packaged blueprints, producing managed inventory records with parsed metadata and resource checksums.
3. The command SHALL compare installed and packaged inventory records, and SHALL fail with an actionable diagnostic for a missing, modified, or unexpected managed skill or resource.
4. Skills without `specle_group` SHALL remain outside managed-inventory comparison and SHALL not cause validation failure.
5. The command SHALL identify an installed inventory originating from a different Specle version as requiring an update or validation with its matching package version.
6. An installed target with zero managed skills SHALL remain inspectable so comparison reports every expected managed skill as missing; a package blueprint SHALL still require its complete managed inventory.

### Requirement 2: Add explicit blueprint validation

**User Story:** As a Specle maintainer, I want to validate package blueprints directly, so source workflow changes are checked without relying on a checked-in installed mirror.

#### Acceptance Criteria

1. `specle validate --blueprint` SHALL resolve the packaged blueprint resource to a filesystem path, scan it through the shared inventory-scanning function, and validate the resulting inventory without requiring an installed target directory.
2. Blueprint validation SHALL validate the blueprint skill frontmatter, dependency declarations, resource checksums, generated inventory model, and lifecycle graph.
3. Blueprint validation SHALL not perform installed-target checksum or content-drift comparison.
4. The command-line interface SHALL reject ambiguous invocation that combines blueprint mode with an installed target directory.
5. Verbose output SHALL identify whether installed-target or blueprint validation ran and report the validated inventory summary.
6. Blueprint validation SHALL reject an incomplete package distribution using package-completeness diagnostics returned by the shared inventory result, including the required `specle` skill and package policy inventory.
7. Inspection failures in either validation mode SHALL be reported as concise validation diagnostics without a traceback.

### Requirement 3: Preserve explicit policy ownership

**User Story:** As a project owner, I want package policy updates to preserve my own policy files, so Specle never deletes documents it does not own.

#### Acceptance Criteria

1. Package policies SHALL remain top-level Markdown documents; nested and binary policy resources are outside the managed distribution contract.
2. Every package-owned policy document SHALL declare a standard YAML-frontmatter ownership marker.
3. Init and validation SHALL use the same top-level Markdown and ownership-marker rule when inspecting package policies.
4. Init SHALL remove only obsolete policy documents carrying the Specle ownership marker and SHALL never remove user-added policy files.
5. The obsolete standalone `discover_policies` compatibility helper and its test-only callers SHALL be removed; policy information shall be consumed through the shared inventory result.

### Requirement 4: Run the appropriate validation in CI

**User Story:** As a maintainer, I want the required test workflow to validate source lifecycle declarations, so broken blueprint transitions cannot pass Verify.

#### Acceptance Criteria

1. The Test workflow’s `Verify` dependency set SHALL run `specle validate --blueprint --verbose`.
2. The document-validation workflow SHALL no longer run installed-target `specle validate`.
3. Existing document prose checks SHALL remain unchanged.

## Non-Functional Requirements

- One authoritative inventory operation must perform the only managed-skill traversal for each root. It must parse metadata, validate direct dependencies, calculate checksums, derive lifecycle graph analysis and diagnostics, and return all of those results together.
- Initialisation, index construction, installed-target validation, update/reconciliation planning, and future lifecycle rendering must consume that result rather than independently rediscovering or reparsing skills.
- Blueprint and installed-target modes may differ only in the root directory supplied and whether their resulting records are compared or runtime state is inspected.
- The shared inventory operation SHALL return package-completeness diagnostics alongside its managed-policy ownership analysis; callers must consume those diagnostics directly and must not replicate or separately invoke those rules.
- The two modes must have explicit, non-overlapping command syntax and diagnostics.
- Installed-target validation must remain read-only.
- This change is independent of `address-security-findings`; it may be implemented or delivered separately.
