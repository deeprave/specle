# Summary: add pre-commit

## Outcome

Specle now has a repository-root pre-commit configuration and an installed local Git hook. It checks branch safety, common repository hygiene, Ruff fixes, dependency vulnerabilities, tests, and type checking before commits are created.

## What changed

- Added `.pre-commit-config.yaml` with pinned `pre-commit-hooks`, Ruff, and osvcheck hook releases.
- Blocked direct commits to `main` while allowing feature-branch commits.
- Added frozen uv-managed pytest and Ty checks, so local checks use the same locked project environment as CI.
- Extended the generic hidden-cache ignore rule to cover generated cache files and directories.

## Evidence

- The complete pre-commit suite passed on the feature branch, including the frozen pytest and Ty hooks.
- The direct-`main` guard was verified to reject a commit attempt without creating a commit.
- Project quality gates passed: pytest (65 tests), Ruff check, Ruff format check, and Ty check.
- PR #15 passed its required GitHub `Verify` check and was merged as `0650616`.

## Key decisions and limits

- Pre-commit remains host-provided and is not a project dependency or CI job.
- Ruff remains a pinned remote pre-commit hook; pytest and Ty are local hooks run through the locked project environment.
- Fresh-clone setup instructions were deliberately not added; local installation is the intended scope.

## Recommendation and follow-up

Use the installed hook for normal feature-branch commits. Revisit hook setup documentation only if this repository later needs a contributor onboarding path.

## Copy-ready update

Added and validated local pre-commit safeguards for Specle, including branch protection, repository hygiene checks, Ruff, osvcheck, and frozen uv-managed pytest and Ty checks. PR #15 passed CI and has been merged.
