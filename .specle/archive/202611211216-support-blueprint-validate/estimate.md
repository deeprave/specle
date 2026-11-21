# Estimate: support blueprint validate

## T-shirt size

L

## Breakdown

- New files: ~1–2, likely a dedicated comparison helper and focused test fixtures.
- Modified files: ~7–10 across CLI parsing and dispatch, installed-inventory validation, package resource discovery, tests, and both CI workflows.
- Estimated tasks: ~6 implementation and validation tasks.
- Key risks: defining generic managed-resource comparison without hard-coding the `specle` skill; producing actionable drift diagnostics while preserving unmarked client skills; keeping blueprint and installed-target modes mutually exclusive and read-only.

## Confidence

High. The existing validator, packaged distribution helpers, and generated-index model provide the needed foundation. The change extends their distinction rather than introducing a new runtime format.

## Recommendation

Design the two validation modes around a shared parsed package inventory, with explicit mode selection at the CLI boundary. Keep installed-target drift detection limited to package-owned skills and resources, and test it independently from blueprint lifecycle validation. Do not couple this work to any future schema or state-restructure change.

## Similar past work

- `add-specle-validate` established the installed-target validator, lifecycle graph, and verbose reporting.
- `address-security-findings` strengthened safe reads and installed-skill inventory validation.
