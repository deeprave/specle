# Tasks: enable Dependabot auto-merge

- [x] 1. Refactor `.github/workflows/test.yml` into independently named lint, format, type-check, and Python-matrix pytest jobs, then add an always-running `Verify` aggregate job that fails unless every dependency succeeds. Preserve the existing triggers, pinned actions, and `uv` setup.
- [x] 2. Add `.github/dependabot.yml` with documented repository-root update schedules for the `uv` and `github-actions` ecosystems.
- [x] 3. Add a dedicated Dependabot-only auto-merge workflow. Generate an App token without checking out pull-request code, inspect Dependabot metadata, and enable merge-commit auto-merge only for `uv` patch/minor and GitHub Actions patch/minor/major updates.
- [x] 4. Update the active `Main` GitHub ruleset to require the stable `Verify` check while preserving its merge-only rule, protections, and existing administrator and Uniquode App bypass actors. Confirm automatic merged-branch deletion remains enabled.
