# Requirements: add specle update

## Introduction

`specle init <directory>` establishes a Specle deployment, but there is no command that safely brings an existing deployment forward to the package blueprints. Maintainers and users need an explicit update operation that can inspect the current deployment, confirm that it is a valid Specle installation requiring change, and replace only package-managed content.

## Glossary

- **Deployment:** a target directory containing a Specle-managed `.agents/` distribution.
- **Distribution inventory:** the complete scanned state of a packaged or installed `.agents/` distribution, including managed skills and policies plus known unmanaged conflicts.
- **Manifest generation:** the complete, versioned checksum inventory for one released package version in the package-owned source manifest.
- **Managed content:** skills marked with `specle_group`, package policies, and the generated `skills/specle/index.json` resource.
- **Drift:** a missing, unexpected, or checksum-modified managed skill or managed resource relative to the blueprint inventory.
- **Update plan:** the detected installed version, its confidence, and the additions, replacements, removals, preserves, and project guidance that update would report or apply.
- **Conflict:** a managed resource modified since its detected generation, or an unmanaged scanned resource occupying an incoming managed path.

## Requirements

### Requirement 1: Provide an explicit update command

**User Story:** As a Specle user, I want to update a chosen deployment, so its managed skills and policies match the installed Specle package.

#### Acceptance Criteria

1. `specle update <target-directory>` SHALL require an explicit existing target directory and SHALL never infer the current directory.
2. The command SHALL inspect the installed target's `.agents/` directory and the packaged blueprint through the shared managed-inventory operation.
3. The command SHALL reject a target that is not a structurally valid Specle deployment, including unreadable managed files, invalid managed metadata, unsatisfied dependencies, invalid lifecycle declarations, or an invalid generated index.
4. The command SHALL identify an exact package manifest generation before partial version scoring and report confidence with its evidence. Equivalent exact generations with identical inventories SHALL be reported as `exact` using the latest matching release version.
5. The command SHALL determine drift and its update plan from the detected generation, the current package generation, and the inspected installed and blueprint inventories.
6. If no managed inventory drift exists, the command SHALL report that the deployment is already current and SHALL make no changes.

### Requirement 2: Preview an update without mutation

**User Story:** As a Specle user, I want to preview an update, so I can understand the detected installation and intended changes before writing to my deployment.

#### Acceptance Criteria

1. `specle update <target-directory> --dry-run` SHALL make no filesystem changes.
2. The dry-run report SHALL show the detected installed version and a reasonable-confidence classification.
3. The dry-run report SHALL list managed resources that would be added, upgraded, removed, or require confirmation because of a conflict.
4. If project-owned files are missing or unexpected, the dry run SHALL report them without modifying them and suggest `onboard`.

### Requirement 3: Update only managed content safely

**User Story:** As a deployment owner, I want updates to replace the supplied skills and policies without damaging my own agent configuration.

#### Acceptance Criteria

1. When drift exists, the command SHALL report the detected version and update plan before applying it.
2. A managed policy resource whose installed checksum matches its detected-generation checksum and differs from the current-generation checksum SHALL be upgraded to the current package resource.
3. A managed skill, including every resource in its directory, SHALL be planned and applied as one atomic unit. If any installed resource differs from its detected-generation checksum, the entire skill replacement or removal SHALL require confirmation; the command SHALL never partially replace or retire a managed skill.
4. A managed policy resource present in the detected generation but absent from the current generation SHALL be removed only when its installed checksum matches the detected-generation checksum.
5. A managed policy resource absent from the detected generation and present in the current generation SHALL be added.
6. Before overwriting or removing a modified managed policy resource, or before replacing an unmanaged scanned resource at an incoming managed path, the command SHALL report every affected action as requiring confirmation. Without `--yes` or `--force`, it SHALL make no changes and exit non-zero after reporting the complete plan.
7. `specle update <target-directory> --yes` SHALL approve every confirmation-required action in the displayed selective update plan without interactive input.
8. The command SHALL regenerate `skills/specle/index.json` after applying managed changes from the resulting installed managed inventory. The index SHALL be generated after managed actions, not staged as package content.
9. The command SHALL preserve unmarked skills and `.agents/project/`, `.agents/steering/`, and other user-owned content unless `--yes` approves replacement of a same-named conflicting skill.
10. The command SHALL use the same staged-copy, replacement, backup, and recovery behaviour as initial installation rather than duplicating deployment file operations.
11. The command SHALL make no change if its preflight inspection or staging fails, and SHALL remove every temporary staging path created before a caught copy failure as well as empty directories created solely by failed staging or apply work.
12. The command SHALL apply the single displayed update plan rather than reconstructing it before application.
13. After every update attempt that applies managed actions, the command SHALL run installed-target validation and report its result. A fully converged target SHALL pass validation.

### Requirement 4: Force a full managed replacement

**User Story:** As a Specle user, I want an explicit force mode, so I can deliberately replace managed inventory when normal version-aware preservation is not appropriate.

#### Acceptance Criteria

1. `specle update <target-directory> --force` SHALL use the same managed-content replacement behaviour as `specle init <target-directory> --force`.
2. Force mode SHALL still preserve unmarked skills and project-, steering-, and other user-owned content outside replaced managed-skill destinations.
3. Force mode SHALL report that it bypasses all normal update confirmations; dry-run output SHALL state that it would bypass them if applied.

### Requirement 5: Build on the shared inventory capability

**User Story:** As a maintainer, I want init, update, validation, indexing, and future reconciliation to use the same inventory facts, so their results cannot diverge.

#### Acceptance Criteria

1. Update planning SHALL consume the existing blueprint and installed `DistributionInventory` records, including managed and unmanaged scanned resource paths, checksums, lifecycle analysis, managed-name sets, and package manifest generations rather than rediscovering or reparsing skills.
2. The code that stages and applies managed deployment changes SHALL be shared between init and update, with each command differing only in its preflight policy and planned destinations.
3. Update planning SHALL not introduce a second managed-inventory traversal for the same target path before applying its displayed plan. Post-update validation may inspect the resulting target.
4. Update SHALL read the package manifest only as release provenance. It SHALL not install or copy that manifest into a target deployment.
5. Update planning and transaction models SHALL be separated from distribution scanning. Its action and confidence values SHALL be explicit closed types rather than unconstrained strings.

## Non-Functional Requirements

- Update is read-write only after all required preflight checks have succeeded; dry-run is read-only.
- Update must retain the existing recoverable replacement behaviour and clear error reporting.
- Update SHALL not prompt interactively. It SHALL report every confirmation-required action in one plan, and require `--yes` for selective conflict approval or `--force` for full managed replacement.
- The asynchronous command path SHALL use AnyIO-compatible scan/read work and call reusable validation functionality directly rather than recursively invoking the top-level CLI entrypoint.
- Version detection is best-effort: user modifications, missing managed resources, and ambiguous checksum matches reduce confidence and must be reported rather than silently treated as certainty.
- This change depends on `add-specle-manifest`, which supplies the package's versioned managed-resource checksum history. It does not add a launcher, an index-only command, reconciliation command, or a lifecycle-rendering CLI command.
