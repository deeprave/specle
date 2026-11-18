# Complexity estimate: delivery policy and completion workflow

## T-shirt size

**XL**

## Breakdown

- **New files:** approximately 3–5: portable delivery steering, project delivery guidance, and `commit` and `complete` skill blueprints.
- **Modified files:** approximately 10–14: onboarding, lifecycle, review, triage, resolve, context guidance, project README, existing workflow skills, and their active installed copies.
- **Estimated tasks:** approximately 6–8 implementation slices spanning policy, onboarding, lifecycle, delivery actions, submitted-work re-entry, and behavioural coverage.
- **Key risks:** delivery policy must remain portable while safely governing external actions; a `complete` workflow must never disturb an unrelated checkout; delivery records need the separate versioned JSON contract rather than an ad-hoc shape.

## Confidence

**Medium.** The required workflow is well defined, but it crosses most existing lifecycle skills and depends on the separate JSON-contract change.

## Recommendation

The existing design is required and sufficient for planning. Complete the versioned JSON-contract dependency before building any delivery-record behaviour; do not create a temporary record format.

## Similar past work

`202611171707-specle-cli-init` established explicit installation ownership and recovery boundaries. This change applies the same explicit-authority and recovery principles to repository delivery.
