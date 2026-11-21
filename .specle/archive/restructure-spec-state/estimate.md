# Estimate: restructure Specle spec state

## T-shirt size

XL

## Breakdown

- New files: per-spec `status.json` resources and schemas, archive support, local-state bootstrap guidance, migration fixtures, and focused tests.
- Modified files: lifecycle/state readers and writers, all affected skill blueprints, installed inventory, documentation, CLI validation, and existing runtime/spec records.
- Estimated tasks: 12–16.
- Key risks: preserving evidence during migration; keeping selection local without weakening worktree isolation; deriving effective completion accurately; delivery-model-specific completion PRs; and maintaining archive discovery and stable-name references.

## Confidence

Medium. The target model is decided, but the implementation must reconcile the current tracked context workflow with the new per-spec contract without losing historical delivery evidence.

## Recommendation

Continue through a detailed design. Treat this as an independent migration: do not depend on a future schema-versioning change beyond defining the required versioned `status.json` contract now.

## Similar past work

- `versioned-json-schemas` established packaged JSON Schema resources, registry loading, and contract validation.
- `add-delivery-policy` established the current branch-and-pull-request delivery lifecycle that this change restructures.
