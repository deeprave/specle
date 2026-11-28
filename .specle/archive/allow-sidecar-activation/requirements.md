# Requirements: Allow sidecar activation

## Why

`activate <name>` is the entry point for starting normal changes and spikes, but it rejects bugfixes and refactors. Prepared abbreviated work instead requires a different, kind-specific command, and `build` is currently limited to normal changes. This splits a common lifecycle operation across workflows even though the target's kind and state identify the appropriate preparation and execution path.

Make activation a kind-aware entry point for supported change types, make named build execution available for prepared bugfixes and refactors, and track active sidecars in a worktree-local registry. Define their full lifecycle and align lifecycle policy, skill instructions and metadata, and next-action reporting.

## Scope and boundaries

- Preserve the existing selection and preparation behaviour for normal changes and spikes. Activation of a selected, defined spike remains a supported way to start it; reporting `activate` for that state is valid.
- Bugfixes and refactors remain explicitly named, non-selected work. Activating them must not change `.specle/current-change`, including when no change is selected.
- When a normal change and an active sidecar come together in the same worktree, automatically link them for joint delivery in either activation order. Completion determines whether the relationship remains: together-completed work remains linked in its history; separately completed work is unlinked from the surviving active sibling.
- Track multiple explicitly active bugfixes and refactors in a Git-ignored worktree-local registry, suggested as `.specle/current-sidecars`. Durable status and reciprocal relationships remain authoritative; registry membership does not change the normal selection or by itself assert delivery.
- Do not infer current-worktree sidecar activity from queued records, durable status alone, or activity in another worktree.
- Keep kind-specific bugfix reproduction and regression coverage, refactor behavioural invariants and baseline, and the existing delivery and verification boundaries. Do not duplicate independent execution flows.
- Other supported kinds must have an explicit, appropriate route or a clear unsupported diagnostic; do not silently treat them as normal changes or invent workflow ownership. Determine their actual supported activation behaviour from the lifecycle policy and existing skills during design.
- This work is independent of `refactor-change-record`, `consolidate-state-enums`, and the current changes-listing delivery. It must work with the implementation available when undertaken and must not assume those queued changes have been delivered.

## Requirements

### 1. Activate according to kind and lifecycle state

**User story:** As a developer, I want one named activation command to begin eligible work so that I need not remember a different starting command for each kind.

1. WHEN `activate <name>` names an eligible active change, THE workflow SHALL inspect its kind and lifecycle state and dispatch the appropriate preparation or owning workflow.
2. WHEN a normal change is activated, THE workflow SHALL retain its selection and required estimate, size-dependent design, tasks, and build progression.
3. WHEN a defined or spiking spike is activated, THE workflow SHALL select or retain it and invoke the spike workflow. Activating an already selected defined spike SHALL be supported.
4. WHEN a defined or planned bugfix or refactor is activated, THE workflow SHALL leave the existing selection unchanged, complete any missing kind-specific prerequisites, and invoke `build <name>` when ready.
5. WHEN the target is archived, missing, in an ineligible lifecycle state, or has a kind without a supported activation route, THE workflow SHALL report the condition without selecting or implementing unrelated work.
6. WHEN a sidecar is commenced while a normal change is active, or a normal change is commenced while a sidecar is active in the same worktree, THE workflow SHALL automatically establish their matching reciprocal relationship as a recoverable operation, without a link prompt.
7. THE workflow SHALL preserve unrelated work and SHALL NOT audit which code the user includes in a delivery, or automatically stash, move, or discard work. Users may deliver concurrent work separately.
8. WHEN concurrent work is delivered and completed together, THE completed records SHALL retain their mutual relationship. WHEN only one linked item is completed, THE completion workflow SHALL remove the matching link from the surviving active sibling without rewriting immutable archived records.

### 2. Build named abbreviated work

**User story:** As a developer, I want `build <name>` to execute prepared bugfixes and refactors so execution has one consistent entry point while retaining each kind's safeguards.

