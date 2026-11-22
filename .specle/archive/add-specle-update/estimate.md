# Estimate: add Specle update

## T-shirt size

**L**

## Breakdown

- **New files:** approximately 2–4 for update planning/version-detection services and focused fixtures representing historical manifest generations.
- **Modified files:** approximately 6–10 across manifest parsing, inventory planning and transactional application, CLI parsing/output, and inventory/CLI tests.
- **Estimated tasks:** 8–10 test-first tasks covering generation detection, confidence, dry-run reporting, selective update actions, force delegation, ownership preservation, recovery, and validation.

## Key risks

- Historical manifests identify resource paths and checksums, while the existing installer replaces managed skill directories. The design must establish a selective, recoverable application plan without duplicating transactional filesystem code.
- User modifications and missing resources make generation detection inherently best-effort. The output must distinguish an exact match, a likely match, and an indeterminate result rather than invent certainty.
- The current manifest has one generation, so fixtures must model historical additions, changes, and removals without treating old names or behaviours as supported compatibility paths.
- `--force` must deliberately converge on existing `init --force` behaviour while normal update preserves modified managed content.

## Confidence

**Medium.** The shared scans, checksums, drift comparison, and replacement/recovery mechanisms already exist, but version-aware selective planning changes the unit of installation from an all-or-nothing deployment to resource-level actions.

## Recommendation

Proceed to design. Define the manifest-generation matching algorithm, confidence labels, plan data model, and the boundary between selective update and forced full replacement before creating tasks.

## Similar past work

- `add-specle-manifest` provides the package-owned release checksum history and manifest parser.
- `specle-cli-init` provides staged managed-content replacement, rollback, and index generation.
- `support-blueprint-validate` provides shared blueprint and installed inventory comparison.
