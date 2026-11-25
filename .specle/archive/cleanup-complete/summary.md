# Summary: Simplify completion delivery

## Summary

Specle now completes normal branch delivery on the original pull request: it records the archival update there, requests auto-merge when permitted, and only uses a recovery PR when the original PR was already merged before archival delivery began.

## Outcome

Completion has one normal workflow for local, direct, and pull-request delivery. Archived records are immutable, and an already merged original PR has a narrow recovery route for transporting the missed archive update.

## What changed

- Removed the separate `wrapup` stage and normal completion PR route.
- Made direct-delivery evidence valid without PR-shaped completion fields.
- Made archive-only PR updates eligible for a fail-closed, reusable CI validation lane while retaining full validation for normal updates and every `main` push.
- Reconciled historic completion records to remove retired completion-commit fields.

## Key decisions and limits

The archive records only immutable PR identity, not a completion commit SHA. Feedback must be handled before archival finalisation; a later defect is independent work.
