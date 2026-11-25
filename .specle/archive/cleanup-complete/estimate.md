# Estimate: Cleanup complete

## T-shirt size

L

## Breakdown

- New files: ~0; this is a replacement of existing workflow contracts and tests.
- Modified or removed files: ~30 across installed skills, source blueprints, lifecycle and delivery policy, documentation, inventory, schema, and lifecycle/schema tests.
- Estimated tasks: ~8–10 independently verifiable slices.
- Key risks: preserving the explicit sidecar and dependency-cleanup invariants while changing finalisation order; making a still-open branch PR resumable without creating a second delivery artefact; keeping installed and blueprint inventories identical; and deciding the one-time treatment of archived `delivery.completion` records.

## Confidence

Medium. The affected surfaces and present failure mode are clear from the just-completed two-PR delivery, but the exact external auto-merge observation and the historical-record migration policy need design decisions.

## Recommendation

Design the complete state machine before changing skill text. Keep all delivery state in the existing versioned records and use the existing PR identity; do not introduce a separate delivery store. Define explicit tests around the branch-PR correction loop, archive-before-final-merge ordering, dependency reconciliation, resumed completion after merge, and the absence of `wrapup` and `delivery.completion` from managed contracts.

## Similar past work

- `add-wrapup-skill` introduced the two-stage completion model now being removed.
- `solve-perpetual-open-change` removed the mutable completion event but retained immutable completion-PR identity.
- `rename-changelist-to-changes` just demonstrated the present two-PR sequence end to end.
