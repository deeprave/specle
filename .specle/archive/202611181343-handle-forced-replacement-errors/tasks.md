# Tasks: handle forced replacement errors

- [x] 1. Add a failing regression test in `tests/test_inventory_initialisation.py` for a forced replacement failure before index installation, preserving the prior index and cleaning temporary paths.
- [x] 2. Translate replacement I/O failures in `src/specle/inventory.py` into destination-specific `SkillInstallationError` values and clean remaining staged paths before re-raising.
- [x] 3. Run the focused regression and all documented quality gates.
- [x] 4. Replace the single-skill regression in `tests/test_inventory_initialisation.py` with failing forced-installation cases for an index-hosting skill and another resource-bearing skill, preserving every previous resource and the index.
- [x] 5. Replace special-cased skill installation in `src/specle/inventory.py` with backup-and-restore handling for every managed destination; retain destination-specific errors and commit the generated index last.
- [x] 6. Run the focused regressions and all documented quality gates after the transactional repair.
- [x] 7. Add a failing rollback-failure regression in `tests/test_inventory_initialisation.py` that verifies the unrecovered backup remains available and its path is reported.
- [x] 8. Update `src/specle/inventory.py` to distinguish restored from unrestored backups, clean only safe paths, and include any retained backup locations in the installation error.
- [x] 9. Run the focused rollback regression and all documented quality gates after the recovery-path repair.
- [x] 10. Add regression coverage for resolving the packaged blueprint root after moving the source inventory beneath `src/specle/blueprints/`.
- [x] 11. Move the portable workflow entrypoint, skills, and steering source inventory into `src/specle/blueprints/`; update resource resolution and source-location references.
- [x] 12. Update the portable blueprint and active `.agents` workflow entrypoints so an explicit `next` instruction invokes the suggested next stage automatically.
- [x] 13. Run the relevant regression suite and all documented quality gates after the blueprint relocation and workflow update.
