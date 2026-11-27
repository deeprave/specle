# Requirements: Add change cancellation

## Introduction

Specle can archive completed delivery, but it has no durable way to end work that is no longer wanted or has become superseded. Deleting an active change loses its intended scope and rationale; marking it complete would falsely claim delivery. A cancellation state and explicit workflow are needed to preserve that distinction.

## Glossary

- **Cancellation:** the intentional terminal end of one active change without asserting that its planned work was delivered.
- **Cancelled change:** an archived change whose lifecycle status is `cancelled`.
- **Named target:** the explicit stable change name supplied to `cancel`; it is never inferred from `.specle/current-change`.

## Requirements

### Requirement 1: Represent cancellation as a terminal lifecycle outcome

**User Story:** As a developer, I want cancelled work to remain visible as history without being mistaken for delivered work.

#### Acceptance Criteria

1. Specle SHALL recognise `cancelled` as a lifecycle status and terminal outcome alongside `complete`.
2. A cancelled record SHALL reside in `.specle/archive/<change-name>/` and retain its existing artifacts and durable history.
3. A cancelled record SHALL record a numeric Unix-second `cancelled_at` timestamp.
4. Cancellation SHALL NOT add completion evidence, fabricate delivery evidence, or imply that the planned work was implemented, verified, reviewed, merged, or published.
5. Lifecycle validation SHALL accept archived `complete` and `cancelled` records for every change kind that the `cancel` skill accepts, while continuing to reject any other archived lifecycle status.
6. Lifecycle validation SHALL reject a `cancelled` record outside `.specle/archive/` and an archived cancelled record without a numeric `cancelled_at` timestamp.

### Requirement 2: Provide an explicit cancellation workflow

**User Story:** As a developer, I want to end a specific change immediately without first selecting it or moving it through unrelated lifecycle stages.

#### Acceptance Criteria

1. Specle SHALL provide a `cancel` skill whose invocation requires an explicit stable change name.
2. `cancel` SHALL resolve only that named active change and SHALL never default to or infer its target from `.specle/current-change`; it MAY cancel the selected change only when that same stable name is explicitly supplied.
3. `cancel` SHALL accept the named active change from every non-terminal lifecycle status, including a state that already contains delivery evidence.
4. `cancel` SHALL reject a missing target, an archived target, and a target already in a terminal lifecycle state without changing durable records.
5. Cancellation SHALL be available without estimate, design, task completion, verification, review, commit, pull-request, merge, or delivery preconditions.

### Requirement 3: Reconcile explicit dependents with confirmation

**User Story:** As a developer, I want cancellation to remove a no-longer-valid prerequisite from affected change records without silently changing those records.

#### Acceptance Criteria

1. Before changing durable records, `cancel` SHALL re-read every active `status.json` and identify each record whose explicit `dependencies` array names the cancellation target.
2. When dependents exist, `cancel` SHALL report the target's dependent change names and recorded lifecycle statuses, then require explicit user confirmation before removing the target from those precise dependency arrays.
3. A negative response SHALL stop cancellation without changing any durable record. The user MAY instead provide a different explicit direction.
4. After confirmation, `cancel` SHALL re-read each affected record immediately before updating it, remove only the named dependency, and preserve its lifecycle status, timestamps, delivery evidence, relationships, and unrelated fields.
5. Cancellation SHALL archive the target and include the confirmed dependency-record updates in the same recoverable mutation.
6. Cancellation SHALL NOT infer sidecars or alter unrelated relationships. For each explicitly declared reciprocal concurrent-delivery partner, it SHALL report that partner and require explicit confirmation before removing only that reciprocal relationship from the surviving active record in the same recoverable mutation.

### Requirement 4: Lead user-owned in-flight cleanup

**User Story:** As a developer, I want cancellation to surface the concrete cleanup consequences of ending in-flight work and obtain my direction before leaving that work behind.

#### Acceptance Criteria

1. When the named change is also the current local selection, cancellation SHALL remove only that matching selector after archiving it; cancellation of a non-selected target SHALL preserve any unrelated selection.
2. Before changing durable lifecycle records for an in-flight target, `cancel` SHALL inspect and report the relevant local checkout facts: every staged, unstaged, and untracked worktree change; the current branch; commits on a recorded delivery branch that are not on its recorded target branch; and any recorded direct-delivery branch and commit.
3. `cancel` SHALL treat pre-existing worktree content as independent and unattributed unless the user explicitly identifies it as belonging to the cancellation target. It SHALL present that content separately from the cancellation mutation and SHALL not assume that current-change selection makes it related.
4. When the inspection reveals worktree changes, branch commits, direct-delivery evidence, or delivery evidence for a pull request, `cancel` SHALL explain the relevant consequence and request explicit user direction before recording cancellation. It SHALL not silently leave those facts for the user to discover later.
5. The requested direction MAY preserve the work, discard or stash local worktree content, retain or remove/rewrite a branch, close an open pull request, or use another user-specified action. The skill SHALL perform a destructive or external action only when that action is explicitly requested and authorised.
6. When existing delivery evidence identifies an open pull request, `cancel` SHALL report that it must not merge and request the user's instruction to close or otherwise handle it. It SHALL not close, merge, or update the pull request automatically.
7. When the identified pull request is already merged, `cancel` SHALL report that the delivered changes remain in the target branch and request the user's direction for any subsequent remediation; cancellation SHALL not attempt to undo, reset, or rewrite it automatically.
8. Cancellation SHALL NOT reset, stash, restore, switch, clean, stage, commit, push, revert, or otherwise alter worktree content, Git history, branches, or remote branches unless the user explicitly requests and authorises that separate action.
9. Existing artifacts, review history, commits, and delivery evidence SHALL be retained as historical facts unless the user explicitly directs an authorised cleanup action.
10. Cancellation SHALL isolate its own mutation to the named archived record, its matching selector, explicitly confirmed dependency removals, and an explicitly confirmed reciprocal concurrent-delivery unlink. It SHALL NOT create a pull request, infer a branch, or act on a tracker item or other external system.

### Requirement 5: Integrate cancellation with workflow guidance and validation

**User Story:** As an agent, I want lifecycle guidance and validation to distinguish cancelled work from both active and successfully completed work.

#### Acceptance Criteria

1. Portable lifecycle guidance and the generated skill inventory SHALL identify `cancelled` as terminal with no next action, including selector replacement and read-only archive inspection guidance.
2. `changes` SHALL exclude archived cancelled work from pending output, except where it is explicitly included as dependency context.
3. Skills that require an active or completed target SHALL reject cancelled records unless their purpose is read-only historical inspection.
4. Schema, lifecycle, and inventory tests SHALL cover cancellation status across supported kinds, archive location and timestamp validation, and rejection of invalid terminal records. The skill guidance SHALL be manually checked against explicit-name selection, confirmed dependency and reciprocal-relationship changes, direct delivery, and user-owned worktree and pull-request boundaries without adding recurring workflow-simulation tests.

## Boundaries

- Cancellation is not a delivery method and does not replace `complete`.
- It changes other active records only to remove the cancelled target after the user explicitly confirms each identified dependency consequence, or to unlink each explicitly declared reciprocal concurrent-delivery partner after separate confirmation.
- It does not require or invent a cancellation reason. A user may retain relevant rationale in the change artifacts when useful.
- It does not reopen, modify, or remove archived history.
