# Tasks: Add Specle changes and index

- [x] 1. Add failing focused tests for diagnostic rows representing malformed/schema-invalid and unrenderable-timestamp records alongside valid results. Files: `tests/test_main.py`, focused state tests.
- [x] 2. Extend change discovery and report presentation so malformed/schema-invalid and timestamp-invalid records remain visible with diagnostics in text, JSON, and CSV output. Files: `src/specle/change_state.py`, `src/specle/main.py`.
- [x] 3. Verify the diagnostic-row presentation with focused tests and all project quality gates. Files: project tooling.
- [x] 4. Exclude invalid change names from listings, use static report diagnostic causes, and validate dependency names without requiring their targets to exist. Files: `src/specle/change_state.py`, `src/specle/main.py`, schema resources as applicable.
- [x] 5. Add shared project-directory preflight and report invalid or unreadable selectors without synthetic change rows; preserve standalone resource command exemptions. Files: `src/specle/main.py`, relevant state helpers.
- [x] 6. Resolve selected changes' next preparation action from artifacts and make S-sized normal work skip design across lifecycle metadata, policies, and preparation skills, including installed and blueprint copies. Files: `src/specle/`, `.agents/`, `src/specle/blueprints/`.
- [x] 7. Render missing, invalid, or inapplicable optional archive dates empty and emit CRLF CSV records. Files: `src/specle/main.py`.
- [x] 8. Add `index --force` for lifecycle diagnostics while always reporting them and retaining other blocking validation. Files: `src/specle/main.py`.
- [x] 9. Strengthen index regeneration coverage to check installed metadata, including a valid local edit, is reflected in the generated index. Files: `tests/test_main.py`.
