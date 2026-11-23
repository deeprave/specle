# Summary: Validate resolved review evidence

## Summary

Resolved review evidence is now accepted only when every recorded finding has a terminal decision or completed follow-up, preventing an approved change from advancing with unsettled review work.

## Outcome

Changes restored to `approved` after resolving review findings can proceed to delivery when their review record is genuinely settled. Missing, unreadable, or unresolved findings evidence blocks the transition.

## What changed

- Validated `review-findings.json` when an approved change records `review.status: "resolved"`.
- Added regression coverage for settled, missing, unreadable, and unsettled review evidence.
