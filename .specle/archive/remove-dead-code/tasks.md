# Tasks: Remove dead code

- [x] 1. Establish the retained behavioural boundary before deletion.
  - [x] 1.1 Trace each reported symbol from the CLI, package metadata, documentation, and tests; classify it as required or unsupported with concrete evidence.
  - [x] 1.2 Confirm the existing command-level tests cover the retained init, update, validation, manifest, and schema-export paths; no new behavioural test is needed before removing unreachable helpers. Files: `tests/test_main.py`.

- [x] 2. Remove unsupported helpers and helper-only tests.
  - [x] 2.1 Remove the uncalled and test-only inventory and change-state helpers, then delete or consolidate their direct-only tests. Files: `src/specle/change_state.py`, `src/specle/inventory.py`, `tests/test_inventory_initialisation.py`, `tests/test_inventory_metadata.py`, `tests/test_inventory_resolution.py`.
  - [x] 2.2 Remove unsupported lifecycle, timestamp, and sidecar helpers and their direct-only tests while retaining actual validation and command behaviour coverage. Files: `src/specle/lifecycle.py`, `src/specle/schema_registry.py`, `src/specle/sidecars.py`, `tests/test_lifecycle.py`, `tests/test_schema_registry.py`.

- [x] 3. Complete the Vulture gate.
  - [x] 3.1 Change the existing Vulture pre-commit hook to the confidence threshold that reports the identified unused-function class and retain complete-tree scanning. File: `.pre-commit-config.yaml`.
  - [x] 3.2 No concrete supported exception was found, so no whitelist is required or added.

- [x] 4. Verify removal and integration.
  - [x] 4.1 Run Vulture at the configured threshold and confirm it reports no unapproved production dead code.
  - [x] 4.2 Run the complete pre-commit suite and the documented pytest, Ruff, formatting, Ty, and Specle validation gates.
