# Tasks: delivery policy and completion workflow

## Dependency

`202611172043-versioned-json-schemas` must define the versioned delivery-record contract before this change creates or consumes delivery records. Do not introduce a temporary JSON shape.

- [x] 1. Add portable `delivery.md` steering that defines the supported delivery models, model-specific lifecycle meanings, and project-customisation boundary; install it in the active steering inventory.
- [x] 2. Extend `onboard` and the project guidance inventory for `project/delivery.md`, collecting the delivery model and delivery conventions one question at a time while preserving unknown policy explicitly.
- [x] 3. Update lifecycle, context, review, triage, and resolve guidance so local review produces `approved`, branch-and-PR delivery records `committed`, and explicitly named submitted normal changes re-enter review work without replacing the active issue.
- [x] 4. Add the `commit` skill to enforce approved-target, scoped-staging, required-check, authority, and model-specific delivery rules using the versioned delivery record.
- [x] 5. Add the `complete` skill for committed branch-and-PR delivery, including head-branch guard, authorised merge, safe target-branch synchronisation, recoverable stash handling, and already-merged confirmation.
- [x] 6. Extend behavioural coverage for no-action outcomes by delivery history, independent-spec hand-off without premature completion, named committed-normal re-entry, authority guards, branch mismatch, stash recovery, and delivery-record constraints.
- [x] 7. Synchronise the root lifecycle reference and schema documentation with the delivered workflow, correcting only stale README references or paths without duplicating policy detail.
- [x] 8. Update Resolve, `spec`, and the root lifecycle diagrams so no-action and independent-spec routes restore `approved` or `committed` according to delivery history and queue independent normal work.
