# Fix approved review validation

## Bug

After every review finding is terminally declined, deferred, skipped, or duplicated, `resolve` correctly restores an active locally reviewed change to `status: "approved"` and records `review.status: "resolved"`. The runtime validator rejects that record because it accepts `approved` only when `review.status` is `"pass"`.

## Expected behaviour

An approved active change with a terminally resolved review must validate and remain ready for `commit`, just like a review that found no actionable items.

## Actual behaviour

`specle validate` emits `invalid review`, causing the pre-commit hook to reject the otherwise approved delivery.

## Reproduction

1. Review an active change and record a finding.
2. Triage every finding as a terminal no-action decision.
3. Run `resolve`.
4. Run `specle validate` or commit with the validation hook.

## Root cause and fix approach

The lifecycle policy and `resolve` distinguish an initially passing review from a resolved review, but runtime validation recognises only the former. Update the production validator to accept the documented resolved review outcome for `approved` work, with focused regression coverage.

## Regression evidence

A runtime-state test will construct an approved change with `review.status: "resolved"` and require validation to pass, while retaining rejection for unsupported review states.
