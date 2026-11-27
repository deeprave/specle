# Tasks: Add Specle changes and index

- [x] 1. Add failing focused tests for diagnostic rows representing malformed/schema-invalid and unrenderable-timestamp records alongside valid results. Files: `tests/test_main.py`, focused state tests.
- [x] 2. Extend change discovery and report presentation so malformed/schema-invalid and timestamp-invalid records remain visible with diagnostics in text, JSON, and CSV output. Files: `src/specle/change_state.py`, `src/specle/main.py`.
- [x] 3. Verify the diagnostic-row presentation with focused tests and all project quality gates. Files: project tooling.
