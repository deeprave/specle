# Design: restructure Specle spec state

## Overview

Replace the shared, tracked `.specle/context.json` and `.specle/current-issue.json` records with two deliberately different forms of state:

- Every spec directory owns a tracked, versioned `status.json` containing only durable facts about that spec.
- Each checkout uses an ignored, one-line `.specle/current-spec` file containing the selected spec's stable directory name.

Active and queued work remains in `.specle/specs/`; archived, durably completed work moves unchanged to `.specle/archive/`. A spec name is its directory name everywhere: no workflow record stores a repository-relative path, no shared queue exists, and no status record stores a derived next command.

This is a deliberately breaking migration of Specle's early runtime contract. It does not retain compatibility readers for the old context pair after migration.

## Architecture

```text
                         ignored, worktree-local
activate ─────────────► .specle/current-spec ──────► selected name
                                                          │
                                                          ▼
                 .specle/specs/<name>/status.json ◄── lifecycle skills
                 .specle/specs/<name>/*.md/json
                           │
                           │ completion finalisation
                           ▼
                .specle/archive/<name>/status.json
                .specle/archive/<name>/*.md/json

status / validate ─────► scan specs + archive status records
```

Create a small state module that is the only Python owner of state locations, loading, validation, discovery, and name resolution. It will provide:

- discovery of active and archived spec directories;
- validation and loading of a spec's `status.json`;
- lookup by stable name, rejecting duplicate names across active and archived locations;
- loading the optional selected name from `.specle/current-spec` and resolving it only to an active spec;
- derived progress reporting and next-skill calculation from the installed lifecycle declarations; and
- migration helpers which convert the existing context records exactly once.

`lifecycle.py` will consume this module instead of reading a context snapshot. It will validate every discovered status record, validate that a selected name exists in active specs, and apply lifecycle/evidence rules to each individual record. Runtime validation must accept a repository with no selection; a fresh clone intentionally has no current spec.

## Status contract

Add a packaged `spec-status/1.0` JSON Schema and registry identifier. Each active and archived spec receives this minimum shape:

```json
{
  "$schema": "https://github.com/deeprave/specle/schemas/spec-status/1.0",
  "kind": "change",
  "status": "planned",
  "progress": {"tasks_completed": 0, "tasks_total": 5},
  "verification": {"status": "not-run"},
  "review": {"status": "not-run", "findings": 0},
  "delivery": null,
  "relationships": [],
  "dependencies": []
}
```

The schema permits existing evidence fields inside `progress`, `verification`, `review`, and `delivery`, so the migration preserves useful historical detail without fabricating missing events. It requires no `name`, `path`, `next`, queue/history collection, current selection, or installed-skill inventory:

- the containing directory is the identity;
- location under `specs` or `archive` classifies active versus completed work;
- the lifecycle graph derives next actions from `kind`, `status`, and evidence;
- `dependencies` contains stable spec names only; and
- `relationships` is an array of typed relationship objects with stable spec-name targets, including sidecar/origin relationships.

The context and current-issue schemas, identifiers, exports, tests, and validation paths are removed. `context.json` is not replaced with a new durable schema. An agent may create an ignored cache for its own handoff needs, but it has no Specle-defined fields and no lifecycle authority.

## Lifecycle and skill changes

Update the lifecycle steering document, the root blueprint instructions, and every affected skill to use the same state rules:

- `spec`, `bugfix`, `refactor`, `prepare`, and `spike` create `status.json` in their new spec directory rather than appending shared queue records.
- `activate <name>` verifies that no unfinished selection exists in this worktree, resolves the named active normal spec, writes its name to `.specle/current-spec`, and then invokes the first missing estimate, design, or tasks stage. It never changes any other spec record.
- Planning and execution skills resolve an unnamed target via `current-spec`; explicitly named non-active work resolves directly by stable name. They update only that target's `status.json`.
- `status`, `analyse`, `summary`, `track`, `triage`, `resolve`, `review`, `commit`, and `verify` scan or resolve per-spec records as their selection rules require. Archived work is addressable only by explicit name.
- The existing `context` skill no longer reconciles durable project state. Reframe it as optional local handoff-cache generation, or remove it from the managed inventory if it has no useful non-authoritative role; neither outcome introduces a required cache contract.
- `next` is always derived from the lifecycle declarations and current evidence. It is never persisted in `status.json`.

