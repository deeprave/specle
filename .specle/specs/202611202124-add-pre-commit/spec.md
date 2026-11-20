# Add pre-commit

## Problem

The repository has CI quality checks but no local pre-commit hook that catches common whitespace, syntax, dependency, security, lint, test, and type-check issues before a commit is created.

## Goal

Add a root pre-commit configuration and install its Git hook using the hosted pre-commit executable, without changing Python dependencies or CI.

## Scope

The configuration will combine the requested standard repository checks, Ruff autofix, osvcheck, and local pytest and Ty hooks. Remote hook revisions will be pinned to their current releases at implementation time. The hook will reject commits directly to `main` while allowing normal feature-branch work.

## Constraints

Pre-commit remains host-provided: it must not be added to the project environment, `pyproject.toml`, or CI. The requested local Ty hook entry is retained exactly as specified and must be validated during implementation.

## Verification

Validate the configuration, install the Git hook, run the hook suite against the repository, confirm no project dependency or CI changes were introduced, and confirm the `main` branch guard behaves as configured.
