# Design: Allow sidecar activation

## Overview

Make `activate` dispatch by the named record's kind and lifecycle state, and extend `build` to explicitly named bugfixes and refactors. The existing skills remain the source of each kind's abbreviated preparation and behavioural safeguards; build is the common task executor. Update lifecycle metadata, documentation, and reporting to match the resulting commands.

## Dispatch and selection

- Normal changes retain selection, estimate, size-dependent design, tasks, and build progression. Spikes retain selection and the spike workflow, including reactivation of an already selected defined spike.
- A named defined or planned bugfix/refactor stays unselected. Activation checks its abbreviated specification and task plan and invokes its owning skill in preparation mode when prerequisites need to be created or reconciled; when ready it invokes `build <name>`. It never changes the local selector, even when none exists.
- Maintain a Git-ignored worktree-local registry of multiple active sidecar names, suggested as `.specle/current-sidecars`. Register on commencement, preserve the normal selection, expose active names in status and changes, report stale entries, and define lifecycle ownership and cleanup for completion, cancellation, local stop, and resumption. Durable state and explicit relationships remain authoritative; registry updates must be recoverable and isolated by worktree.
- When activation brings a normal change and a registered sidecar together, in either order, ask whether to link each eligible pair for joint delivery, with yes suggested as the default. Only the user's affirmative answer permits the reciprocal update. A decline leaves the pair unlinked and explains the independent route, including user-directed stashing or separate worktrees where needed; never stash automatically.
- The owning abbreviated workflow accepts an explicit user request to associate an existing named bugfix or refactor with the selected parent. Re-read both status records, validate kinds and existing relationships, and create the reciprocal pair as one recoverable update; preserve unrelated fields and refuse conflicts without a half-linked result. Do not infer consent from invoking activation.
- Define an internal preparation-only invocation contract for `bugfix` and `refactor`: complete missing prerequisite artifacts without executing tasks, return success or an actionable failure to the caller, and let `activate` continue to named build on success. Preserve the separate user-directed prepare-only flow.
- Archived, missing, terminal, and ineligible records receive a clear diagnostic without selecting or building unrelated work. The installed lifecycle metadata recognises `change`, `bugfix`, `refactor`, and `spike`; `docs`, `release`, and unknown kinds have no activation route declared by current skills, so report unsupported rather than inventing one.

## Build ownership and lifecycle

`build <name>` resolves an explicitly named active abbreviated record without replacing selection, validates its kind, state, specification and task plan, and applies the owning kind's reproduction/regression or behavioural-invariant/baseline requirements. It updates only that record's tasks, progress, timestamps, and stale verification/review state, then hands off named verification. Keep the existing normal-change pre-build alignment confirmation and delivery boundaries.

Reconcile `bugfix`, `refactor`, and `prepare` so abbreviated contracts and preparation remain owned there while execution has a single `build` path; keep explicit existing commands usable as appropriate and avoid two competing task executors. Align activation/build lifecycle frontmatter, policy, `verify`, `review`, `changes`, and entrypoint guidance. Apply the same changes to packaged blueprints and installed copies.

Update `docs/LIFECYCLE.md`, including its tables and diagrams, to describe the same actual lifecycle, including the S-sized design skip and the abbreviated activation-to-build handoff.

## Next-action reporting

Update the existing package-owned resolver without assuming a future record or enum implementation. Defined/planned unselected bugfixes and refactors report `activate`; selected defined spikes may report the direct `spike` action, while `activate` remains supported. Building, verification, review, and delivery states must not route back to preparation. Where task completion is needed to distinguish build from verify, follow the existing build workflow's task interpretation and handle missing, empty, or unreadable plans conservatively; do not treat checked tasks as proof of verification. Preserve the action-name-only output contract.

## Verification direction

Exercise selected and unselected normal changes and spikes; named sidecar preparation and build; multiple sidecars and separate worktrees; registration, stale entries, lifecycle cleanup, and interruption; both activation orders; affirmative, declined, and unavailable link prompts; recoverable relationship handling; missing prerequisites; and unsupported kind/state diagnostics. Cover next-action output at the defined, planned, building, verification, and later lifecycle boundaries, including task-plan ambiguity. Confirm installed and packaged skill metadata remain consistent and the lifecycle graph validates. Run the project quality gates.
