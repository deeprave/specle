# Enable Dependabot auto-merge

## Problem

Specle has matrix CI checks but no stable aggregate check for branch rules, and no workflow that lets the installed Uniquode auto-merge App merge eligible Dependabot pull requests.

## Goal

Provide a clear CI verification gate and an opt-in Dependabot auto-merge workflow that works with the repository's merge-only ruleset.

## Behaviour

- Refactor the test workflow into clearly named verification jobs for formatting, linting, type checking, and tests across supported Python versions.
- Add an always-running `Verify` aggregate job that reports one stable required check after all required jobs finish.
- Require `Verify` in the existing `main` ruleset.
- Configure Dependabot to create updates for the `uv` and GitHub Actions ecosystems.
- Add a workflow that authenticates as the configured Uniquode GitHub App and enables merge-commit auto-merge only for eligible Dependabot updates.
- Use `AUTOMERGE_APP_CLIENT_ID` and `AUTOMERGE_APP_PRIVATE_KEY`; do not expose secret values.
- Before invoking the trusted App's merge operation, query the PR's currently required checks and proceed only when every check, including `Verify`, has passed.

## Constraints

Keep existing pull-request and `main` push coverage. Preserve manual merge-only delivery and do not broaden automated merging beyond the defined Dependabot eligibility policy.

## Verification

Verify Dependabot configuration is valid for both ecosystems, confirm `Verify` is the required ruleset check through pull-request CI, and confirm the auto-merge workflow does nothing for ineligible or non-Dependabot pull requests.
