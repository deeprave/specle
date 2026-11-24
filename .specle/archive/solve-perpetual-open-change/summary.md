# Summary: Resolve perpetual completion state

## Summary

Specle no longer records a mutable completion-PR opening event in an immutable archive, so completed work does not remain perpetually listed for wrapup.

## Outcome

Completion records retain only immutable PR identity, while `wrapup` checks the PR's actual external state when explicitly invoked. Completion also clears directly declared fulfilled dependencies in the same archival-finalisation change.

## What changed

- Removed the nested completion event from the status schema and migrated the affected historical records.
- Made archived complete records terminal for changelist and status reporting.
- Clarified that `wrapup` is completion-PR handling, not a lifecycle transition.
- Assigned completion ownership for removing fulfilled explicit dependencies from active status records.

## Key decisions and limits

Completion events are deliberately invalid rather than temporarily tolerated. Dependency cleanup changes only declared status-record dependencies; it does not infer relationships or rewrite planning prose.