The skill frontmatter and `LIFECYCLE.md` retain the lifecycle declaration as the cross-skill transition contract. The new state module validates the declared graph against durable per-spec evidence; it does not move policy into Python.

## Completion and archiving

`commit` records delivery evidence in the target status before delivery. For branch-and-pull-request delivery, a merged PR makes the target effectively complete even though archival has not yet been committed. This allows `activate` to select unrelated work without waiting for cleanup.

`complete` handles finalisation in this order:

1. Confirm the configured delivery final event from recorded evidence or authorised provider inspection.
2. Generate `summary.md` while the spec is still at its active location.
3. Move the whole directory to `.specle/archive/<name>` using a staged temporary move, preserving all artifacts.
4. Update the archived `status.json` with durable `complete` evidence.
5. Present the exact finalisation file list and obtain the user's delivery confirmation.
6. Commit and deliver it according to the selected delivery model, then clear the local selector if it selected that spec.

For direct-main delivery, the finalisation commit is made directly on main. For branch-and-pull-request delivery where the delivery PR has already merged, create `<delivery-branch>-completion` from the retained delivery head, commit and push the archive finalisation there, and open a PR to main. Then switch and synchronise local main so unrelated work can continue. This completion PR contains only the archived spec records; it does not absorb later main-branch work.

## Migration

The migration runs as part of this change, not as an ongoing compatibility layer:

1. Add tracked `.specle/.gitignore` with `/current-spec` and `/context.json`.
2. Create `status.json` in every existing spec directory from its matching current, queued, or recent legacy record. Preserve known progress, verification, review, delivery, dependencies, and relationships; use empty/null values only where the old state has no evidence.
3. Convert legacy path-based relationships to stable names.
4. Move legacy completed spec directories to `.specle/archive/`, including their artifacts such as generated summaries. Leave defined, active, and otherwise incomplete work under `.specle/specs/`.
5. Seed the ignored current selector for the presently active migration spec only in the local working tree.
6. Remove tracked `.specle/context.json` and `.specle/current-issue.json`, their schemas, and all old contract references.

Migration verification must prove that no legacy record is silently dropped and that no unobserved delivery outcome is invented.

## Error handling

| Condition | Handling |
| --- | --- |
| `current-spec` is absent | Treat as no selected work; require explicit activation for unnamed active-only commands. |
| `current-spec` has more than one non-empty line, invalid name, or points to archive/missing directory | Report a precise local-state error; do not alter durable records. |
| Duplicate spec name in active and archive | Fail validation and require manual resolution; never guess. |
| Missing or malformed `status.json` | Report the spec path and schema/lifecycle diagnostic; do not infer state from Markdown artifacts. |
| Attempt to activate while selected spec is unfinished | Preserve the local selection and stop. |
| Completion cannot confirm delivery event | Leave active status/directory untouched and state what evidence is missing. |
| Archive move or replacement fails | Retain or restore the source directory using staged temporary operations; never leave a partial archive as success. |

## Test strategy

- Unit-test state discovery, current-selector validation, stable-name resolution, duplicate handling, and absent-selection behaviour.
- Validate representative `status.json` fixtures for planned, verified, committed, completed, sidecar-related, and archived specs.
- Update CLI validation tests to validate per-spec records and the lifecycle graph without legacy runtime files.
- Test migration from the repository's representative legacy context records, asserting preservation of delivery/relationship evidence and archive placement.
- Test a worktree-style pair of directories with separate ignored selectors and no tracked-state conflict.
- Test effective completion and completion-branch planning without a required tracked write to an already merged delivery branch.
- Run the project quality gates: `pytest`, `ruff check`, `ruff format --check`, `ty check`, and `specle validate --verbose`.
