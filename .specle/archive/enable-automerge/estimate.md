# Complexity estimate: enable Dependabot auto-merge

## T-shirt size

**L**

## Breakdown

- **New files:** approximately 2–3 — Dependabot configuration and a dedicated auto-merge workflow, with possible workflow support configuration.
- **Modified files:** approximately 2–4 — the test workflow, repository ruleset configuration, and project documentation where the automation policy needs recording.
- **Estimated tasks:** approximately 6–8 — split CI jobs, add the stable aggregate gate, configure Dependabot, define eligibility, implement App-token auto-merge, configure the ruleset, and validate safe non-eligible behaviour.
- **Key risks:** the aggregate `Verify` job must fail reliably when any matrix or quality job fails; App authentication and private-key handling must not expose credentials; the ruleset must require verification without changing existing manual merge controls; and eligibility must be precise enough that automation cannot merge an unintended pull request.

## Confidence

**Medium.** The intended outcomes and configured App credentials are known, but the specific Dependabot eligibility policy and the exact existing ruleset representation need design-level confirmation.

## Recommendation

Continue through design. Keep Dependabot PRs within the ordinary verification and ruleset flow; the auto-merge workflow should enable merge only after the stable `Verify` gate is satisfied. Define the eligibility policy explicitly rather than inferring it from the App installation or PR author alone.

## Similar past work

`202611180808-add-delivery-policy` established the project’s branch-and-pull-request delivery controls and explicit external-write boundaries. This change extends those controls with narrowly scoped automation rather than replacing them.
