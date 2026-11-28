# Design: Allow sidecar activation

## Overview

Make `activate` dispatch by the named record's kind and lifecycle state, and extend `build` to explicitly named bugfixes and refactors. The existing skills remain the source of each kind's abbreviated preparation and behavioural safeguards; build is the common task executor. Update lifecycle metadata, documentation, and reporting to match the resulting commands.

## Dispatch and selection

- Normal changes retain selection, estimate, size-dependent design, tasks, and build progression. Spikes retain selection and the spike workflow, including reactivation of an already selected defined spike.
- A named defined or planned bugfix/refactor stays unselected. Activation checks its abbreviated specification and task plan and invokes its owning skill in preparation mode when prerequisites need to be created or reconciled; when ready it invokes `build <name>`. It never changes the local selector, even when none exists.
- An existing selected parent does not automatically become the sidecar's delivery partner. Preserve the current requirement for an explicit reciprocal relationship before concurrent delivery or execution alongside that parent; otherwise report the existing separate-worktree route. Do not mutate relationships as a side effect of activation.
- Archived, missing, terminal, and ineligible records receive a clear diagnostic without selecting or building unrelated work. The installed lifecycle metadata recognises `change`, `bugfix`, `refactor`, and `spike`; `docs`, `release`, and unknown kinds have no activation route declared by current skills, so report unsupported rather than inventing one.

## Build ownership and lifecycle

`build <name>` resolves an explicitly named active abbreviated record without replacing selection, validates its kind, state, specification and task plan, and applies the owning kind's reproduction/regression or behavioural-invariant/baseline requirements. It updates only that record's tasks, progress, timestamps, and stale verification/review state, then hands off named verification. Keep the existing normal-change pre-build alignment confirmation and delivery boundaries.

Reconcile `bugfix`, `refactor`, and `prepare` so abbreviated contracts and preparation remain owned there while execution has a single `build` path; keep explicit existing commands usable as appropriate and avoid two competing task executors. Align activation/build lifecycle frontmatter, policy, `verify`, `review`, `changes`, and entrypoint guidance. Apply the same changes to packaged blueprints and installed copies.

## Next-action reporting

Update the existing package-owned resolver without assuming a future record or enum implementation. Defined/planned unselected bugfixes and refactors report `activate`; selected defined spikes may report the direct `spike` action, while `activate` remains supported. Building, verification, review, and delivery states must not route back to preparation. Where task completion is needed to distinguish build from verify, follow the existing build workflow's task interpretation and handle missing, empty, or unreadable plans conservatively; do not treat checked tasks as proof of verification. Preserve the action-name-only output contract.

## Verification direction

Exercise selected and unselected normal changes and spikes; explicitly named bugfix/refactor preparation and build with and without a selected parent; relationship handling; missing prerequisites; and unsupported kind/state diagnostics. Cover next-action output at the defined, planned, building, verification, and later lifecycle boundaries, including task-plan ambiguity. Confirm installed and packaged skill metadata remain consistent and the lifecycle graph validates. Run the project quality gates.
