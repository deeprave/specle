# Complexity estimate: delivery policy and completion workflow

## T-shirt size

**XL**

## Breakdown

- **New files:** approximately 3–5: portable delivery steering, project delivery guidance, and `commit` and `complete` skill blueprints.
- **Modified files:** approximately 10–14: onboarding, lifecycle, review, triage, resolve, context guidance, existing workflow skills, root references, and their active installed copies.
- **Estimated tasks:** approximately 6–8 implementation slices spanning policy, onboarding, lifecycle, delivery actions, submitted-work re-entry, and behavioural coverage.
- **Key risks:** delivery policy must remain portable while safely governing external actions; a `complete` workflow must never disturb an unrelated checkout; the delivery state needed by this change must be recorded only to the extent required by its implemented workflow, without anticipating a future schema change.

## Confidence

**Medium.** The required workflow is well defined, but it crosses most existing lifecycle skills and governs external repository operations. It has no dependency on queued future work.

## Recommendation

The existing design is required and sufficient for planning. Continue through the normal design, task, implementation, and quality stages. Do not introduce requirements from queued future work; any record added here must serve this change's currently implemented behaviour.

## Similar past work

`202611171707-specle-cli-init` established explicit installation ownership and recovery boundaries. This change applies the same explicit-authority and recovery principles to repository delivery.
