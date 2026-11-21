# Requirements: remove spec stamp prefix

## Introduction

Specle currently prefixes every active and archived change directory with a creation timestamp. The prefix was intended only to provide ordering, but it makes change names unnecessarily long and duplicates information that belongs in durable metadata. The workflow also uses “spec” ambiguously for both `spec.md` and the change directory that contains it.

## Glossary

- **Change:** one durable unit of planned or delivered work, stored as a directory beneath `.specle/changes/` while active or `.specle/archive/` after completion.
- **Change slug:** the short, human-readable unique directory name for a change, such as `add-online-install`.
- **Created timestamp:** Unix seconds recorded as a JSON number in `status.json` when a change is first created.
- **Activated timestamp:** Unix seconds recorded as a JSON number when `activate` first selects a change in a worktree; it is `null` until activation.

## Requirements

### Requirement 1: Use unique slugs as change directory names

**User Story:** As a developer, I want to refer to a change by a concise slug rather than a timestamp-prefixed path.

#### Acceptance Criteria

1. New active changes SHALL be created beneath `.specle/changes/<name>/` without adding an automatic datetime prefix.
2. A change slug SHALL be unique across both `.specle/changes/` and `.specle/archive/` after NFC normalization and Unicode case folding.
3. IF an attempted new slug already exists in either collection, THEN creation SHALL fail with an actionable collision diagnostic.
4. Lifecycle commands that accept a named change SHALL resolve its exact unique name without applying a timestamp-prefix convention.
5. The active and archive collection paths SHALL be `.specle/changes/` and `.specle/archive/`.

### Requirement 2: Record creation and activation time in durable state

**User Story:** As a developer, I want temporal information stored as state rather than encoded in a directory name.

#### Acceptance Criteria

1. Every change `status.json` SHALL contain `created_at` and `activated_at` fields.
2. Timestamp input SHALL accept a full naive ISO 8601 datetime, an offset-aware ISO 8601 datetime, or an integer Unix epoch expressed in milliseconds or nanoseconds. A naive datetime SHALL be interpreted in the user's current timezone; date-only values SHALL be rejected.
3. Accepted timestamps SHALL be normalized to Unix seconds as a JSON number before durable state is recorded. A fractional value SHALL be used only when needed for sub-second precision. `activated_at` SHALL be `null` before first activation and SHALL be set once on first successful activation using that normalized representation.
4. Subsequent activation or continuation of a change SHALL preserve its original `activated_at` value.
5. A custom timestamp normalizer SHALL convert accepted input forms to the durable representation at an explicit write boundary. Durable-record validation SHALL reject values that are not already canonical numeric Unix seconds.

### Requirement 2a: Support Unicode change names

**User Story:** As a developer, I want to name a change with filesystem-compatible Unicode characters without losing a readable word separator.

#### Acceptance Criteria

1. A change name SHALL allow filesystem-compatible NFC Unicode characters within its words.
2. Multiple name words SHALL be separated only by the ASCII hyphen-minus (`-`), not an en dash or em dash.
3. Change-name validation SHALL reject empty names, non-NFC forms, dot components, path separators, NUL, Windows-reserved device names, and components invalid for the target filesystem.
4. A timestamp-shaped user-supplied name SHALL remain valid when it otherwise meets the name rules.

### Requirement 3: Update the tracked repository state

**User Story:** As a maintainer, I want this repository's tracked active and archived changes to use the new layout and terminology.

#### Acceptance Criteria

1. Every tracked active change directory SHALL move from `.specle/specs/` to `.specle/changes/` and be renamed to its slug; every tracked archived change directory SHALL be renamed to its slug.
2. Every tracked change record SHALL receive `created_at`; `activated_at` shall be recorded where the tracked state establishes it, otherwise it shall be `null`.
3. All tracked internal references to change names SHALL be updated, including dependencies, relationships, current selection, review findings, delivery records, tracker links, summaries, and documentation.
4. The implementation SHALL fail rather than overwrite a tracked active or archived change when the new layout contains a slug collision.
5. Archived changes SHALL remain complete and discoverable in their renamed tracked locations.

### Requirement 4: Adopt change terminology and rename the creation skill

**User Story:** As a developer and agent user, I want “change” to identify the work item, leaving “spec” unambiguously available for `spec.md`.

#### Acceptance Criteria

1. Workflow guidance, durable-state descriptions, validation output, and command prompts SHALL refer to work items as changes rather than specs where they do not specifically mean `spec.md`.
2. The distributable `spec` skill SHALL be renamed to `define`, including its directory, frontmatter name, index entry, dependencies, lifecycle declarations, references, and installed mirror.
3. `define` SHALL retain the current creation behaviour: create an unselected normal change with requirements, `spec.md`, and initial status, without activating or planning it.
4. References to `spec.md` SHALL remain unchanged when they mean that file.
5. Retired `spec` skill names SHALL not be retained. User-supplied change names remain valid when they meet the current name rules, including names that happen to start with a timestamp.

### Requirement 5: Rename persisted change identifiers

**User Story:** As a developer, I want machine-readable state to use the same unambiguous change terminology as the workflow.

#### Acceptance Criteria

1. The `spec-status` JSON Schema resource, registry identifier, schema URL, and all tracked status records SHALL be renamed to `change-status`.
2. The status relationship field `spec` SHALL be renamed to `change` in the schema, runtime code, and every tracked record.
3. The spike findings field `outcome_spec` SHALL be renamed to `outcome_change` in the schema, runtime code, and every tracked record.
4. Structured review-finding references to another work item SHALL use `resulting_change`; retired `resulting_spec_name` and `resulting_spec_path` keys SHALL not remain.
5. The local selector SHALL be renamed from `.specle/current-spec` to `.specle/current-change`, including ignore rules, runtime state code, and all workflow references.
6. Internal Python names, validation diagnostics, generated index entries, and documentation SHALL use “change” for a work item. Product-name references to `Specle` and file-specific references to `spec.md` SHALL remain unchanged.

## Non-Functional Requirements

- This unreleased product SHALL not include compatibility aliases, a migration command, or handling for prior external installations.
- The tracked repository layout update must not overwrite an active or archived change.
- This change SHALL use direct `spec`-to-`change` identifier replacements first; reducing or removing `_change` suffixes is a separate design question and is out of scope.
- The implementation must preserve the distinction between active `.specle/changes/` changes and archived `.specle/archive/` changes.
- Existing queued changes remain independent; this migration does not create an ordering dependency among them.
- The change must update blueprint and active `.agents/` skills together, rebuild the generated index, and validate lifecycle and runtime state after migration.
- Collision checks during `define` and first-activation timestamp preservation during `activate` are agent-enforced workflow responsibilities; they are not a Python runtime validation subsystem.
- Explicit write-side callers may normalize supported timestamp input, but durable-record validation does not rewrite or reinterpret stored timestamps.
