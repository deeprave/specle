# Tasks: add pre-commit

- [x] 1. Add the repository pre-commit configuration
  - [x] 1.1 Confirm the current release tags for `pre-commit-hooks`, `ruff-pre-commit`, and `osvcheck`.
  - [x] 1.2 Add `.pre-commit-config.yaml` with the required remote hooks, pinned releases, branch guard, and Ruff arguments.
  - [x] 1.3 Add local `system` hooks for `uv run pytest -Walways -Werror` and `ty check`, limited to Python files without filename arguments.

- [x] 2. Validate and install the local Git hook
  - [x] 2.1 Validate the configuration and install the hosted pre-commit hook in this checkout.
  - [x] 2.2 Run every configured hook against repository files and resolve configuration-owned failures.
  - [x] 2.3 Confirm the `main` branch guard rejects a direct commit without creating one, while preserving the current branch and working tree.

- [x] 3. Verify project safeguards remain unchanged
  - [x] 3.1 Confirm no project dependency, lockfile, or CI workflow was added or changed for pre-commit.
  - [x] 3.2 Run `uv`-managed pytest, Ruff check, Ruff format check, and Ty check.

- [x] 4. Keep generated hook caches out of the working tree
  - [x] 4.1 Extend the existing generic hidden-cache ignore rule to cover files as well as directories.
  - [x] 4.2 Confirm an osvcheck run no longer leaves an untracked cache file.

- [x] 5. Align local Python hooks with the locked project environment
  - [x] 5.1 Run pytest through `uv run --frozen`.
  - [x] 5.2 Run Ty through `uv run --frozen`.
  - [x] 5.3 Re-run the hook suite and project quality gates.
