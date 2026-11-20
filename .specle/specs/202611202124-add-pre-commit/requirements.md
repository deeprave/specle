# Requirements: add pre-commit

## Introduction

Specle currently has no repository-local pre-commit configuration or installed Git hook. This change adds a focused local developer safeguard without changing CI or making pre-commit a Python project dependency.

## Requirements

### Requirement 1: Provide a repository pre-commit configuration

1. THE repository SHALL add `.pre-commit-config.yaml` at its root.
2. THE configuration SHALL use the latest available release of every remote hook repository when this change is implemented, with each release pinned in the configuration.
3. THE configuration SHALL include these hooks from `pre-commit/pre-commit-hooks`:
   - `no-commit-to-branch` with `args: ["--branch", "main"]` and `exclude: "^main$"`;
   - `end-of-file-fixer`;
   - `trailing-whitespace`;
   - `check-yaml`;
   - `check-added-large-files`;
   - `check-merge-conflict`;
   - `check-toml`; and
   - `requirements-txt-fixer`.
4. THE configuration SHALL include the `ruff` hook from `https://github.com/astral-sh/ruff-pre-commit`, using the latest available pinned release with `--fix` and `--line-length=120` arguments.
5. THE configuration SHALL include the `osvcheck` hook from `https://github.com/deeprave/osvcheck`, using its latest available pinned release.

### Requirement 2: Provide local Python quality hooks

1. THE configuration SHALL define a local system-language `pytest` hook with `entry: uv run pytest -Walways -Werror`, `types: [python]`, and `pass_filenames: false`.
2. THE configuration SHALL define a local system-language `ty` hook named `ty check` with `entry: ty check`, `types: [python]`, and `pass_filenames: false`.

### Requirement 3: Keep pre-commit local

1. PRE-COMMIT SHALL be supplied by the hosted development environment and installed as a Git hook for this repository.
2. THE change SHALL NOT add pre-commit to the virtual environment, `pyproject.toml`, dependency groups, or the lockfile.
3. THE change SHALL NOT add pre-commit execution to GitHub Actions or any other CI workflow.

## Non-functional requirements

- The configuration must be readable and use the repository’s existing YAML conventions.
- The installed hook must not block direct work on branches other than `main`.
- Remote hook versions must be verified immediately before implementation rather than copied from an outdated example.
