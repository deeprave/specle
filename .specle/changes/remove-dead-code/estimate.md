# Estimate: Remove dead code

## T-shirt size

M

## Breakdown

- New files: 0–1, only if a concrete retained-use exception requires the Vulture whitelist.
- Modified files: approximately 8–10 across pre-commit configuration, six production modules, and focused tests.
- Estimated tasks: 4.
- Key risks: accidentally treating test coverage as a retention reason; removing an internal helper without preserving its actual command-line consumer behaviour; and making the Vulture gate noisy enough that it is routinely bypassed.

## Confidence

High. Repository evidence shows no declared Python API beyond the `specle` command, while the reported symbols have either no caller or only direct test callers. The exact deletion and test consolidation still need design-level tracing of the command paths.

## Recommendation

Proceed as one change. Retention is narrowly decided from present, concrete product or compatibility requirements—not speculative external use. The Vulture gate should examine the complete source and test trees at the confidence level that reports these unused functions, with a versioned whitelist only for exceptions that meet that evidence standard.

## Similar past work

The archived `add-pre-commit` change established the local, host-provided pre-commit model. This change extends that model without adding a project dependency or CI job.
