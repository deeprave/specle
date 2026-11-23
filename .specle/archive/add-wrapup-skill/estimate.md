# Estimate: Add wrapup skill

## T-shirt size

L

## Breakdown

- New files: ~1 managed skill and its installed copy.
- Modified files: ~20–30, covering completion and status-mutating skills, lifecycle and delivery policy, schema resources and registry, package inventory, and focused tests.
- Estimated tasks: 5–7 top-level tasks.
- Key risks: keeping final delivery, archival finalisation, and completion-PR merge ownership unambiguous; updating timestamps consistently without changing `updated_at` during archival; and preserving unrelated working-tree content across branch operations.

## Confidence

High

## Recommendation

Use a design to define the archived-record completion-PR evidence, `wrapup` preconditions and recovery paths, the timestamp contract, and a complete inventory of lifecycle owners before task planning.

## Similar past work

`rename-status-to-changelist` exposed the repeated-completion-PR problem directly. `restructure-spec-state` and `versioned-json-schemas` provide the existing state and schema-validation patterns this change must extend.
