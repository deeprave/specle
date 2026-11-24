# Bugfix: Solve perpetual open completion change

## Bug

Archived completed changes record `delivery.completion.event: "pull-request-open"` when their archival completion PR is created. The archive is immutable during `wrapup`, so the event remains `pull-request-open` after that PR merges.

## Expected behaviour

An archived completion record retains the immutable identity of its completion PR without storing an event whose state later changes. Completed archives do not reappear as pending `wrapup` work merely because their completion PR was once opened.

Once a delivered change's final event places it on the delivery branch, `complete` clears that fulfilled name from every active record that explicitly lists it as a dependency. For a jointly delivered parent and sidecars, it clears every member of that delivery set. The affected records are included in the same archival-finalisation commit, without changing their lifecycle status or `updated_at`.

When branch-and-PR delivery requires an archival completion PR, `wrapup` performs its external merge and synchronisation without creating a lifecycle transition out of terminal `complete`. Public lifecycle documentation must show that as explicit optional handling, not a normal flow edge.

## Actual behaviour

`changelist`, `status`, and lifecycle guidance interpret the retained `pull-request-open` event as evidence that archival delivery is still pending. Merged completion PRs for archived changes therefore remain listed as requiring wrapup.

Completed prerequisites also remain in active records' `dependencies` arrays after delivery, so changelist reports obsolete dependency context until someone manually corrects it.

## Reproduction

1. Complete a branch-and-pull-request delivery that requires an archival completion PR.
2. Merge the completion PR and run `wrapup`.
3. Run `changelist`.
4. Observe the archived record still reported for `wrapup` because its immutable completion event says `pull-request-open`.

## Root cause and fix approach

The completion delivery schema requires an event, and `complete` records a mutable opening event in an archive that `wrapup` must not change. Remove completion events from the schema and the historical archives, omit them when opening a completion PR, and remove guidance that treats a completion event as current open-state evidence. `wrapup` will use the completion PR reference to inspect its actual external state when explicitly invoked.

`complete` currently archives only the delivered change set. Extend that existing finalisation mutation, after final delivery is confirmed, to reread active records and remove only explicit dependency entries that match the delivered parent or its jointly archived sidecars. Stage those metadata-only updates in the same finalisation commit. Do not infer dependencies, change lifecycle status or `updated_at`, or delegate this work to `wrapup`.

The lifecycle flow and audit still draw `wrapup` as a conditional transition from `complete`, contradicting the terminal-state rule. Describe it as an explicit completion-PR operation instead.

## Regression evidence

Schema coverage will accept completion evidence without an event, reject the obsolete event field, and reject malformed required completion identity fields. Completion guidance will cover exact dependency removal after final delivery, including delivery sets with sidecars and preservation of unrelated dependency entries and lifecycle metadata. Lifecycle guidance validation will confirm installed and blueprint copies stay aligned.
