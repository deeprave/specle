# Summary: enable Dependabot auto-merge

## Outcome

Specle now provides a stable `Verify` CI gate, scheduled Dependabot updates, and policy-limited automated merging for eligible Dependabot pull requests.

## What changed

- CI now runs independently named lint, formatting, type-check, and Python-version test jobs, followed by the stable `Verify` aggregate check.
- The active `Main` ruleset requires `Verify`, while retaining merge-commit delivery, existing protections, and the trusted Uniquode App bypass.
- Dependabot is configured for weekly `uv` and GitHub Actions updates.
- The Dependabot auto-merge workflow uses the configured GitHub App, evaluates the agreed update policy, waits for the PR's live required checks, and only then invokes merge-commit auto-merge.
- The workflow uses the Dependabot-scoped App private key configuration and never checks out pull-request code.

## Evidence

- Local `ruff check`, `ruff format --check`, `ty check`, `pytest`, and `specle validate --verbose` passed.
- PR #10 completed all CI checks, including `Verify`, GitGuardian, and Sourcery review.
- The live ruleset requires `Verify`; repository auto-merge and automatic merged-branch deletion are enabled.

## Key decisions and limits

- `uv` patch and minor updates are eligible; GitHub Actions patch, minor, and major updates are eligible.
- The Uniquode App remains a trusted ruleset bypass actor, but its workflow waits for all required checks before invoking its merge operation.
- The workflow intentionally avoids speculative stale-update cleanup and treats GitHub-maintained Actions updates as within the agreed policy.

## Recommendation and follow-up

Allow Dependabot to create its first scheduled pull requests and observe the configured merge flow. Adjust the policy only if operational evidence shows a need.

## Copy-ready update

Enabled Dependabot automation with a stable required `Verify` CI gate. Eligible uv patch/minor and GitHub Actions updates can now be merged by the trusted Uniquode App only after the PR's required checks pass.
