# Requirements: add specle update

## Introduction

`specle init <directory>` establishes a Specle deployment, but there is no command that safely brings an existing deployment forward to the package blueprints. Maintainers and users need an explicit update operation that can inspect the current deployment, confirm that it is a valid Specle installation requiring change, and replace only package-managed content.

## Glossary

- **Deployment:** a target directory containing a Specle-managed `.agents/` distribution.
- **Blueprint inventory:** the packaged `src/specle/blueprints/` distribution scanned from the installed Specle package.
- **Managed content:** skills marked with `specle_group`, package policies, and the generated `skills/specle/index.json` resource.
- **Drift:** a missing, unexpected, or checksum-modified managed skill or managed resource relative to the blueprint inventory.

## Requirements

### Requirement 1: Provide an explicit update command

**User Story:** As a Specle user, I want to update a chosen deployment, so its managed skills and policies match the installed Specle package.

#### Acceptance Criteria

1. `specle update <target-directory>` SHALL require an explicit existing target directory and SHALL never infer the current directory.
2. The command SHALL inspect the installed target's `.agents/` directory and the packaged blueprint through the shared managed-inventory operation.
3. The command SHALL reject a target that is not a structurally valid Specle deployment, including unreadable managed files, invalid managed metadata, unsatisfied dependencies, invalid lifecycle declarations, or an invalid generated index.
4. The command SHALL determine drift by comparing the inspected installed and blueprint inventories.
5. If no managed inventory drift exists, the command SHALL report that the deployment is already current and SHALL make no changes.

### Requirement 2: Update only managed content safely

**User Story:** As a deployment owner, I want updates to replace the supplied skills and policies without damaging my own agent configuration.

#### Acceptance Criteria

1. When drift exists, the command SHALL install the blueprint's managed skill directories and package policy documents, remove obsolete managed skills and policies, and regenerate `skills/specle/index.json`.
2. The command SHALL preserve unmarked skills and `.agents/project/`, `.agents/steering/`, and other user-owned content.
3. The command SHALL use the same staged-copy, replacement, backup, and recovery behaviour as initial installation rather than duplicating deployment file operations.
4. The command SHALL make no change if its preflight inspection or staging fails.
5. After a successful update, the command SHALL report the managed destinations updated and the target SHALL pass installed-target validation against its package blueprint.

### Requirement 3: Build on the shared inventory capability

**User Story:** As a maintainer, I want init, update, validation, indexing, and future reconciliation to use the same inventory facts, so their results cannot diverge.

#### Acceptance Criteria

1. Update planning SHALL consume the existing `ManagedInventory` records, checksums, lifecycle analysis, managed-name sets, and the installed/package manifest generations rather than rediscovering or reparsing skills.
2. The code that stages and applies managed deployment changes SHALL be shared between init and update, with each command differing only in its preflight policy and planned destinations.
3. Update SHALL not introduce a second managed-inventory traversal for the same target path during one command invocation.

## Non-Functional Requirements

- Update is read-write only after all required preflight checks have succeeded.
- Update must retain the existing recoverable replacement behaviour and clear error reporting.
- This change depends on `add-specle-manifest`, which supplies the managed distribution's generation and checksum provenance. It does not add a launcher, an index-only command, reconciliation command, or a lifecycle-rendering CLI command.
