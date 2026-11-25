# Change: Cleanup complete

## Motivation

Specle's current branch-delivery finalisation splits one change across the original delivery PR, an archival completion PR, and a separate `wrapup` command. The second PR exists only because archiving occurs after the first PR merges. It makes final delivery harder to resume and creates immutable completion state that cannot reflect later external events.

## Intended outcome

Make `complete` the only finalisation workflow. A branch delivery remains in its original PR throughout external review and corrective iterations. Once ready, `complete` archives the delivery set and pushes that finalisation to the same PR, records immutable `delivery.completion` evidence for that archival commit, requests auto-merge where permitted, and later synchronises the delivery branch after its merge. Direct delivery follows the same conceptual lifecycle without a PR wait.

## Scope

- Remove `wrapup` and archival completion PRs while retaining `delivery.completion` as the completion record on the original delivery PR.
- Keep the submitted branch PR open for all external review, triage, resolution, corrective delivery, and final archival changes.
- Move archival finalisation before the final merge for branch delivery.
- Make the external CI/review/merge wait resumable through `complete`, not a separate lifecycle command.
- Update lifecycle policy, delivery policy, installed skills, blueprints, inventory, schema, documentation, and regression coverage together.

## Boundaries and assumptions

- A PR merge remains the final delivery event for the configured branch-and-PR policy.
- `complete` may report an outstanding external condition and resume later; it must not create a second PR merely to archive the same delivery.
- Existing historical archives retain their valid `delivery.completion` records; this change neither migrates nor removes them.

## Verification direction

Verification should cover direct and branch delivery guidance, removal of all managed `wrapup` inventory and archival-completion-PR references, preservation of the `delivery.completion` contract, a branch PR correction loop that remains on the original PR, finalisation pushed to that same PR, dependency cleanup, and resumed completion after an external merge.