1. WHEN a named bugfix or refactor has its required specification and task plan and is eligible to build, THE build workflow SHALL execute that target without changing `.specle/current-change`.
2. THE build workflow SHALL apply bugfix-specific reproduction and regression requirements or refactor-specific behavioural invariants and baseline requirements as applicable, and update the named target's task progress and lifecycle state.
3. WHEN required preparation is missing or inconsistent, THE workflow SHALL identify and complete the applicable prerequisites through their owning workflow before building, or report why the target cannot proceed; it SHALL NOT treat missing work as completed.
4. THE change SHALL reconcile the roles of `prepare`, `bugfix`, `refactor`, `activate`, `build`, `verify`, and review so their instructions and lifecycle metadata consistently describe preparation, execution, and continuation without duplicating competing implementations.
5. Existing normal-change build confirmation and other established authorisation and delivery boundaries SHALL remain effective.
6. WHEN activation invokes a kind-specific workflow to prepare missing prerequisites, THE preparation-only handoff SHALL be explicit, SHALL NOT execute tasks, and SHALL return control to activation to continue to named build when preparation succeeds.

### 3. Keep next actions and lifecycle guidance consistent

**User story:** As a developer, I want reported next actions to match commands that actually work for a change's kind and state.

1. THE lifecycle policy, packaged skill instructions and metadata, installed skill copies, and relevant entrypoint documentation SHALL agree on activation, selection, preparation, and build ownership.
2. THE next-action resolver and change-listing output SHALL reflect the applicable kind, status, selection, and preparation state, including activation of unselected prepared bugfixes and refactors and the supported selected defined spike activation.
3. WHEN an abbreviated change is already being built or has progressed to verification, review, or delivery, THE next action SHALL reflect its actual lifecycle stage rather than restarting preparation.
4. THE reporting contract SHALL retain action names without embedding arguments where the existing output format specifies action names.
5. THE public lifecycle reference SHALL describe the implemented lifecycle, including abbreviated activation and named build and the S-sized design skip.

### 4. Register and manage the sidecar lifecycle

**User story:** As a developer, I want to inspect active sidecars in this worktree and understand when their local activity begins and ends.

1. THE system SHALL maintain a worktree-local, Git-ignored registry of zero or more actively commenced bugfix and refactor names, registering each only once without replacing the normal selection.
2. Status and changes workflows SHALL expose registered active sidecars and distinguish local activity from recorded joint-delivery relationships.
3. WHEN a registry entry is missing, invalid, archived, terminal, or otherwise stale, THE inspecting workflow SHALL report it without silently linking it or treating it as valid active work.
4. THE lifecycle policy and applicable skills SHALL define sidecar creation, activation, preparation, build, verification, review, delivery, completion, cancellation, and local stop or resumption, including registry ownership and cleanup. Local inactivity SHALL NOT be conflated with durable completion.
5. Registry and lifecycle updates SHALL handle failures and interruption recoverably, preserve unrelated work and worktree isolation, and SHALL distinguish registry membership from the automatic activation links and completion unlinks.
6. A consistently linked pair SHALL NOT acquire duplicate relationships; conflicts or incomplete pairs SHALL be reported without silently overwriting them.
7. THE `specle changes` CLI SHALL expose registered local sidecars and stale registry entries in its existing supported output modes, distinguishing local activity from durable delivery relationships.
8. THE `complete` event SHALL remove only sidecars that have actually reached completion from the local registry, independent of archive location or delivery path. The removal SHALL be idempotent and retryable on normal, direct, and recovery completion paths.
9. New project initialisation SHALL add `/current-sidecars` to the runtime ignore rules while preserving existing ignore-file contents.

## Verification direction

Exercise activation and next-action decisions for normal changes, spikes, bugfixes, and refactors across eligible states, including multiple sidecars, both activation orders, separate worktrees, automatic links, together and separate completion, stale registry entries, and CLI output. Verify completion-triggered cleanup and retry, initialisation ignore rules, recovery after interruption, selection preservation, and unchanged unrelated work. Run the project's documented quality gates.
