# Technical design: delivery policy and completion workflow

## Overview

Introduce a portable delivery-policy layer that separates local quality approval from external delivery. The distribution supplies generic delivery guidance; onboarding creates a project-selected policy; lifecycle and skills use that policy to move work through `approved`, `committed`, and `complete`.


## Architecture

```text
steering/delivery.md ───────────────┐
                                  onboarding ──> project/delivery.md
                                                    │
verified ──> review ──> approved ──> commit ──> committed
                                                 │       │
                                                 │       └─ named triage / resolve / verify / review / commit
                                                 v
                                             complete ──> complete
```

- `steering/delivery.md` defines three portable models: local-only Git, direct shared-upstream commits, and branch-and-pull-request review. It describes the meaning of `approved`, `committed`, and `complete`, while explicitly allowing a project to define another model.
- `project/delivery.md` records the selected model and only confirmed project conventions: delivery target branch, branch naming, commit format, required checks, secret scanning, pull-request formatting/templates, final event, and authority for agent external writes.
- `onboard` inventories `delivery.md` with the stable project documents and asks for each required delivery fact one at a time. Unknown preferences remain explicitly unestablished.
- Local `review` changes an implementation target from `verified` to `approved`; it never claims delivery completion.
- `commit` accepts only an approved target, scopes staging to its change, runs project-required delivery checks, and either gives instructions or performs only authorised commit, push, and pull-request actions. A branch-and-pull-request delivery becomes `committed`; local-only and direct-to-main delivery can become `complete` after their configured final event.
- `complete` handles only a committed branch-and-pull-request target. It supports confirming a merge performed elsewhere and, where policy and the user authorise it, performing the merge and local synchronisation.
- `commit` and `complete` record only the delivery evidence needed by this workflow in the selected target's existing `.specle/context.json` record. They do not depend on a separate delivery-record schema.
- Any abbreviated bugfix or refactor executed while active work exists records a relationship object with its origin path, a user-selected relationship type, and `with-related-spec` delivery mode. `bugfix`, `refactor`, and `implement` stop unlinked abbreviated work from entering the active worktree and direct it through `prepare` for later named execution in a separate worktree. `status` derives related-sidecar reporting from these records. `commit` includes only approved sidecars that explicitly declare this delivery mode and the selected origin; it records shared delivery evidence and transitions every member together.
- Resolve distinguishes no-action review outcomes by the target's delivery history: a locally reviewed target returns to `approved` and `commit`; a previously committed target returns to `committed` and `complete`. Neither path treats local review resolution as delivery completion.
- A named committed normal target is a non-active target throughout feedback work. Its scoped build, verification, review, approval, and recommit stages update only that target's record and never replace the active issue.
- An independent-spec hand-off is a routing event, not delivery evidence. Resolve creates the new normal work as a queued `defined` spec, then restores the origin to `approved` when it has only local review history or `committed` when it has a submitted delivery, preserving the active issue.

## Complete flow

For branch-and-pull-request delivery:

1. Read the named or selected `committed` target and the selected project policy.
2. Require the local checkout to be on the submitted branch. If it is on the delivery target branch or any other branch, stop before stashing, switching, merging, pulling, or otherwise changing the worktree; report both branch names.
3. Confirm external findings are settled and inspect merge readiness. If the pull request is already merged, use that evidence; otherwise require both project policy and explicit user authority before merging it.
4. Before an authorised merge-and-sync operation, detect tracked and untracked changes. Preserve them with a named recoverable stash, including untracked files. Do not discard ignored, untracked, staged, or unstaged work.
5. Merge the reviewable change when authorised, switch to the configured delivery target branch, and fast-forward from upstream. Do not use destructive reset or force operations.
6. Restore the stash after synchronisation. If restoration conflicts or fails, retain the stash, record a local-recovery note, and report concrete recovery steps without deleting work. The external merge remains evidenced delivery even when local restoration needs user attention.
7. Mark the selected target `complete` after the final delivery event. A non-active target never replaces the active current issue.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Missing or incomplete project delivery policy | Stop and direct the user to `onboard`. |
| Target not `approved` for `commit` or not `committed` for `complete` | Stop without Git or external actions. |
| Checkout differs from the delivery head branch | Stop before every worktree or external delivery action and report the mismatch. |
| External authority absent and PR is unmerged | Provide the next required human action; do not merge or mark complete. |
| PR already merged | Confirm delivery evidence; perform local synchronisation only when the checkout guard passes. |
| Stash creation fails | Stop before merge or branch operations. |
| Stash restoration conflicts | Preserve the stash, record recovery information, and report the conflict without deleting work. |
| New feedback on committed work | Move only that named target to `review-findings`; preserve the active issue. |
| All local-review findings are terminally no-action | Restore the target to `approved` with next `commit`; do not complete it. |
| Independent-spec hand-off | Create the separate normal spec as queued `defined` work after other findings are settled; restore the origin to `approved` or `committed` and do not complete it. |

## Test strategy

- Steering and onboarding tests cover all delivery models, stable project-document inventory, one-at-a-time delivery questions, and explicit unknown-policy recording.
- Lifecycle tests cover approval, no-action return by delivery history, queued independent-spec hand-off without premature completion, committed delivery, direct/local completion, named committed-normal re-entry from external feedback, and return through verification and approval.
- Commit tests cover target-state guards, scoped staging, required checks, authority gates, context-record delivery evidence, and model-specific transitions.
- Complete tests cover head-branch matching, no-action branch mismatch, clean and dirty worktrees, recoverable stash creation/restoration, stash-conflict preservation, already-merged confirmation, authorised merge-and-sync, and non-active target preservation.
- Run the project quality gates through `uv`: pytest, Ruff check, Ruff format check, and Ty.
- Root lifecycle and schema/reference tests cover only their stated source locations, generated-resource exception, and delivery workflow claims; the README remains concise and does not duplicate policy details.
