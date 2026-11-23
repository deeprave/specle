# Fix approved review validation

## Bug

After every review finding is terminally declined, deferred, skipped, or duplicated, `resolve` correctly restores an active locally reviewed change to `status: "approved"` and records `review.status: "resolved"`. The runtime validator rejects that record because it accepts `approved` only when `review.status` is `"pass"`.

## Expected behaviour

An approved active change with `review.status: "resolved"` must validate and remain ready for `commit` only when its readable `review-findings.json` shows every finding has a terminal no-action decision or a completed dispatch. An unresolved, unreadable, or missing findings record must be rejected.

## Actual behaviour

`specle validate` rejects every resolved review because it accepts `approved` only with `review.status: "pass"`. A naïve repair that accepts the label alone would also allow an unresolved findings record through validation.

## Reproduction

1. Review an active change and record a finding.
2. Triage every finding as a terminal no-action decision.
3. Run `resolve`.
4. Run `specle validate` or commit with the validation hook.

## Root cause and fix approach

The lifecycle policy and `resolve` distinguish an initially passing review from a resolved review, but runtime validation recognises only the former. Update the production validator to load and validate the matching `review-findings.json` when it sees `review.status: "resolved"`, accepting only terminally settled findings with focused regression coverage.

## Regression evidence

Runtime-state tests will cover a terminally settled resolved review, unresolved findings, missing or unreadable findings records, and unsupported review states.
