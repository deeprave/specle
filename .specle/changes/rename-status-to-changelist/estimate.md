# Estimate: Rename status to changelist

## T-shirt size

M

## Breakdown

- New files: ~1 managed skill directory and its installed copy.
- Modified files: ~8–12, including the renamed skill, new status skill, workflow references, lifecycle documentation, and generated index.
- Estimated tasks: 4 top-level tasks.
- Key risks: preserving the existing changelist inventory unchanged while making the new status report concise, correct for both primary and linked worktrees, and clearly read-only.

## Confidence

High

## Recommendation

Use a design to separate the two commands and identify every reference to the existing inventory behaviour before renaming it. No Python CLI work is required.

## Similar past work

`enhance-define-skill` recently refined managed workflow boundaries and demonstrates the required blueprint-to-installed synchronisation and index regeneration process.
