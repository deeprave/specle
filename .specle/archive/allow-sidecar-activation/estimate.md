# Estimate: Allow sidecar activation

## T-shirt size

M

## Breakdown

- Modified files: approximately 12–18, including lifecycle policy, activation and build skills, abbreviated workflow skills and their installed and blueprint copies, next-action logic, and focused tests.
- New files: no production modules expected.
- Estimated tasks: 4–6 implementation slices.
- Key risks: changing ownership of abbreviated execution without losing bugfix or refactor safeguards; preserving the selected parent and explicit delivery relationships; keeping lifecycle metadata and next-action reporting coherent.

## Confidence

Medium. Existing lifecycle metadata and the shared resolver provide useful infrastructure, but the workflow currently embeds execution rules in several skills and the supported kind/state combinations need careful reconciliation.

## Recommendation

Keep the work as one change and design the dispatch and preparation boundaries before tasks. Preserve the existing selected normal and spike flows and avoid a dependency on planned record or enum refactors.

## Similar past work

The archived `add-specle-changes-index` change established next-action reporting and the current S-sized preparation path; `correct-to-thread-abuse` illustrates explicitly linked abbreviated delivery.
