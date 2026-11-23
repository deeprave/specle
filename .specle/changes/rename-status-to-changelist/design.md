# Design: Rename status to changelist

## Overview

Split the current overloaded name into two managed, read-only skills. `changelist` retains the existing pending-work inventory unchanged in purpose. The new `status` gives a concise view of the local checkout's selected change and Git worktree state.

## Architecture

```text
current status inventory skill
        |
rename managed directory and metadata to changelist
        |
update inventory-specific references and regenerate index

new status skill
        |
read current-change + selected status.json + lifecycle policy
        |
read Git worktree list + current branch + porcelain summary
        |
report concise current-work and worktree orientation
```

## Skill contracts

### `changelist`

- Retain the existing inventory table, pending-count, selection, sidecar, dependency-context, and audit guidance.
- Remain read-only and make no selector or lifecycle changes.
- Use the renamed skill name, description, usage text, and next-step references appropriate to an inventory.

### `status`

- Read `.specle/current-change` when present. If it selects a valid active change, read its `status.json`, derive the next action from lifecycle policy, and report its name, kind, lifecycle status, and next action.
- When verbose output is requested, read the selected change's `spec.md` and present a concise purpose, outcome, scope, and current progress summary rather than reproducing full artifacts.
- When no valid selection exists, say that no change is in progress and do not infer one from active directories.
- Use `git worktree list --porcelain` and the current directory to state whether this checkout is the primary worktree or a linked worktree. Report the current branch and a compact `git status --short` count by state, not file paths.
- Remain read-only; do not create a selector, activate a change, update a record, or modify Git state.

## Synchronisation

Rename the canonical and installed `status` inventory directories to `changelist`, then add matching canonical and installed `status` directories. Update cross-skill, lifecycle, and human-facing workflow references only where they refer to the old inventory role, and document the new focused `status` role concisely. Regenerate `.agents/skills/specle/index.json` from the installed inventory.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Selector is absent | Report that no change is in progress. |
| Selector names no active change or lacks `status.json` | Report the invalid local selection without changing it. |
| Lifecycle state is unrecognised | Report the recorded state and identify that no next action can be derived. |
| Git worktree or branch inspection fails | Report the unavailable Git detail while still reporting any available change state. |

## Test strategy

This is Markdown guidance, not production code. Review role separation, renamed references, exact canonical/installed copies, generated index entries, and read-only boundaries. Validate the managed inventories and run repository quality gates without adding tests for skill documents.
