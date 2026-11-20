# Requirements: validate distributable documentation

## Introduction

The Markdown blueprints distributed by Specle are both human guidance and operational instructions for agents. They, together with the repository's README and `docs/` documentation, need reliable source-only checks for Markdown structure, spelling, and selected prose conventions. Blueprint lifecycle logic additionally needs deterministic validation. A local agent skill will run these checks using tools already installed in the development environment. These checks must not duplicate or validate the installed `.agents/` copies, because those are generated from the source blueprint inventory.

## Glossary

- **Source documentation inventory**: the distributable Markdown source under `src/specle/blueprints/`, plus `README.md` and Markdown files under `docs/`.
- **Document validation**: the local agent skill introduced by this change.
- **Lifecycle contract**: machine-readable transition data used to validate the human-readable lifecycle guidance and skill ownership.
- **Advisory finding**: a reported issue that does not fail the workflow or block delivery.

## Requirements

### Requirement 1: Run source-documentation Markdown linting

**User Story:** As a maintainer, I want structural Markdown checks on the distributable blueprints, so that common formatting and syntax errors are caught before distribution.

#### Acceptance Criteria

1. THE repository SHALL configure `markdownlint-cli2` to check the source documentation inventory.
2. THE configuration SHALL include `README.md`, `docs/**/*.md`, and Markdown files under `src/specle/blueprints/`, while excluding installed `.agents/` copies and `.specle/` runtime artefacts.
3. THE configuration SHALL preserve unwrapped prose by disabling the line-length rule.
4. THE local document-validation skill SHALL run Markdownlint with the repository-owned configuration and report violations as failures.
5. THE Markdownlint configuration SHALL support intentional blueprint conventions, including YAML frontmatter, fenced examples, and unwrapped prose, while retaining checks that identify structural Markdown defects.

### Requirement 2: Run source-documentation spelling checks

**User Story:** As a maintainer, I want deterministic spelling checks for distributable Markdown, so that avoidable documentation errors are found without broad false-positive suppression.

#### Acceptance Criteria

1. THE repository SHALL configure CSpell to check the source documentation inventory.
2. THE CSpell configuration SHALL use `en-GB`, the software-terms dictionary, and a maintained allow-list for project names and accepted software-industry exceptions.
3. THE allow-list SHALL include only justified terms; it SHALL not disable broad categories of spelling checks.
4. THE local document-validation skill SHALL run CSpell with the repository-owned configuration and report violations as failures.
5. THE CSpell configuration SHALL recognise the project’s documented UK/AU spelling policy, established software terms, and justified project terminology without broadly disabling spelling checks.

### Requirement 3: Add advisory prose-style feedback

**User Story:** As a maintainer, I want useful prose-style feedback without premature delivery failures, so that the project can tune its writing policy from real findings.

#### Acceptance Criteria

1. THE repository SHALL provide a Vale configuration and narrow repository-owned initial style rules for the source documentation inventory.
2. THE local document-validation skill SHALL run Vale with the repository-owned configuration and present its findings.
3. Vale findings SHALL be advisory: they SHALL not make the local validation fail or block the main `Verify` gate.
4. THE initial rules SHALL document their intent and SHALL not silently adopt a broad external editorial style guide as project policy.
5. THE Vale configuration and rules SHALL fit the concise instructional Markdown used by skills and policies, rather than imposing generic prose conventions that conflict with established repository style.

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

### Requirement 6: Deliver non-required pull-request validation

**User Story:** As a maintainer, I want the proven local documentation checks to run on pull requests without becoming a dependency of the main quality gate.

#### Acceptance Criteria

1. THE change SHALL provide a dedicated GitHub Actions document-validation workflow that runs on pull-request events only.
2. THE workflow SHALL NOT be a dependency of, or a required check within, the main `Verify` aggregate or repository rules.
3. THE workflow SHALL use the source documentation inventory as its sole documentation input unless a later explicit requirement expands its scope.
4. Markdownlint, CSpell, and lifecycle violations SHALL fail their workflow steps with actionable diagnostics.
5. Vale SHALL display advisory findings and return a non-zero result for suggestions, while its workflow check remains non-required by repository rules.
6. Every validation step SHALL be read-only and SHALL NOT format, fix, or otherwise modify documentation.

### Requirement 7: Support local document-validation feedback

**User Story:** As a maintainer, I want to run configured document checks locally through an agent skill, so that I can tune rules and fix findings before considering CI adoption.

#### Acceptance Criteria

1. EACH document checker SHALL use repository-owned configuration and a documented local invocation.
2. THE local invocation SHALL use the same source-documentation scope and configuration as any later corresponding CI check.
3. EACH checker SHALL support selected-file invocation while a maintainer tunes dictionaries, exclusions, or style rules.
4. The local skill and CI workflow SHALL use the same configuration, source-documentation scope, rules, exclusions, and paths. CI tool setup SHALL not introduce a project dependency.
5. THE change SHALL not require Hypothesis or an AI service for local document validation.

### Requirement 8: Tune configurations against the source inventory

**User Story:** As a maintainer, I want validation configuration that reflects the actual blueprint package, so that local findings identify genuine documentation defects rather than routine features of agent skills and project documentation.

#### Acceptance Criteria

1. THE change SHALL provide repository-owned configuration for Markdownlint, CSpell, and Vale.
2. THE configuration SHALL be developed and checked against representative skills, policies, README content, and documentation under `docs/`.
3. THE configuration SHALL preserve established intentional conventions, including frontmatter, code examples, unwrapped prose, UK/AU spelling, and accepted software terminology.
4. THE configuration SHALL not suppress broad categories of structural, spelling, or prose checks merely to make the current inventory pass.
5. THE skill or its accompanying guidance SHALL identify how maintainers can tune each configuration when a finding reveals a genuine project convention.
6. THE change SHALL use shared configuration by default. It MAY add documented scope-specific configuration only where blueprint and repository-documentation conventions genuinely differ.

### Requirement 9: Check changed source documentation before commit

**User Story:** As a maintainer, I want quick validation of staged source documentation before a commit, so that straightforward structural and spelling defects are caught before the full pull-request workflow runs.

#### Acceptance Criteria

1. THE repository SHALL add maintained pre-commit hooks for Markdownlint, CSpell, and Vale that receive staged files and restrict their scope to the source documentation inventory.
2. THE hooks SHALL reuse the repository-owned configuration already used by local full-inventory validation and CI.
3. Markdownlint and CSpell hook failures SHALL block a commit. Vale findings SHALL remain advisory locally and SHALL not block a commit.
4. THE repository SHALL add a local `specle validate` pre-commit hook that runs without file arguments whenever hooks execute, because lifecycle validation is inventory-wide.
5. THE hooks SHALL be read-only and SHALL NOT format, fix, or otherwise modify staged documentation.
6. THE pre-commit configuration SHALL use maintained upstream hooks where available and a narrow local system hook only for the repository's own `specle validate` command.

## Non-Functional Requirements

- The local skill, CI workflow, and configurations must remain understandable to maintainers.
- No check may require an external AI service or transmit document content to one.
- The lifecycle validator must be deterministic and covered by focused tests.
- This change is independent of `enable-automerge`, versioned JSON schemas, and all other queued work.
