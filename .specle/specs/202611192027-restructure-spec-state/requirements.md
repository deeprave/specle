# Requirements: restructure spec state

## Introduction

Specle currently keeps substantial lifecycle, delivery, inventory, and historical state in a shared `context.json`, while `current-issue.json` duplicates the current selection. External completion events then mutate repository-tracked state after a pull request has merged, leaving routine completion with uncommitted files. This proposal redesigns persistence around self-contained spec records and worktree-local runtime state.

## Open questions — resolve before activation

1. **Single local selection record:** should `current-issue.json` be folded into a local-only context record, or should one file replace the other under a new name?
2. **Worktree discovery and storage:** can Git’s local worktree metadata provide the canonical worktree list, with Specle storing only local spec-selection associations outside tracked content?
3. **Effective completion:** should `complete` derive completion from recorded delivery references and observed provider/Git evidence without mutating tracked spec state?
4. **Archival timing:** should physical moves to `.specle/archive/` occur through an explicit maintenance PR, or through authorised post-merge automation?
5. **Policy access:** which resolved policy values, if any, belong in a regenerated runtime report without becoming a second authoritative policy source?

## Glossary

- **Spec identity:** the timestamped spec-directory name, used as the stable identifier rather than a path.
- **Per-spec status:** the status record stored with one spec’s artifacts.
- **Runtime context:** local, worktree-specific operational state that is safe to regenerate.
- **Effective completion:** completion derived from recorded delivery references and observed final delivery evidence.

## Requirements

### Requirement 1: Make specs self-describing

**User Story:** As a developer, I want each spec to own its lifecycle and delivery record, so that updating one change does not rewrite a shared collection of unrelated state.

#### Acceptance Criteria

1. EACH active or archived spec SHALL contain a machine-readable status record that identifies its kind, lifecycle, progress, verification, review, and delivery evidence.
2. SPECLE SHALL identify specs by their directory name; workflow records SHALL NOT require repository-relative spec paths as identity.
3. THE redesign SHALL remove redundant `recent_specs` history from shared runtime context.
4. THE installed-skill catalogue SHALL remain the generated `skills/specle/index.json` resource and SHALL NOT be duplicated in runtime context.

### Requirement 2: Isolate worktree-local state

**User Story:** As a developer using multiple worktrees, I want each worktree’s current selection to remain local, so that branches do not conflict over machine-specific paths or unrelated active work.

#### Acceptance Criteria

1. THE redesign SHALL use exactly one authoritative current-spec selection per worktree; it SHALL NOT duplicate that selection in two runtime files.
2. WORKTREE paths and branch associations SHALL be treated as workstation-local runtime data and SHALL NOT be committed as portable project facts.
3. THE implementation SHALL use Git worktree information where applicable rather than inventing a competing tracked absolute-path registry.
4. A worktree’s local state SHALL not require edits to another worktree’s selected spec or status record.

### Requirement 3: Separate delivery evidence from post-merge churn

**User Story:** As a developer, I want a merged pull request to make work effectively complete without leaving an obligatory uncommitted source-tree mutation.

#### Acceptance Criteria

1. A branch-and-pull-request spec SHALL record its delivery reference before merge.
2. `complete` SHALL determine effective completion from final delivery evidence without requiring a tracked source-file rewrite after merge.
3. THE workflow SHALL continue to block activation of unrelated normal work while the current delivery is not effectively complete.
4. THE selected archival policy SHALL avoid routine uncommitted source-tree changes after merge.

### Requirement 4: Archive completed specs

**User Story:** As a developer, I want completed specs outside the active spec inventory, while keeping them discoverable by stable name.

#### Acceptance Criteria

1. THE selected archival workflow SHALL move completed spec directories from `.specle/specs/` to `.specle/archive/` without changing their stable names.
2. STATUS and reporting workflows SHALL discover active specs and archived specs from their respective locations.
3. Cross-spec references SHALL use stable spec names rather than mutable directory paths.
4. THE archival operation SHALL preserve every spec artifact and delivery record.

## Non-Functional Requirements

- The design must minimise Git merge conflicts across worktrees.
- It must remain independent of the queued JSON-schema-versioning change; do not introduce versioning requirements by assumption.
- Project steering and project guidance remain authoritative for policy unless an explicit later decision changes that model.
- Migration must preserve existing active, queued, completed, and delivery evidence without fabricating external outcomes.
