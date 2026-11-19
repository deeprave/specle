# Estimate: add `specle validate`

## T-shirt size

XL

## Breakdown

- New files: approximately 2–4 for validation and graph-building modules, plus focused tests.
- Modified files: approximately 25–35: CLI wiring, inventory metadata schema/parser, lifecycle-owning source skills and active copies, generated index, and test suites.
- Estimated tasks: 8–10 implementation slices.
- Key risks: expressing conditional normal, abbreviated, spike, review, and delivery flows precisely enough for deterministic graph analysis; keeping skill declarations and body instructions aligned; and validating current runtime state without imposing future JSON-schema versioning or compatibility assumptions.

## Confidence

Medium. The StrictYAML parser and inventory model now provide a clear foundation, but this is the first formalisation of the lifecycle contract used by production skills.

## Recommendation

Use a full design before planning. Separate the declarative transition model, graph validation, installed-inventory validation, runtime-record validation, CLI boundary, and skill migration into independently testable slices. Keep the queued JSON-schema-versioning change independent.

## Similar past work

`adopt-strictyaml-frontmatter` established the constrained frontmatter parser and source/active inventory synchronisation. `add-decision-gated-progression` and `add-delivery-policy` established the lifecycle flows that the validator must now model without reinterpreting prose.
