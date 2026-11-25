# Requirements: Cleanup complete

## Problem

Branch-and-pull-request delivery currently treats the delivery PR as ready to merge when `complete` begins, archives the record only after that merge, then opens a second archival completion PR that `wrapup` must later merge. This splits one delivery lifecycle across two commands and two pull requests, makes `complete` attempt final delivery too early, and leaves archival completion state that cannot itself be updated after merge.

Direct and branch delivery also diverge unnecessarily after local review. Both need an external-feedback loop where `triage`, `resolve`, revision or corrective work, verification, review, and `commit` can repeat until all delivery feedback is settled.

## Desired outcome

`complete` is the sole finalisation workflow for every delivery model. It archives completed work and submits that archival update through the same delivery path. Branch delivery retains one PR throughout the external-review loop and uses that same PR for the archival update and final merge. `delivery.completion` remains a valid immutable record of that archival finalisation; no separate `wrapup` skill or completion PR remains.

## User stories and acceptance criteria

### 1. Continue external review before final completion

As a developer with submitted work, I want branch delivery to remain in the normal triage-and-fix loop while its PR is open, so that feedback can be addressed without prematurely merging or archiving the change.

1. When a branch-delivery change is `committed` and its delivery PR is open, the workflow SHALL permit named `triage`, `resolve`, revision or corrective work, verification, review, and `commit` iterations against that same delivery PR.
2. `commit` SHALL update the existing recorded delivery PR after an accepted corrective iteration rather than creating a completion-specific PR.
3. `complete` SHALL require that every current external finding is resolved or has a terminal recorded disposition before it performs finalisation.

### 2. Finalise branch delivery in one PR

As a developer completing a reviewed branch delivery, I want archival finalisation to remain in the existing PR, so that final delivery has one review and merge path.

1. When invoked for a merge-ready branch-delivery change, `complete` SHALL verify recorded delivery evidence and eligible jointly delivered sidecars, then archive the delivery set and generate its summaries without creating a second PR.
2. `complete` SHALL reconcile fulfilled explicit dependencies, archive records, and a `delivery.completion` record identifying the archival-finalisation commit in the same branch-delivery PR before requesting final merge.
3. When repository policy permits, `complete` SHALL request auto-merge for the existing PR after pushing finalisation; otherwise it SHALL report the exact outstanding merge condition.
4. After that PR merges, `complete` SHALL preserve unrelated tracked work, switch to the delivery branch, fast-forward from upstream, restore preserved work, and clear its matching selector.

### 3. Use one completion model across delivery policies

As a developer, I want direct and branch delivery to share completion semantics, so that `complete` is predictable regardless of the configured policy.

1. Direct-main completion SHALL archive and synchronise its finalisation in the configured delivery branch without a second lifecycle command.
2. Branch-and-PR completion SHALL differ only by waiting for, or arranging, the final merge of its existing delivery PR.
3. The workflow SHALL remove the `wrapup` skill and references to archival completion PRs while preserving the `delivery.completion` schema contract for immutable finalisation evidence on the original delivery PR.

### 4. Handle the external wait explicitly

As a developer awaiting CI or auto-merge, I want completion to report an accurate resumable state, so that waiting for external systems does not create a second lifecycle stage.

1. When CI, required review, or merge eligibility is outstanding, `complete` SHALL report the external condition and retain the single delivery PR as the only pending delivery artifact.
2. A later `complete <change-name>` invocation SHALL recheck the recorded delivery PR and either report its remaining external condition or complete synchronisation after merge without requiring `wrapup`.

## Scope and boundaries

- Replace the current two-stage `complete` plus `wrapup` model across installed skills, blueprints, lifecycle policy, schema, inventory, documentation, and relevant tests.
- Preserve the existing explicit relationship and sidecar validation rules.
- Preserve the rule that active state records are re-read before a precise metadata update and that relationship-only updates do not change `updated_at`.
- Do not add a separate delivery-tracking store or infer relationships from branch names, worktree order, or shared files.
- Request auto-merge when the repository permits it. Do not add a polling service or notification mechanism in this change; a later explicit `complete` invocation rechecks the recorded PR when synchronisation is needed.
