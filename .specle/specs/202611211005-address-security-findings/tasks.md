# Tasks: address security findings

- [x] 1. Add failing validation-boundary tests
  - [x] 1.1 Cover regular files and symlinks resolving to regular files as valid validation inputs.
  - [x] 1.2 Cover non-regular resolved inputs for runtime state, managed skills, and the generated index, asserting a diagnostic is returned before content is read. Touch `tests/test_lifecycle.py`, `tests/test_main.py`, and focused inventory tests as appropriate.
  - [x] 1.3 Cover a broken optional selector as an invalid validation input rather than an absent selector. Touch `tests/test_lifecycle.py`.
- [x] 2. Implement the shared validation text-reader boundary
  - [x] 2.1 Add a narrow helper that accepts regular resolved files and reports a path-specific failure for every other type. Touch `src/specle/` validation modules.
  - [x] 2.2 Route installed-skill discovery, runtime state, and generated-index reads through the helper while preserving existing malformed/unreadable diagnostics. Touch `src/specle/inventory.py`, `src/specle/spec_state.py`, and `src/specle/main.py`.
  - [x] 2.3 Distinguish an absent optional file from a broken symlink that does not resolve to a regular file. Touch `src/specle/file_reading.py`.
  - [x] 2.4 Add a production-code regression test for a candidate installed `SKILL.md` that is non-regular or a broken link. Touch `tests/test_inventory_metadata.py`.
  - [x] 2.5 Branch installed-skill discovery so an absent `SKILL.md` remains ignored but an existing or broken-link non-regular `SKILL.md` fails validation with a diagnostic. Touch `src/specle/inventory.py`.
- [x] 3. Inspect workflow credential timing
  - [x] 3.1 Inspect the workflow to confirm ordinary-token metadata and required-check polling, unchanged eligibility conditions, and secret use only by the final App-token step. Do not add a workflow test.
- [x] 4. Defer the App token to the final merge action
  - [x] 4.1 Give the ordinary workflow token only the required read scopes and use it for metadata and `gh pr checks`. Touch `.github/workflows/dependabot-automerge.yml`.
  - [x] 4.2 Create and use the GitHub App token only in the eligible, passing auto-merge step, retaining merge-commit auto-merge and all established eligibility conditions. Touch `.github/workflows/dependabot-automerge.yml`.
- [x] 5. Run the focused and complete validation suite
  - [x] 5.1 Run the changed test modules, then `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and `uv run --frozen specle validate . --verbose`.
