# Tasks: add specle update

- [x] 1. Model manifest generations and update plans.
  - [x] 1.1 Add focused tests in `tests/test_manifest.py` for parsing release generations, checksum-path maps, malformed/conflicting manifests, and exact/likely/indeterminate detection evidence.
  - [x] 1.2 Implement typed manifest-generation parsing and version-detection helpers in `src/specle/manifest.py`, reusing the existing manifest line validation.
  - [x] 1.3 Add a flattened managed-resource view and typed update-plan records in `src/specle/inventory.py` without re-scanning either inventory.

- [x] 2. Extract the shared managed deployment transaction.
  - [x] 2.1 Add focused tests in `tests/test_inventory_initialisation.py` proving staged add/replace/remove operations recover from failure and preserve user-owned neighbouring files.
  - [x] 2.2 Refactor `src/specle/inventory.py` so `initialise_distribution` builds its existing full-install operation plan and uses one reusable staged backup/recovery transaction.
  - [x] 2.3 Implement resource-level apply operations for normal updates, including safe empty-directory cleanup and regenerated `skills/specle/index.json`.

- [x] 3. Extend inventory and plan modelling for reviewed safety cases.
  - [x] 3.1 Add production tests for unmanaged policy collisions, exact additive/subtractive manifest detection, and project-overlay shape guidance.
  - [x] 3.2 Extend `ManagedInventory`, manifest detection, and planning so unmanaged paths and the single displayed plan drive safe actions.
  - [x] 3.3 Generate the index after managed actions from projected installed metadata, retain rollback recovery, and clean up failed-operation directories.

- [x] 4. Apply and validate the displayed plan through the CLI.
  - [x] 4.1 Add command tests for TTY-only confirmation, non-interactive failure, applying a plan once, and post-update validation output.
  - [x] 4.2 Refactor CLI application to use the displayed plan once, enforce TTY confirmation, and run/report validation after applied updates.

- [x] 5. Verify the complete feature.
  - [x] 5.1 Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, and `uv run ty`.
  - [x] 5.2 Run `uv run specle validate --blueprint` and installed-target validation after exercising update behaviour.

- [x] 6. Separate distribution scanning from update models and planning.
  - [x] 6.1 Add focused production tests for typed action and confidence domains without testing retired names or implementation structure.
  - [x] 6.2 Rename `ManagedInventory` to `DistributionInventory`, move update-specific models and planning to dedicated modules, and retain one-way imports through shared leaf records.
  - [x] 6.3 Replace production assertion-based validation with explicit exceptions.

- [x] 7. Make manifest detection and skills atomic update units.
  - [x] 7.1 Add production tests for equivalent exact release generations and atomic replacement or removal when one skill resource diverges.
  - [x] 7.2 Detect an equivalent exact-generation class as the latest exact release, preserving its common checksums for safe update planning.
  - [x] 7.3 Plan and apply managed skills as complete directories; preserve or replace every resource together, while retaining resource-level policy handling.

- [x] 8. Make update orchestration asynchronous and directly reusable.
  - [x] 8.1 Add end-to-end CLI tests for non-TTY conflict failure without mutation, update-specific staging recovery, direct post-update validation, and force dry-run wording.
  - [x] 8.2 Extract reusable asynchronous inventory/manifest scan, confirmation, update, and validation operations; do not recurse through `main`.
  - [x] 8.3 Use an asynchronous confirmation prompt and report force behaviour conditionally during dry runs.

- [x] 9. Verify the revised update behaviour.
  - [x] 9.1 Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, and `uv run ty check`.
  - [x] 9.2 Run `uv run specle validate --blueprint`, installed-target validation, and representative update dry-run and applied-update checks.
