# Requirements: enhance define skill

## Introduction

`define` currently creates structurally valid change artifacts, but its guidance does not ask an agent to investigate the problem, distinguish known facts from assumptions, or actively resolve material uncertainty. That can leave a change technically formatted yet insufficiently understood for design and implementation.

## Glossary

- **Definition:** the planning activity that creates an unselected normal change and captures why it is needed, what outcome it requires, and its relevant boundaries.
- **Relevant evidence:** project guidance, source code, documentation, tests, current or archived changes, and user-provided material that can clarify a proposed change.
- **Material uncertainty:** an unanswered question whose answer would alter scope, observable behaviour, compatibility, acceptance criteria, or the appropriate change type.
- **Assumption:** a minor inferred detail that does not materially alter the requested outcome and is recorded as such.

## Requirements

### Requirement 1: Investigate before defining a change

**User Story:** As a developer, I want an agent to understand the surrounding project before it defines work, so the resulting change reflects the actual system rather than a superficial restatement of my request.

#### Acceptance Criteria

1. Before writing a normal change, `define` SHALL examine the applicable project guidance and relevant evidence in the codebase and documentation.
2. `define` SHALL inspect relevant active and archived changes before deciding whether work is already covered, related, or genuinely independent.
3. `define` SHALL use the evidence it finds to distinguish current behaviour, requested outcome, affected boundaries, and implementation details that remain undecided.
4. `define` SHALL not perform implementation, select the change, or begin later planning stages while gathering this evidence.

### Requirement 2: Elicit material uncertainty

**User Story:** As a developer, I want the agent to ask useful questions when essential information is missing, so a defined change does not conceal consequential guesses.

#### Acceptance Criteria

1. If material uncertainty remains after investigation, `define` SHALL ask the user focused questions before creating the change artifacts.
2. Questions SHALL explain the decision they unblock and offer an evidence-based default where one is available.
3. `define` MAY infer minor details that do not materially change the requested outcome, but SHALL record those details as assumptions or boundaries in the artifacts.
4. `define` SHALL not ask for information that can be established from available project evidence.

### Requirement 3: Capture a substantive change definition

**User Story:** As a developer, I want change artifacts that clearly communicate why the work matters and what it changes, so later design, tasks, implementation, and review begin from a sound contract.

#### Acceptance Criteria

1. `requirements.md` SHALL explain the problem or opportunity, why the work is needed now, and the desired observable outcome.
2. `requirements.md` SHALL state specific capabilities or behaviour to add, modify, or remove; identify affected code, interfaces, configuration, dependencies, or systems when known; and clearly mark compatibility or breaking impact when applicable.
3. `requirements.md` SHALL state explicit boundaries and non-goals, including work deliberately left to later changes.
4. `requirements.md` SHALL provide clear, testable acceptance criteria that later verification can use as the conformance checklist.
5. `spec.md` SHALL remain a concise, human-readable summary of the motivation, intended outcome, key scope, impact, unresolved questions or recorded assumptions, and the evidence expected to verify the change.
6. The skill SHALL prioritise useful content over a prescribed proposal format or semantic heading names.

### Requirement 4: Preserve clear change relationships

**User Story:** As a developer, I want related work made visible without creating fictional ordering constraints, so each queued change remains independently understandable and executable.

#### Acceptance Criteria

1. `define` SHALL record a dependency only when the user explicitly requests one or an already-implemented technical prerequisite makes it necessary.
2. Conceptual overlap, anticipated implementation order, and future functionality SHALL NOT create a dependency by themselves.
3. When existing work partially addresses the request, the definition SHALL explain the boundary between the changes rather than silently absorbing or constraining either change.

### Requirement 5: Preserve the definition lifecycle boundary

**User Story:** As a developer, I want to define several possible changes without starting them, so ideation and execution remain separate.

#### Acceptance Criteria

1. `define` SHALL create a unique normal change under `.specle/changes/` with `requirements.md`, `spec.md`, and a versioned `status.json` in the `defined` state.
2. `define` SHALL not write `.specle/current-change`, activate the new change, or invoke estimate, design, tasks, build, verification, or review.
3. The blueprint and installed `define` skill SHALL contain the same definition guidance, and the installed skill index SHALL be regenerated when its metadata or content changes.

### Requirement 6: Report a completed definition

**User Story:** As a developer, I want a concise summary after a proposed change is fully defined, so I can assess its intent without being forced to continue that work.

#### Acceptance Criteria

1. After investigation and draft definition work, `define` SHALL present a concise summary of the problem, intended outcome, scope, boundaries, assumptions or unresolved material questions, and verification direction.
2. `define` SHALL create its durable change record without requiring confirmation and SHALL not select, activate, or otherwise progress it.
3. If a proposed slug is already used, `define` SHALL identify the conflicting change and stop before creating a record, so the user can rename the proposed change or investigate whether the existing work already covers it.

### Requirement 7: Confirm before build starts

**User Story:** As a developer, I want the current specification restated immediately before implementation starts, so I can confirm alignment before spending time and tokens on a build.

#### Acceptance Criteria

1. Before a `planned` normal change transitions to `building`, `build` SHALL present a concise alignment summary derived from its current specification, including intended outcome, scope and non-goals, acceptance direction, planned tasks, and material assumptions or limits.
2. `build` SHALL require explicit user confirmation before its first implementation action, including when decision-gated progression is enabled.
3. `activate` and `tasks` SHALL continue their ordinary preparation and progression behaviour without introducing a confirmation pause.
4. Decision-gated automation policy SHALL name the pre-build alignment summary and confirmation as a mandatory stop.
5. The blueprint and installed copies of every affected managed skill and lifecycle policy SHALL remain aligned, the human lifecycle reference SHALL describe the final boundary, and the installed skill index SHALL be regenerated.

## Non-Functional Requirements

- The enhanced skill must remain reusable across project types and must derive project-specific facts from the local guidance and evidence it reads.
- The skill must use concise UK/AU English in its own human-facing guidance.
- This change improves the existing `define`, `activate`, and `tasks` guidance only; it does not add a new skill, alter the durable change schema, or introduce a separate proposal-file format.
