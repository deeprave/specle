# Change: Cleanup complete

## Motivation

Specle currently needs an original delivery PR, a completion PR, and `wrapup` to finish one branch-delivered change. It also lacks reliable recovery for interrupted finalisation before archival.

## Intended outcome

Normal branch completion archive-finalises on the original open PR, records only immutable PR identity in `delivery.completion`, and requests authorised auto-merge. Direct delivery retains implementation-commit evidence and has no PR completion object. Resumed completion discovers its missing phase, while an already merged original PR creates a narrow `-complete` recovery PR.

## Scope

- Remove `wrapup` and normal archival completion PRs.
- Keep archived records immutable; post-archive defects are independent work.
- Remove `delivery.completion.commit` from the current schema and historical archives.
- Add a conservative archive-only PR CI fast lane while retaining full `main` CI.
- Update lifecycle and delivery policy, installed skills, blueprints, index, schema, workflow CI, documentation, and regression coverage together.

## Boundaries

- A normal original PR remains the single branch-delivery path.
- A `-complete` PR is recovery only after premature original-PR merge and transports the missed archive commit without adding completion evidence.
- Completion checks the current phase branch and stops on mismatch.
- No polling, hidden branch switching, fabricated PR evidence, or automatic branch deletion.

## Verification

Verify direct and branch guidance, phase-specific recovery and correction loops, removal of completion commit evidence from all status records, conservative PR-path classification, required-check continuity, full `main` coverage, schema/runtime validation, and project quality gates.
