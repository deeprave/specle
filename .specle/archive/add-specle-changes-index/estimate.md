# Estimate: Add Specle changes and index

## T-shirt size

M

## Breakdown

- Modified files: approximately 5–8 across CLI parsing, state presentation, inventory writing, and tests.
- New files: 0–2 focused test modules or helpers.
- Estimated tasks: 4.
- Key risks: keeping CLI output read-only and deterministic; using durable timestamps without inventing fallback state; and ensuring index-only replacement preserves every other installed resource.

## Confidence

High. Existing change-state, inventory, lifecycle analysis, and index-generation components provide the required primitives.

## Recommendation

Implement as one change. Reuse the validated record and inventory readers; do not create parallel parsing, state, or index-generation paths.
