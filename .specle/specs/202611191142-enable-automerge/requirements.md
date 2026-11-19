# Requirements: enable Dependabot auto-merge

## Introduction

Specle's current test workflow runs the same quality checks in every Python-version matrix entry. Its resulting check names are version-specific, so they are unsuitable as a stable branch-rules requirement. The repository also has no Dependabot configuration to generate dependency-update pull requests. The Uniquode auto-merge App is installed and its client-ID variable and private-key secret are configured, but it has no workflow to use them.

## Glossary

- **Verify**: the stable aggregate GitHub Actions check that represents all required CI work.
- **Dependabot**: GitHub's dependency-update service, configured per package ecosystem.
- **Eligible update**: a Dependabot pull request that matches the project-defined auto-merge policy.
- **Auto-merge App**: the installed Uniquode GitHub App that can bypass the `main` ruleset to merge an eligible pull request.

## Requirements

### Requirement 1: Refactor CI verification jobs

**User Story:** As a maintainer, I want CI work separated into clearly named jobs, so that failures identify the failed quality concern and the aggregate gate remains stable.

#### Acceptance Criteria

1. THE test workflow SHALL continue to run on pull requests and pushes to `main`.
2. THE workflow SHALL run Ruff linting, Ruff formatting, type checking, and the pytest suite as independently named verification jobs.
3. THE pytest job SHALL run across Python 3.13, 3.14, and 3.15.
4. THE workflow SHALL preserve the project's existing `uv`-based dependency synchronisation and commands.

### Requirement 2: Publish a stable Verify gate

**User Story:** As a maintainer, I want one stable required check, so that branch protection remains correct when individual CI jobs change.

#### Acceptance Criteria

1. THE workflow SHALL provide a job named `Verify` that waits for every required verification job.
2. THE `Verify` job SHALL run even when an upstream job fails and SHALL fail unless every required job succeeds.
3. THE `Verify` check name SHALL not vary by Python version.
4. THE `main` ruleset SHALL require the `Verify` GitHub Actions check before a pull request can merge.

### Requirement 3: Configure Dependabot updates

**User Story:** As a maintainer, I want Dependabot to create dependency-update pull requests, so that eligible updates exist for the auto-merge workflow to evaluate.

#### Acceptance Criteria

1. THE repository SHALL provide `.github/dependabot.yml` with an update entry for the `uv` ecosystem at the repository root.
2. THE configuration SHALL provide an update entry for the GitHub Actions ecosystem at the repository root.
3. THE configuration SHALL use a documented update schedule and keep updates as ordinary pull requests for the existing verification and review workflow.
4. THE configuration SHALL not require a separate future feature before it can create update pull requests.

### Requirement 4: Enable Dependabot auto-merge

**User Story:** As a maintainer, I want eligible Dependabot updates merged by the installed App, so that safe routine dependency maintenance does not require manual delivery.

#### Acceptance Criteria

1. THE repository SHALL provide a dedicated auto-merge workflow that runs only for Dependabot pull requests and its explicit manual trigger, if one is provided.
2. THE workflow SHALL obtain an App token using `AUTOMERGE_APP_CLIENT_ID` and `AUTOMERGE_APP_PRIVATE_KEY` without logging either credential.
3. THE workflow SHALL enable merge-commit auto-merge only for updates that satisfy the documented eligibility policy.
4. THE workflow SHALL not merge a pull request from another author or an ineligible Dependabot update.
5. THE workflow SHALL rely on GitHub's required `Verify` check and the existing ruleset rather than bypassing verification.

### Requirement 5: Preserve manual delivery controls

**User Story:** As a maintainer, I want automation to coexist with normal pull-request delivery, so that it does not change the established human workflow.

#### Acceptance Criteria

1. THE repository SHALL continue to permit merge commits only and automatically delete merged pull-request branches.
2. THE `main` ruleset SHALL retain administrator and Uniquode auto-merge App bypass actors.
3. THE change SHALL not add a classic branch-protection rule that overlaps the existing ruleset.

## Non-Functional Requirements

- The workflow configuration must remain readable and use pinned or versioned actions according to the project's existing conventions.
- No secret value may be committed, printed, or copied into project documentation.
- The branch ruleset and workflow design must remain usable if the Python matrix changes later.
- Dependabot configuration is a direct prerequisite for the auto-merge workflow because it supplies the pull requests the workflow evaluates.
- This change is independent of queued schema-versioning work and must not rely on it.
