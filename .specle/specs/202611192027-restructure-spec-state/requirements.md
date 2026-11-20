# Requirements: restructure spec state

## Introduction

Specle currently keeps substantial lifecycle, delivery, inventory, and historical state in a shared `context.json`, while `current-issue.json` duplicates the current selection. External completion events then mutate repository-tracked state after a pull request has merged, leaving routine completion with uncommitted files. This proposal redesigns persistence around self-contained spec records and worktree-local runtime state.

## Decided state model

- `.specle/current-spec` is an ignored, one-line local selector containing a stable spec name. It is created or updated by `activate`, is not synchronised between worktrees, and is absent in a fresh clone until a user explicitly activates a spec.
- `.specle/.gitignore` contains `/current-spec` and `/context.json`.
- `context.json` is retired as a durable contract. Agents may maintain an optional ignored handoff cache, but it has no required shape or lifecycle authority.
- Every spec owns a versioned `status.json`. The directory name supplies identity and its location supplies active-versus-archived classification, so durable status does not duplicate a name, path, queue, history, selected spec, or next workflow.
- Delivery merge evidence makes a branch-and-pull-request spec effectively complete. Durable completion generates `summary.md` and archives the spec with its completion evidence.
- Direct-main projects commit finalisation directly. Branch-and-pull-request projects create a `<merged-branch>-completion` branch and completion PR, then may continue unrelated work after synchronising local `main`.
- Specle distributes package-owned policy separately from user-owned steering. Package policy is installed in `.agents/policies/`; installation never updates or removes `.agents/steering/`.

## Glossary

- **Spec identity:** the timestamped spec-directory name, used as the stable identifier rather than a path.
- **Per-spec status:** the status record stored with one spec’s artifacts.
- **Runtime context:** local, worktree-specific operational state that is safe to regenerate.
- **Effective completion:** completion derived from recorded delivery references and observed final delivery evidence.

## Requirements

### Requirement 1: Make specs self-describing

**User Story:** As a developer, I want each spec to own its lifecycle and delivery record, so that updating one change does not rewrite a shared collection of unrelated state.

#### Acceptance Criteria

1. EACH active or archived spec SHALL contain a versioned `status.json` that identifies its kind, lifecycle, progress, verification, review, delivery evidence, dependencies, and relationships.
2. SPECLE SHALL identify specs by their directory name; workflow records SHALL NOT require repository-relative spec paths as identity.
3. THE redesign SHALL remove redundant `recent_specs` history from shared runtime context.
4. THE installed-skill catalogue SHALL remain the generated `skills/specle/index.json` resource and SHALL NOT be duplicated in runtime context.

### Requirement 2: Isolate worktree-local state

**User Story:** As a developer using multiple worktrees, I want each worktree’s current selection to remain local, so that branches do not conflict over machine-specific paths or unrelated active work.

#### Acceptance Criteria

1. THE redesign SHALL use exactly one authoritative current-spec selection per worktree: the ignored one-line `.specle/current-spec` file. It SHALL NOT duplicate that selection in tracked state.
2. WORKTREE paths and branch associations SHALL be treated as workstation-local runtime data and SHALL NOT be committed as portable project facts.
3. THE implementation SHALL use Git worktree information where applicable rather than inventing a competing tracked absolute-path registry.
4. A worktree’s local state SHALL not require edits to another worktree’s selected spec or status record.

### Requirement 3: Separate delivery evidence from post-merge churn

**User Story:** As a developer, I want a merged pull request to make work effectively complete without leaving an obligatory uncommitted source-tree mutation.

#### Acceptance Criteria

1. A branch-and-pull-request spec SHALL record its delivery reference before merge.
2. `complete` SHALL determine effective completion from final delivery evidence without requiring a tracked source-file rewrite on the already merged delivery branch.
3. THE workflow SHALL permit activation of unrelated normal work after effective completion, even while a branch-and-pull-request completion PR is pending.
4. Finalisation SHALL generate `summary.md`, archive the spec, and record durable completion evidence in one committed delivery according to the project's delivery model.

### Requirement 4: Archive completed specs

**User Story:** As a developer, I want completed specs outside the active spec inventory, while keeping them discoverable by stable name.

#### Acceptance Criteria

1. THE selected archival workflow SHALL move completed spec directories from `.specle/specs/` to `.specle/archive/` without changing their stable names.
2. STATUS and reporting workflows SHALL discover active specs and archived specs from their respective locations.
3. Cross-spec references SHALL use stable spec names rather than mutable directory paths.
4. THE archival operation SHALL preserve every spec artifact and delivery record.

### Requirement 5: Make state transitions resilient and unambiguous

**User Story:** As a developer, I want every workflow to use one clear local selector and durable state rules, so preparation, spikes, delivery, and recovery cannot silently create dead ends or select ambiguous work.

#### Acceptance Criteria

1. `activate` SHALL be the sole workflow writer of `.specle/current-spec`; it SHALL activate resumable normal specs and spikes only after checking the local selection guard.
2. Activation of a fully prepared normal spec SHALL set it to `planned` before invoking `build`; activation of a spike SHALL invoke its research workflow.
3. A spike SHALL retain `complete` durable status and an optional stable `outcome_spec` name when its findings are complete.
4. Ordinary stable-name resolution SHALL fail for a duplicate active/archive identity. A separate later reconcile workflow owns analysis and recovery.
5. Status reporting SHALL not treat an active-location `complete` record as pending work except when shown as explicit dependency context.
6. Every delivery model with confirmed final delivery evidence SHALL use the same authorised, recoverable archive finalisation process.

## Non-Functional Requirements

- The design must minimise Git merge conflicts across worktrees.
- Per-spec `status.json` is a durable versioned JSON contract; the retired optional handoff cache has no schema.
- Package policy is read before project-owned steering and project guidance; steering and project guidance may refine it.
- Migration must preserve existing active, queued, completed, and delivery evidence without fabricating external outcomes.
