# Requirements: add specle changes and index

## Introduction

Specle has durable change records but no concise CLI view of work that remains incomplete or of completed, archived work. Users must currently inspect directories and JSON manually to see a change's type, lifecycle state, dependencies, and next workflow action. The generated installed-skill index is also available only as an incidental outcome of installation, rather than through an index-only command.

## Glossary

- **Active change:** a valid record under `.specle/changes/`.
- **Archived change:** a valid record under `.specle/archive/`.
- **Incomplete change:** an active change whose status is not `complete`.
- **Lifecycle transition:** a change of the top-level `status` value in a change's `status.json`.
- **Next action:** the owning workflow action for a lifecycle status, displayed as an action name only, without arguments or a complete command line.
- **Installed-skill index:** the generated `.agents/skills/specle/index.json` resource describing managed installed skills by group, name, description, and usage.

## Requirements

### Requirement 1: List incomplete active changes by default

**User Story:** As a developer, I want a concise list of incomplete work, so I can see what remains to be done without reading every change directory.

#### Acceptance Criteria

1. `specle changes` SHALL read the durable change records in the current project's `.specle/changes/` directory without modifying them.
2. The default output SHALL include every valid incomplete active change and SHALL exclude records with `status: "complete"`.
3. Each displayed active change SHALL include its stable name, creation date in `YYYY-MM-DD` form, kind, status, declared dependencies, and next action.
4. The next-action column SHALL show only the action name, not a fully formed command or change argument.
5. Empty dependencies and a lifecycle status with no next action SHALL use a clear, consistent placeholder.
6. Output ordering SHALL be deterministic.
7. Missing change collections SHALL produce a successful, clear empty result rather than an error.

### Requirement 2: List archived changes on request

**User Story:** As a developer, I want to inspect completed work separately, so active work remains focused while completed changes remain discoverable.

#### Acceptance Criteria

1. `specle changes --archive` SHALL list valid records in `.specle/archive/` and SHALL not include active changes.
2. Archive output SHALL use the same name, kind, status, dependencies, and next-action fields as the active listing.
3. Archive output SHALL display completion date in `YYYY-MM-DD` form instead of creation date.
4. Archive output SHALL remain read-only and deterministic.
5. Missing archive collections SHALL produce a successful, clear empty result rather than an error.

### Requirement 3: Reuse validated lifecycle state

**User Story:** As a developer, I want listing to use the same durable records and lifecycle interpretation as other CLI checks, so output is trustworthy and does not duplicate parsing rules.

#### Acceptance Criteria

1. The command SHALL reuse the established change-state reader and schema validation path for discovering records.
2. Invalid records or lifecycle diagnostics SHALL be reported clearly and SHALL cause a non-zero exit rather than appearing as normal list entries.
3. The mapping from status to next action SHALL be defined once in package-owned code or metadata and remain consistent with the documented lifecycle policy.
4. The command SHALL not select, activate, update, archive, repair, or otherwise mutate a change.
5. Archive output SHALL use `archived_at` as its sole completion-date source and report an actionable validation diagnostic when that durable value is missing or invalid.

### Requirement 4: Rebuild an installed-skill index without installation

**User Story:** As a developer, I want to regenerate a deployment's skill index without replacing its skills or policies, so the generated resource can be brought back into sync after managed metadata changes.

#### Acceptance Criteria

1. `specle index <target-directory>` SHALL require an explicit target directory and SHALL not assume the current directory.
2. The command SHALL scan managed skills installed under the target's `.agents/skills/` using the same metadata parsing and grouping rules as installation.
3. The command SHALL generate `.agents/skills/specle/index.json` from the installed managed inventory, including each skill's group, name, description, and usage.
4. The command SHALL replace only the generated index resource, using a temporary sibling followed by replacement; it SHALL not install, update, remove, or rewrite managed skills or policies.
5. Missing, malformed, or invalid installed managed skills SHALL produce an actionable non-zero diagnostic and SHALL leave the existing index unchanged.
6. The command SHALL report the target and generated index location on success.

## Non-Functional Requirements

- The command is a concise console report and must follow the repository's minimal-output policy.
- `specle index` is a narrowly scoped generated-resource operation; it does not replace `init` or the future update workflow.
- Date presentation is human-facing only; durable values remain Unix-second numbers.
- The command does not replace the agent `status` skill, which may provide broader workflow interpretation and context.
- The durable `updated_at` and `archived_at` fields already available on `main` supply the timestamps that `changes` reads. This change introduces no compatibility aliases or alternate legacy state formats.
