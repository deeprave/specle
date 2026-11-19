# Requirements: validate distributable documentation

## Introduction

The Markdown blueprints distributed by Specle are both human guidance and operational instructions for agents. They need reliable source-only checks for Markdown structure, spelling, selected prose conventions, and the lifecycle logic that connects skills and state. These checks must not duplicate or validate the installed `.agents/` copies, because those are generated from the source blueprint inventory.

## Glossary

- **Blueprint package**: the distributable Markdown source under `src/specle/blueprints/`.
- **Document validation**: the separate pull-request workflow introduced by this change.
- **Lifecycle contract**: machine-readable transition data used to validate the human-readable lifecycle guidance and skill ownership.
- **Advisory finding**: a reported issue that does not fail the workflow or block delivery.

## Requirements

### Requirement 1: Run source-only Markdown linting

**User Story:** As a maintainer, I want structural Markdown checks on the distributable blueprints, so that common formatting and syntax errors are caught before distribution.

#### Acceptance Criteria

1. THE repository SHALL configure `markdownlint-cli2` to check Markdown files under `src/specle/blueprints/` only.
2. THE configuration SHALL exclude installed `.agents/` copies and `.specle/` runtime artefacts.
3. THE configuration SHALL preserve unwrapped prose by disabling the line-length rule.
4. THE document-validation workflow SHALL run the maintained Markdownlint action at a pinned revision and report violations as failures.

### Requirement 2: Run source-only spelling checks

**User Story:** As a maintainer, I want deterministic spelling checks for distributable Markdown, so that avoidable documentation errors are found without broad false-positive suppression.

#### Acceptance Criteria

1. THE repository SHALL configure CSpell to check Markdown files under `src/specle/blueprints/` only.
2. THE CSpell configuration SHALL use `en-GB`, the software-terms dictionary, and a maintained allow-list for project names and accepted software-industry exceptions.
3. THE allow-list SHALL include only justified terms; it SHALL not disable broad categories of spelling checks.
4. THE document-validation workflow SHALL run the maintained CSpell action at a pinned revision and report violations as failures.

### Requirement 3: Add advisory prose-style feedback

**User Story:** As a maintainer, I want useful prose-style feedback without premature delivery failures, so that the project can tune its writing policy from real findings.

#### Acceptance Criteria

1. THE repository SHALL provide a Vale configuration and narrow repository-owned initial style rules for the blueprint package only.
2. THE document-validation workflow SHALL run the maintained Vale action at a pinned revision and publish findings as pull-request annotations.
3. THE Vale job SHALL be advisory: it SHALL not fail its workflow or block the main `Verify` gate.
4. THE initial rules SHALL document their intent and SHALL not silently adopt a broad external editorial style guide as project policy.

### Requirement 4: Validate lifecycle logic deterministically

**User Story:** As a maintainer, I want executable checks for documented lifecycle logic, so that dead ends and contradictory workflow ownership are caught without relying on AI interpretation.

#### Acceptance Criteria

1. THE repository SHALL define a machine-readable lifecycle contract that complements, but does not replace, the human-readable lifecycle steering.
2. THE validator SHALL confirm every non-terminal status has at least one valid outgoing transition and can reach a terminal status.
3. THE validator SHALL confirm each transition has an owning skill, each documented `next` workflow names an installed Specle skill, and each terminal status has no required next workflow.
4. THE validator SHALL detect invalid transitions, unreachable states, and state/skill ownership contradictions with actionable diagnostics.
5. THE lifecycle contract and validation tests SHALL be maintained with the blueprint source rather than installed `.agents/` copies.

### Requirement 5: Record project language guidance

**User Story:** As a project maintainer, I want human language and spelling conventions in the project overlay, so that reusable skills can follow local communication conventions without requiring an `AGENTS.md` instruction.

#### Acceptance Criteria

1. THE project overlay SHALL include `language.md`, mapped from its README, to record the project's human language, spelling locale, and accepted terminology exceptions.
2. THE `onboard` blueprint SHALL inventory `language.md` as a required project document and ask one focused question at a time when its language, spelling locale, or exceptions are missing or incomplete.
3. THE onboarding process SHALL record only user-confirmed or source-supported language guidance and SHALL state when a preference is not established.
4. THE distribution SHALL not require a project to state language or spelling conventions in `AGENTS.md`.
5. THIS repository's `language.md` SHALL record UK/AU spelling with its accepted software-industry exceptions, including `license`, `artifact`, and `color`.

### Requirement 6: Isolate document-validation delivery

**User Story:** As a maintainer, I want to tune documentation checks independently from application delivery, so that emerging editorial rules do not destabilise the main quality gate.

#### Acceptance Criteria

1. THE repository SHALL provide a dedicated document-validation workflow that runs on pull requests only.
2. THE workflow SHALL not be a dependency of, or a required check within, the main `Verify` aggregate.
3. THE workflow SHALL use the blueprint package as its sole documentation input unless a later explicit requirement expands its scope.
4. THE structural, spelling, and lifecycle jobs SHALL fail their own workflow on violations; only the Vale job remains advisory.

### Requirement 7: Support local document-validation feedback

**User Story:** As a maintainer, I want to run the configured document checks locally before opening a pull request, so that I can tune rules and fix findings with the same behaviour CI will use.

#### Acceptance Criteria

1. EACH document checker SHALL use repository-owned configuration and a documented local invocation.
2. THE local invocation SHALL use the same blueprint-only scope and configuration as its corresponding CI check.
3. EACH checker SHALL support selected-file invocation while a maintainer tunes dictionaries, exclusions, or style rules.
4. THE CI workflow SHALL invoke the same configured behaviour rather than defining CI-only rules, exclusions, or paths.
5. THE change SHALL not require Hypothesis or an AI service for local document validation.

## Non-Functional Requirements

- The workflow and configurations must use pinned action revisions and remain understandable to maintainers.
- No check may require an external AI service or transmit document content to one.
- The lifecycle validator must be deterministic and covered by focused tests.
- This change is independent of `enable-automerge`, versioned JSON schemas, and all other queued work.
