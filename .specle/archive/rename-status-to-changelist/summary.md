# Summary: Status and changelist workflow

## Summary

Specle now separates the current-work `status` report from the pending-work `changelist`, so developers can quickly orient themselves without losing the fuller change inventory.

## Outcome

`status` reports the selected change, its lifecycle next action, and a compact local worktree summary. `changelist` remains the read-only inventory for pending, dependency-context, and related change work.

## What changed

- Renamed the previous inventory skill to `changelist`.
- Added focused `status` guidance for selected work, worktrees, branches, and compact uncommitted-change summaries.
- Clarified lifecycle documentation, safer verbose summaries, estimate-aware next actions, and handling of unrecognised states and untracked work.
