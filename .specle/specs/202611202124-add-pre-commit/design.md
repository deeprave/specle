# Design: add pre-commit

## Overview

Add a repository-root `.pre-commit-config.yaml` that combines standard repository hygiene checks, Ruff autofix, osvcheck, and local Python test and type-check hooks. Install the hosted `pre-commit` executable as this checkout's Git hook without changing project dependencies, the lockfile, or CI.

## Architecture

```text
git commit on feature branch
    │
    └── pre-commit Git hook
          ├── branch guard and repository hygiene hooks
          ├── Ruff remote hook with autofix
          ├── osvcheck remote hook
          └── local system hooks: pytest and ty check
```

The `no-commit-to-branch` hook blocks direct commits to `main` while feature branches remain eligible for ordinary commits. Remote hook repositories are pinned to releases discovered immediately before implementation. Local `system` hooks use the hosted executables and do not create a pre-commit-managed Python environment.

## Configuration

The configuration has four hook groups:

1. `pre-commit/pre-commit-hooks` supplies the requested branch, whitespace, YAML, file-size, merge-conflict, TOML, and requirements checks.
2. `astral-sh/ruff-pre-commit` supplies Ruff with `--fix` and `--line-length=120`.
3. `deeprave/osvcheck` supplies the dependency vulnerability hook.
4. `repo: local` defines system-language `uv run pytest -Walways -Werror` and `ty check` hooks, both restricted to Python files and configured with `pass_filenames: false`.

No project configuration, dependency group, lockfile, or GitHub workflow is modified. The Git-hook installation is local checkout state and therefore is not committed.

## Failure handling

| Condition | Behaviour |
| --- | --- |
| Direct commit to `main` | `no-commit-to-branch` rejects the commit. |
| Formatting or hygiene issue | The relevant hook reports the issue; Ruff may apply its configured autofix. |
| Test or type-check failure | The system hook exits non-zero and blocks the commit. |
| Remote hook install or execution failure | Pre-commit reports the failed hook; no commit is created. |
| Hosted executable unavailable | Stop installation or validation and report the missing tool; do not add a project dependency as a workaround. |

## Test strategy

- Validate the YAML configuration with pre-commit.
- Install the hook with the hosted executable and confirm the Git hook exists.
- Run the configured hook suite against all files, resolving only issues in scope for this change.
- Confirm the branch guard rejects a direct `main` commit without creating one.
- Run the existing project quality gates through `uv`: `pytest`, `ruff check`, `ruff format --check`, and `ty check`.
