# Tasks: Cleanup complete

## Completed before review revision

- [x] 1. Add initial lifecycle, inventory, and schema regression coverage for one-PR completion and remove `wrapup`. (`tests/test_lifecycle.py`, `tests/test_inventory_metadata.py`, `tests/test_schema_registry.py`)
- [x] 2. Replace original branch-delivery guidance and managed inventory with the first one-PR completion design. (`.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 3. Run initial full quality gates and installed/blueprint validation.

## Review revision

- [x] 4. Extend change-status validation and migrate historical archive records to remove `delivery.completion.commit`; specify direct delivery without PR completion evidence. (`src/specle/schemas/change-status/1.0.json`, `.specle/archive/*/status.json`, `tests/test_schema_registry.py`, `tests/test_lifecycle.py`)
- [x] 5. Revise lifecycle, delivery, commit, complete, triage, resolve, review, activate, status, summary, and documentation guidance for normal completion, archived-unmerged feedback, and exceptional premature-merge recovery. (`.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 6. Add conservative PR CI classification and fast metadata validation while retaining required `Verify` and full `main` coverage. (`.github/workflows/test.yml`, workflow-focused tests or validation)
- [x] 7. Regenerate the installed skill index and add focused regression coverage for direct completion, recovery branch guards, resumption, archived feedback, schema migration, and fast-lane workflow structure. (`.agents/skills/specle/index.json`, `tests/`)
- [x] 8. Run full project gates, installed and blueprint validation, workflow syntax/structure checks, historical-archive migration audit, and re-review the delivery model.

## Revised after Antigravity review

- [x] 9. Repair direct-delivery runtime evidence validation and remove every archived-feedback lifecycle exception. (`src/specle/lifecycle.py`, `.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 10. Clarify normal and recovery completion, including existing-PR authority, tracked-only staging, direct push, closed-PR stops, and immutable recovery archive transport. (`.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 11. Extract fail-closed PR validation-lane classification into a local reusable action, remove recurring workflow tests, and validate it with `act`. (`.github/actions/`, `.github/workflows/test.yml`)
- [x] 12. Reconcile accepted review dispatches, align entrypoint/index documentation, run full gates, act validation, and re-review.
