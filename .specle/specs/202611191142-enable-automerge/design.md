# Design: enable Dependabot auto-merge

## Overview

Refactor the existing test workflow into independently named quality jobs and a stable aggregate `Verify` job. Configure the existing `main` ruleset to require only that aggregate check. Add Dependabot configuration for `uv` and GitHub Actions, plus a dedicated workflow that enables merge-commit auto-merge for narrowly eligible Dependabot pull requests after GitHub has observed the required gate.

## Architecture

```text
Dependabot PR
    │
    ├── test workflow ──► lint ───────┐
    │                     format ─────┤
    │                     type check ─┼──► Verify (stable required check)
    │                     pytest matrix┘
    │                                      │
    └── auto-merge workflow ──► App token ─┼──► eligibility check ──► enable merge auto-merge
                                           │
main ruleset ◄─────────────────────────────┘
```

The ruleset requires `Verify` alone. Individual CI jobs remain observable dependencies of `Verify`, so their names and the test matrix can evolve without changing the required-check rule.

## CI workflow

Refactor `.github/workflows/test.yml` into separately named jobs for Ruff linting, Ruff formatting, Ty type checking, and pytest. The pytest job retains the Python 3.13, 3.14, and 3.15 matrix. Every job continues to use the existing pinned checkout/setup-uv actions and `uv sync --frozen --all-groups` setup.

Add a `Verify` job that:

- declares all required quality jobs in `needs`;
- uses an always-running condition so it executes even after a failed dependency; and
- fails unless every dependency succeeded.

The displayed `Verify` check name is stable and is the only workflow check added to the `main` ruleset’s required-status-checks rule.

## Dependabot configuration

Add `.github/dependabot.yml` with repository-root entries for:

- `uv`; and
- `github-actions`.

Use a documented regular schedule. Dependabot continues to create ordinary pull requests; neither configuration nor the auto-merge workflow bypasses review, ruleset, or required-check behaviour.

## Auto-merge workflow

Add a dedicated workflow on `pull_request_target`. It must first confirm that the pull request author is `dependabot[bot]` and targets `main`; it must not check out or run pull-request code. `pull_request_target` evaluates the workflow from the base repository, so the trusted workflow can use the configured App credentials. This is safe only because every step operates on pull-request metadata and no step executes content from the pull-request branch.

The workflow obtains an installation token from `AUTOMERGE_APP_CLIENT_ID` and `AUTOMERGE_APP_PRIVATE_KEY` through a pinned GitHub App token action. It passes that token to Dependabot metadata inspection and the merge-enabling command. It never prints either credential or token.

Eligibility is explicit:

| Ecosystem | Eligible update types |
| --- | --- |
| `uv` | SemVer patch and minor |
| `github-actions` | SemVer patch, minor, and major |

All other authors, ecosystems, update types, metadata failures, and unknown values are ineligible. For an eligible pull request, the workflow uses the App token to run `gh pr checks --required --watch --fail-fast` against the PR. That command waits for the live required-check set, which includes `Verify`; a failed check exits the job without any merge operation. Only after the command succeeds does the workflow invoke merge-commit auto-merge. The trusted App retains its ruleset bypass, but the workflow itself enforces the required-check precondition.

## Ruleset and repository settings

Update the existing active `Main` ruleset rather than creating a classic branch-protection rule. Preserve its `main` targeting, merge-only restriction, deletion and non-fast-forward protections, existing repository-administrator bypass, and Uniquode App bypass. Add `Verify` as its required status check.

Retain automatic deletion of merged pull-request branches. No workflow setting changes the project’s normal human delivery path.

## Failure handling

| Condition | Behaviour |
| --- | --- |
| Quality job fails | `Verify` fails; the ruleset prevents merge. |
| Required check fails or is cancelled | The required-check command exits without invoking the merge operation. |
| App token or metadata lookup fails | The auto-merge job fails without enabling merge. |
| Dependabot created the PR base ref | Repository secrets are unavailable under GitHub's Dependabot restrictions; the job fails closed without enabling merge. |
| PR is not Dependabot-authored | The auto-merge workflow does nothing. |
| Update is outside policy | The workflow reports or exits as ineligible without enabling merge. |
| Ruleset update cannot preserve existing actors/rules | Stop before changing repository settings and report the conflict. |

## Test strategy

- Inspect workflow job dependencies and `Verify` failure aggregation through pull-request CI.
- Validate Dependabot configuration syntax and its two ecosystem entries.
- Inspect ruleset configuration to confirm `Verify` is required while existing rules and bypass actors remain present.
- Exercise or inspect workflow conditions for eligible and ineligible Dependabot metadata, and confirm no workflow path checks out untrusted pull-request code or logs credentials.
- Inspect the workflow to confirm it waits for the PR's live required checks and invokes the merge operation only after they pass.
- Run the project quality gates: `pytest`, `ruff check`, `ruff format --check`, and `ty`.
