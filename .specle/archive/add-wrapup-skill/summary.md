# Summary: Add wrapup skill

## Summary

Specle now separates archival finalisation from the final merge of its archival completion pull request, making completed work resumable without reopening its durable change record.

## Outcome

`complete` prepares and submits archival finalisation once. The new managed `wrapup` skill then owns only completion-PR merge, delivery-branch synchronisation, and clearing the matching local selection.

## What changed

- Added the managed `wrapup` skill and indexed it in the local inventory.
- Made delivery and lifecycle guidance distinguish approval, committed delivery, archival finalisation, and final wrapup.
- Added `updated_at` and `archived_at` handling to change records.
- Allowed external feedback on an open completion PR to be triaged through related bugfix or refactor sidecars without mutating the archived record.

## Key decisions and limits

An archived record remains immutable except for explicit completion-PR triage updating `review-findings.json`. Related corrective work is delivered to the existing completion branch before wrapup resumes.
