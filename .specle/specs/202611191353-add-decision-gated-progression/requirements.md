# Requirements: add decision-gated progression

## Introduction

Specle lifecycle skills are individually useful, but successful local stages often need no human decision. A reusable policy must allow projects to choose automatic continuation while preserving explicit intervention where judgement, remediation, or external authority is required.

## Glossary

- **Progression policy**: project guidance that selects how an agent continues after a lifecycle skill completes.
- **Manual mode**: the agent reports the next skill and waits for the user.
- **Decision-gated mode**: the agent invokes the unambiguous next local skill until it reaches a defined decision boundary.
- **Decision boundary**: a point requiring user judgement, remediation direction, or explicit authority.

## Requirements

### Requirement 1: Define portable progression policy

**User Story:** As a project owner, I want to choose whether successful local workflow stages continue automatically, so that Specle matches my preferred level of interaction.

#### Acceptance Criteria

1. THE reusable steering inventory SHALL define `manual` and `decision-gated` progression modes in an automation policy document.
2. IF project automation guidance is missing or does not establish a mode, THEN agents SHALL use manual mode.
3. IN manual mode, a completed lifecycle skill SHALL report its next step and wait for user direction.
4. IN decision-gated mode, an agent SHALL invoke the unambiguous next local lifecycle skill after a successful transition, preserving every selected skill's full instructions and state update.
5. THE policy SHALL not permit an agent to skip estimate, design, tasks, build, verify, review, triage, resolve, commit, or complete merely because continuation is enabled.
6. THE policy SHALL not authorise external writes; delivery authority remains governed exclusively by project delivery policy and explicit user authorisation.

### Requirement 2: Define decision-gated boundaries

**User Story:** As a developer, I want automation to stop only when my input can materially affect the outcome, so that I am not interrupted for routine successful work.

#### Acceptance Criteria

1. IN decision-gated mode, successful local normal-work stages SHALL continue through estimate, design, tasks, build, verify, and review when no material decision is identified.
2. IF requirements are incomplete, a material design choice lacks user direction, or another skill identifies an unresolved decision, THEN the agent SHALL stop, explain the decision, and wait for the user.
3. IF verification fails, THEN the agent SHALL stop with the concrete failures and required remediation; it SHALL not invent a fix or automatically revise the specification.
4. IF review approves, THEN the agent SHALL set the target to `approved` and stop to request authorisation for `commit`.
5. IF review records findings, THEN the agent SHALL invoke triage before waiting for user decisions.
6. A direct invocation of a lifecycle skill SHALL retain its existing preconditions and guards; automatic progression may invoke a prerequisite skill in sequence but SHALL not bypass that guard.

### Requirement 3: Make triage completion explicit

**User Story:** As a reviewer, I want to see every decision together before implementation resumes, so that I can revise related decisions into one coherent resolution.

#### Acceptance Criteria

1. AFTER every current finding has a recorded decision, triage SHALL persist those decisions and their routes, set the target to `triaged`, and present a complete decision-and-route summary.
2. THE summary SHALL include every current finding, its severity, decision, rationale when recorded, and proposed route.
3. TRIAGE SHALL stop after presenting the summary, even in decision-gated mode.
4. THE agent SHALL wait for the user to request `resolve` or revise one or more triage decisions.
5. `resolve` remains the only workflow that dispatches accepted review decisions; it may resume decision-gated continuation after its own explicit invocation and successful routing.

### Requirement 4: Select policy through onboarding

**User Story:** As a project owner, I want onboarding to establish progression behaviour as a local policy, so that it is intentional and visible without repeating it in AGENTS guidance.

#### Acceptance Criteria

1. ONBOARD SHALL inventory `automation.md` as a required project guidance document.
2. ONBOARD SHALL ask one focused question to select manual or decision-gated progression and record any supported local exceptions.
3. ONBOARD SHALL create or refresh `.agents/project/automation.md` only after it has collected the user's answer with the other project guidance.
4. THE project README SHALL map `automation.md` as authoritative project guidance.
5. THE root and reusable AGENTS documents SHALL not need a project-specific progression-policy instruction; lifecycle-owning skills SHALL consult the project automation policy directly.

### Requirement 5: Remove the implement shortcut

**User Story:** As a user, I want one consistent continuation model rather than a special orchestration skill, so that workflow behaviour does not depend on the command I happened to start.

#### Acceptance Criteria

1. THE managed blueprint and active inventories SHALL remove the `implement` skill and its generated index entry.
2. THE reusable workflow guidance SHALL remove `implement` as a normal workflow option while preserving its ordinary lifecycle sequence.
3. FOR planned queued abbreviated work, lifecycle guidance and `prepare` SHALL set the next owning skill to `bugfix` or `refactor`, rather than `implement`.
4. `bugfix` and `refactor` SHALL retain the ability to execute a named planned abbreviated target without replacing an unrelated active issue.
5. THE migration SHALL not change normal-spec, review, verification, delivery, or external-write semantics beyond the selected continuation policy.

## Non-Functional Requirements

- Progression behaviour must be deterministic from recorded state, the project automation policy, and the selected skill's documented outcome.
- Every automatic stage must report concise progress and name the specific decision boundary when it stops.
- The policy remains agent-client agnostic and must work without a CLI, network access, or an AI service beyond the executing agent.
- This change is independent of the queued StrictYAML, lifecycle-validator, document-validation, auto-merge, and JSON-schema-versioning changes.
