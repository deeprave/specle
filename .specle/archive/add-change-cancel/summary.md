# Summary: Add change cancellation

## Summary

Specle can now record abandoned or superseded work as archived `cancelled` history, without mistaking it for delivered work.

## Outcome

Agents can cancel one explicitly named active change while preserving its history and presenting the user with any dependency, relationship, worktree, branch, or pull-request consequences that need a decision.

## What changed

- Added the `cancel` workflow and terminal lifecycle state.
- Added cancellation-aware lifecycle validation and status metadata support.
- Documented safe handling for one-sided concurrent relationships and committed parent-sidecar delivery sets.

## Key decisions and limits

Cancellation does not undo commits, branches, pull requests, merges, or published work. Lifecycle timestamps are normally recorded but remain optional metadata.
