# Requirements: address security findings

## Introduction

The 21 November 2026 security assessment in `.specle/report.json` informed this specification. This change addresses the two resulting requirements while preserving deliberate project decisions: Dependabot may auto-merge its configured eligible updates only after required checks pass, the trusted Uniquode App may bypass the `main` ruleset for that purpose, and users may choose symlinked installation layouts.

The assessment’s remaining proposals are intentionally out of scope: install-layout symlink restrictions, changelog publication changes, imported-issue restrictions, and a dependency scan gate are not required. Blueprint validation and installed-inventory drift detection are independently specified by `support-blueprint-validate`.

## Requirements

### Requirement 1: Defer auto-merge credential use

**User Story:** As a repository owner, I want the auto-merge App credential used only for the final privileged operation, so ordinary eligibility and CI checks do not receive the credential capable of bypassing delivery rules.

#### Acceptance Criteria

1. Dependabot metadata lookup and required-check polling SHALL use the ordinary workflow token, without creating a GitHub App token.
2. The workflow SHALL create the GitHub App token only after an eligible update's required checks have passed, immediately before enabling the configured auto-merge.
3. The workflow SHALL retain its Dependabot-only trigger, shall not check out pull-request code, and shall preserve its required-check gate.
4. The workflow SHALL retain the established eligibility policy: uv patch/minor updates and GitHub Actions patch/minor/major updates.
5. The change SHALL not remove the trusted App's ruleset-bypass capability required for an eligible passing pull request to merge.

### Requirement 2: Read only regular validation inputs

**User Story:** As a developer, I want validation to reject a non-regular input before reading it, so a special file cannot block validation while intentional symlinked files remain supported.

#### Acceptance Criteria

1. Before reading a Specle validation input, the validator SHALL confirm that its resolved target is a regular file.
2. A symlink that resolves to a regular file SHALL remain valid input.
3. A non-regular resolved target, including a device or directory, SHALL fail validation with a clear path-specific diagnostic before its content is read.
4. The check SHALL apply to every file read by installed-target validation, including skill files, generated indexes, runtime selectors, and status records.
5. Installed-skill discovery SHALL ignore a directory with no `SKILL.md`, but SHALL fail validation when an existing or broken-link `SKILL.md` does not resolve to a regular file.

## Non-Functional Requirements

- The security hardening must preserve the project’s existing delivery model and explicit auto-merge policy.
- Validation must not reject intentional symlinked file layouts solely because they use symlinks.
