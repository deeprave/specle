# Tasks: fix workflow Vale reporting

- [x] 1. Inspect the existing workflow reporting configuration.
  - [x] 1.1 Confirm the non-fork Vale job creates the standalone check through `github-pr-check` and that the fork job already uses annotations.
  - [x] 1.2 Confirm `test.yml` has no Vale job or Verify dependency to preserve.

- [x] 2. Route non-fork Vale output through Document validation annotations.
  - [x] 2.1 Change only the non-fork Vale reporter to `github-pr-annotations`.
  - [x] 2.2 Preserve the configured files, advisory alert level, and `fail_level: any` behaviour.

- [x] 3. Validate the declarative workflow directly.
  - [x] 3.1 Inspect the final workflow and run the repository's applicable quality and lifecycle checks. Do not add workflow tests.
