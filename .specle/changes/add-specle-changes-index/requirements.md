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
3. Each displayed active change SHALL include its stable name, creation date in `YYYY-MM-DD` form when renderable, kind, status, declared dependencies, and next action. A diagnostic SHALL appear only for a record that has one.
4. The next-action column SHALL show only the action name, not a fully formed command or change argument.
5. The text report SHALL include a header row naming every displayed field.
6. Empty dependencies, a lifecycle status with no next action, and an unavailable date SHALL use clear, consistent placeholders.
7. Output ordering SHALL be deterministic.
8. Missing change collections SHALL produce a successful, clear empty result rather than an error.

### Requirement 2: List archived changes on request

**User Story:** As a developer, I want to inspect completed work separately, so active work remains focused while completed changes remain discoverable.

#### Acceptance Criteria

1. `specle changes --archive` SHALL list valid records in `.specle/archive/` and SHALL not include active changes.
2. Archive output SHALL use the same name, kind, status, dependencies, and next-action fields as the active listing. A diagnostic SHALL appear only for a record that has one.
3. Archive output SHALL display its applicable terminal date in `YYYY-MM-DD` form instead of creation date: `archived_at` for `complete`, or `cancelled_at` for `cancelled`. These timestamps are optional; an absent value SHALL use the standard empty placeholder.
4. Archive output SHALL remain read-only and deterministic.
5. Missing archive collections SHALL produce a successful, clear empty result rather than an error.

### Requirement 3: Reuse durable state and lifecycle context

**User Story:** As a developer, I want listing to use the same durable records and lifecycle interpretation as other CLI checks, so output is trustworthy and does not duplicate parsing rules.

#### Acceptance Criteria

1. The command SHALL reuse the established change-state reader and schema validation path for discovering records.
2. A discoverable record with malformed or schema-invalid state, or an unrenderable timestamp, SHALL remain represented in its collection with its stable directory name and an explicit diagnostic. It SHALL not be omitted or abort the rest of the listing. Lifecycle-invalid records remain inspectable by this listing command.
3. The mapping from a record and local selection context to its next action SHALL be defined once in package-owned lifecycle code and remain consistent with the documented lifecycle policy.
4. The command SHALL not select, activate, update, archive, repair, or otherwise mutate a change.
5. Archive output SHALL use the applicable optional terminal timestamp: `archived_at` for `complete`, or `cancelled_at` for `cancelled`. A missing optional timestamp is represented as an empty placeholder or `null`; a non-finite or unrenderable numeric timestamp is represented by an actionable diagnostic on that record.

### Requirement 4: Provide machine-readable change output

**User Story:** As a tool or agent, I want structured change output, so I can consume the same durable state without parsing the human table.

#### Acceptance Criteria

1. `specle changes --json` SHALL emit JSON instead of the human-readable table.
2. The JSON result SHALL identify the selected collection (`active` or `archive`) and contain a deterministically ordered `changes` array.
3. Each array item SHALL include the change name, kind, status, dependencies, relevant durable timestamp or `null`, and next action. It SHALL include a diagnostic only when that record has one.
4. `specle changes --archive --json` SHALL use the archived collection and its applicable optional terminal timestamp under the same validation rules as text output.
5. JSON output SHALL remain read-only, represent schema and timestamp errors on the relevant records, and SHALL not emit non-standard non-finite JSON numbers.
6. `specle changes --json --pretty` SHALL pretty-print JSON with an indentation width of two spaces.

### Requirement 5: Provide CSV change output

**User Story:** As a tool or developer, I want explicit CSV output, so I can import the same report without relying on the human table's tab separators.

#### Acceptance Criteria

1. `specle changes --csv` SHALL emit RFC 4180-compatible CSV instead of the human-readable table.
2. CSV output SHALL include a header row and the same rows and logical fields as text output, using its formatted `YYYY-MM-DD` date when available. It SHALL include a diagnostic column only when at least one emitted row has a diagnostic.
3. `specle changes --archive --csv` SHALL select only archive rows and use its applicable optional terminal timestamp to produce its date or empty placeholder.
4. CSV output SHALL remain deterministic and read-only, use portable line endings, and represent the same per-record diagnostics as text and JSON output.
5. `--csv` and `--json` SHALL be mutually exclusive; `--pretty` SHALL remain available only with `--json`.

### Requirement 6: Rebuild an installed-skill index without installation

**User Story:** As a developer, I want to regenerate a deployment's skill index without replacing its skills or policies, so the generated resource can be brought back into sync after managed metadata changes.

#### Acceptance Criteria

1. `specle index <target-directory>` SHALL require an explicit target directory and SHALL not assume the current directory.
2. The command SHALL scan managed skills installed under the target's `.agents/skills/` using the same metadata parsing and grouping rules as installation.
3. The command SHALL generate `.agents/skills/specle/index.json` from the installed managed inventory, including each skill's group, name, description, and usage.
4. The command SHALL replace only the generated index resource, using a temporary sibling followed by replacement; it SHALL not install, update, remove, or rewrite managed skills or policies.
5. The target SHALL contain a valid managed `specle` skill. A missing, unmanaged, or invalid `specle` skill SHALL produce an actionable non-zero diagnostic and SHALL leave the existing index unchanged. Other discovered managed skills are the installed inventory; the command SHALL not infer a separate expected-skill baseline.
6. The command SHALL report the target and generated index location on success.
7. The replacement index SHALL be UTF-8 encoded, retain normal readable permissions, and reject a directory at the index destination with an actionable diagnostic.

## Non-Functional Requirements

- The command is a concise console report and must follow the repository's minimal-output policy.
- `specle index` is a narrowly scoped generated-resource operation; it does not replace `init` or the future update workflow.
- Date presentation is human-facing only; durable values remain Unix-second numbers.
- The command does not replace the agent `status` skill, which may provide broader workflow interpretation and context.
- The durable `created_at`, `archived_at`, and `cancelled_at` fields already available on `main` supply the timestamps that `changes` reads. This change introduces no compatibility aliases or alternate legacy state formats.
