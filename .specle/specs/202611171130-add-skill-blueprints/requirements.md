# Requirements: add skill blueprints

## Introduction

Specle distributes reusable skill blueprints from `src/specle/skills/`, while a target repository uses an active subset in `.agents/skills/`. Installing a skill must be deliberate: its direct skill dependencies need to be understood and available before its blueprint becomes active.

## Glossary

- **Blueprint**: the canonical `SKILL.md` stored in `src/specle/skills/<skill>/`.
- **Active skill**: an installed copy at `.agents/skills/<skill>/SKILL.md`.
- **Direct dependency**: another skill that the blueprint requires to perform its own workflow, rather than an optional next step.

## Requirements

### Requirement 1: Treat source blueprints as canonical

**User Story:** As a developer, I want each reusable skill defined once, so that active installations can be reviewed against a clear source of truth.

#### Acceptance Criteria

1. THE project SHALL keep each reusable skill blueprint at `src/specle/skills/<skill-name>/SKILL.md`.
2. THE project SHALL treat the blueprint as the canonical source for the active `.agents/skills/` copy.
3. THE project SHALL preserve project-specific guidance outside the skill blueprint in `.agents/project/`.

### Requirement 2: Assess dependencies before installation

**User Story:** As a developer, I want to know whether a skill depends on another installed skill before activating it.

#### Acceptance Criteria

1. BEFORE installing a blueprint, THE workflow SHALL identify its direct skill dependencies.
2. THE workflow SHALL distinguish required dependencies from optional next-step skills.
3. IF a required dependency is absent from `.agents/skills/`, THEN the workflow SHALL install or otherwise resolve it before activating the dependent skill.

### Requirement 3: Install reviewed blueprints into the active inventory

**User Story:** As a developer, I want approved skills available to agents working in this repository.

#### Acceptance Criteria

1. WHEN a blueprint and its direct dependencies are ready, THE workflow SHALL copy it to `.agents/skills/<skill-name>/SKILL.md`.
2. THE active copy SHALL match the reviewed source blueprint.
3. THE workflow SHALL not change unrelated active skills during an installation.

### Requirement 4: Identify and group Specle skills

**User Story:** As a developer, I want Specle skills distinguishable and grouped without separate ownership and presentation metadata, so that installation, updates, and inventory never overwrite or display skills owned by another tool or the user.

#### Acceptance Criteria

1. THE project SHALL declare a non-empty `specle_group` in the frontmatter of every Specle skill blueprint.
2. THE workflow SHALL treat an active skill marked with `specle_group` as eligible for Specle-managed installation and updates.
3. THE workflow SHALL not overwrite an installed skill without `specle_group`.

### Requirement 5: Classify work items

**User Story:** As a developer, I want each work item classified independently of its lifecycle status, so that I can distinguish regular changes, bugfixes, documentation work, and releases.

#### Acceptance Criteria

1. THE `.specle/context.json` schema SHALL store a `kind` for `current_spec`, queued specs, and recent specs.
2. THE workflow SHALL recognise `change`, `bugfix`, `refactor`, `docs`, and `release` as initial kinds.
3. THE workflow SHALL preserve and report an unknown non-empty kebab-case kind rather than rejecting it.
4. Existing context records without `kind` SHALL be treated as `change`.
5. THE status inventory SHALL display each work item's kind separately from its lifecycle status.

### Requirement 6: Verify abbreviated work

**User Story:** As a developer, I want bounded bugfix and refactor workflows to be verifiable without displacing unrelated active feature work.

#### Acceptance Criteria

1. THE `bugfix` and `refactor` workflows SHALL create a timestamped spec directory containing a structured `spec.md` and `tasks.md`, without requiring `requirements.md` or `design.md`.
2. THE workflows SHALL preserve the active current issue and track their own matching queued record with the appropriate `kind`.
3. THE `verify` workflow SHALL verify an active normal spec against `requirements.md` and SHALL verify a named queued abbreviated spec against its documented abbreviated-work criteria.
4. WHEN verifying a named queued abbreviated spec, THE `verify` workflow SHALL update only that matching queued record and SHALL not replace or alter the active current issue.
5. THE workflow SHALL provide a `prepare` entry point that creates an abbreviated bugfix or refactor's `spec.md` and `tasks.md`, leaves its queued record `planned` with `next: "implement"`, and performs no implementation work.

### Requirement 7: Implement existing abbreviated work

**User Story:** As a developer, I want `implement` to advance an existing bugfix or refactor without treating it as a normal active feature.

#### Acceptance Criteria

1. THE `implement` workflow SHALL identify whether its target is a normal active spec or a named queued abbreviated spec by its recorded `kind`.
2. WHEN the target kind is `bugfix` or `refactor`, THE workflow SHALL reuse its existing abbreviated artefacts, delegate execution to the matching workflow, and preserve the active current issue.
3. THE workflow SHALL not apply the normal estimate, design, tasks, or build stages to a `bugfix` or `refactor`.
4. WHEN abbreviated tasks are complete, THE workflow SHALL stop and report `verify` as the next step.
5. THE `implement` and `verify` workflows SHALL require an explicitly named queued target for abbreviated work and SHALL not select one implicitly.

### Requirement 8: Show and review concurrent work correctly

**User Story:** As a developer, I want active and sidecar work to remain visible and independently reviewable.

#### Acceptance Criteria

1. THE status inventory SHALL display a queued item's explicit `next` skill when one is recorded.
2. THE `review` workflow SHALL stop when its target has not passed verification and direct the user to `verify`.
3. THE `review` workflow SHALL review an explicitly named verified queued bugfix or refactor without changing the active current issue.
4. WHEN such a review passes, THE workflow SHALL move only that record from `queued_specs` to `recent_specs` as `complete`.
5. WHEN such a review has findings, THE workflow SHALL keep only that queued record at `review-findings` with `revise` as the next step.

### Requirement 9: Plan against existing changes

**User Story:** As a developer, I want implementation tasks to account for relevant recent work, so that the plan is neither redundant nor detached from the actual codebase.

#### Acceptance Criteria

1. BEFORE generating or reconciling a normal spec's task plan, THE `tasks` workflow SHALL inspect relevant staged, unstaged, and recent committed changes.
2. THE workflow SHALL account for relevant existing implementation in the plan while ignoring unrelated working-tree changes.
3. THE workflow SHALL not mark a task complete based only on existing code or a diff; task completion remains owned by `build` and verified independently.

### Requirement 10: Integrate external work sources and a delivery destination

**User Story:** As a developer, I want to import work from several external sources while optionally publishing completed-work information to one destination.

#### Acceptance Criteria

1. THE `track` workflow SHALL read project guidance that separately configures zero or more work sources and zero or one delivery destination.
2. THE workflow SHALL import explicitly named source items into a spec and check linked sources for updates without changing the spec until the user confirms a proposed update.
3. THE workflow SHALL record source links and the optional destination link in `.specle/specs/<spec>/tracker-links.json`.
4. THE workflow SHALL publish only to the configured destination and only with explicit user authorisation.
5. THE project tracking guidance SHALL configure GitHub Issues as a source of user reports, configure no destination, and require a pull request resolving a linked issue to use `Close #<issue>`.
6. THE workflow SHALL default to the active normal spec and SHALL accept a queued bugfix or refactor only when the user explicitly names it.

### Requirement 11: Revise normal and abbreviated work in place

**User Story:** As a developer, I want accepted feedback to revise the affected work item without replacing its history or disrupting unrelated active work.

#### Acceptance Criteria

1. THE `revise` workflow SHALL revise an active normal spec's affected requirements, design, and tasks in place, preserving valid completed work.
2. THE workflow SHALL revise a queued bugfix or refactor only when the user explicitly names it, updating only its abbreviated `spec.md` and `tasks.md`.
3. AFTER revising a queued abbreviated item, THE workflow SHALL preserve the active current issue and set only that record to `planned` with `next: "implement"`.
4. THE workflow SHALL not implement code, tests, or task steps.

### Requirement 12: Track active investigations

**User Story:** As a developer, I want a bounded investigation to be visible as active work without masquerading as an implementation spec.

#### Acceptance Criteria

1. THE workflow SHALL recognise `spike` as a work kind with the lifecycle `defined` → `spiking` → `complete`.
2. THE `spike` workflow SHALL use the normal current-issue path and SHALL not displace unfinished active work without user intent.
3. THE workflow SHALL store the investigation in `findings.json`, including its question, effort budget, scope, findings, recommendations, risks, and optional outcome-spec reference.
4. THE effort budget SHALL use S/M/L/XL as a bounded research effort rather than a delivery estimate.
5. THE workflow SHALL not implement production code or enter verification or review.

### Requirement 13: Establish project review guidance

**User Story:** As a developer, I want review and triage preferences recorded as project guidance, so that agents present and address findings consistently.

#### Acceptance Criteria

1. THE project-overlay inventory SHALL include `.agents/project/review.md`.
2. THE onboarding workflow SHALL ask for review presentation mode and automated-decision policy when review guidance is missing or incomplete.
3. THE project README SHALL identify `review.md` as authoritative project guidance.
4. THE reusable P1–P6 review severity taxonomy SHALL live in `.agents/steering/review.md`.
5. THE reusable review steering SHALL define default one-at-a-time, batch, and automatic presentation layouts; a project MAY override them in project review guidance.

### Requirement 14: Triage review findings

**User Story:** As a developer, I want feedback from internal and external review sources consolidated into durable, prioritised decisions before any fixes are addressed.

#### Acceptance Criteria

1. THE `triage` workflow SHALL record each target spec's review sources and consolidated findings in `review-findings.json`.
2. THE record SHALL retain stable source identities and revisions so unchanged external review items are not re-recorded.
3. THE workflow SHALL consolidate clear duplicates while retaining source references and SHALL present uncertain duplicates for user judgement.
4. THE workflow SHALL classify actionable findings using the steering P1–P6 taxonomy and present them according to project review guidance.
5. THE workflow SHALL record decisions and routes without implementing code, tests, or task steps.
6. THE lifecycle SHALL distinguish raw `review-findings` awaiting triage from `triaged` findings ready for later addressing.

### Requirement 15: Resolve triaged findings

**User Story:** As a developer, I want accepted triage decisions dispatched to the appropriate follow-up workflows without re-triaging or silently implementing unrelated work.

#### Acceptance Criteria

1. THE `resolve` workflow SHALL operate only on a `triaged` target whose current findings all have decisions.
2. THE workflow SHALL group accepted findings in P1–P6 order and dispatch their recorded routes.
3. THE workflow SHALL support routes to `revise`, prepared or directly executed `bugfix` and `refactor` work, a new `spec`, and no-action dispositions.
4. THE workflow SHALL default new bugfix and refactor work to preparation; direct execution requires an explicit decision or automatic-policy authorisation.
5. THE workflow SHALL record each dispatch result in `review-findings.json` and SHALL not re-triage findings, implement code itself, or alter external review sources.
6. THE workflow SHALL leave originating lifecycle changes to the downstream owning workflow and SHALL not mark the target complete solely because it dispatched accepted decisions.
7. WHEN every current finding has a terminal no-action disposition (`decline`, `skip`, `defer`, or `duplicate`), THE workflow SHALL record the review as resolved and complete the selected target. An active normal target SHALL become `complete`; a named queued abbreviated target SHALL move to `recent_specs` as `complete` without changing the active current issue.
8. ON a later invocation, THE workflow SHALL inspect recorded accepted-action dispatches and their resulting work items. WHEN every current finding is terminally no-action or has a completed dispatched follow-up, THE workflow SHALL record the review as resolved and complete the selected target without redispatching completed work.
9. WHEN an accepted `spec` route creates an independent normal spec from the active normal target, THE workflow SHALL defer that terminal hand-off until every other current finding is terminally no-action or has a completed follow-up. It SHALL then record the hand-off, complete the originating current spec, and only then initialise the new spec as the current work. The origin SHALL not wait for the independent spec to complete.

### Requirement 16: Summarise completed work

**User Story:** As a developer, I want a human-facing account of completed work that I can share or adapt for stakeholders without confusing it with agent-managed findings or publishing it automatically.

#### Acceptance Criteria

1. THE project SHALL provide a `summary` skill in place of the former `demo` skill.
2. THE skill SHALL select completed active work by default and require an explicit name for any completed non-active work item; it SHALL support normal changes, bugfixes, refactors, and spikes.
3. THE skill SHALL stop without writing a summary unless the selected work item has `status: "complete"`.
4. THE skill SHALL write a standalone human-facing `summary.md` in the selected spec directory, including outcome, evidenced results, decisions or limits, follow-up recommendations, and a concise copy-ready update.
5. FOR a spike, THE summary SHALL foreground its recorded recommendation and optional outcome-spec reference; `findings.json` remains the machine-readable investigation record.
6. THE skill SHALL not alter lifecycle state or publish to an external system.

### Requirement 17: Name the Specle workflow guide

**User Story:** As a developer, I want the skill that introduces this workflow to carry the product name, so that it is distinctive and easy to invoke among other installed skills.

#### Acceptance Criteria

1. THE project SHALL rename the source-only `about` blueprint to `specle`.
2. THE source directory name and frontmatter `name` SHALL both be `specle`.
3. THE skill SHALL describe the installed Specle workflow and inventory rather than presenting itself as a generic about skill.

### Requirement 18: Group the Specle skill inventory

**User Story:** As a developer, I want each Specle skill to identify itself and its group with one marker, so that the Specle guide can present a durable, generated workflow inventory without hard-coded skill names.

#### Acceptance Criteria

1. EVERY Specle skill blueprint SHALL declare a non-empty `specle_group` frontmatter field.
2. EVERY installed Specle skill SHALL retain its blueprint's `specle_group` value.
3. THE generated Specle inventory SHALL include only installed skills marked with `specle_group`.
4. THE `specle` skill SHALL group that inventory from `specle_group`, order defined groups consistently, and report an unrecognised group without omitting a marked skill.
5. THE skill SHALL disregard skills managed by another tool or the user when they do not carry `specle_group`.

### Requirement 19: Separate skill summaries from usage guidance

**User Story:** As a developer, I want concise skill summaries and detailed usage guidance kept separately, so that agents can select skills from compact trigger information while presenting the appropriate level of help to users.

#### Acceptance Criteria

1. EVERY Specle skill blueprint SHALL declare a concise `description` that retains its essential trigger keywords.
2. EVERY Specle skill blueprint SHALL declare a non-empty `usage` field describing when to apply the skill, its important preconditions or exclusions, and its expected result.
3. EVERY installed Specle skill SHALL retain its blueprint's `description` and `usage` metadata.
4. THE `specle` skill SHALL read both fields from the installed Specle inventory and determine whether to show a compact summary, detailed usage guidance, or both according to the user's request.
5. THE metadata contract SHALL remain suitable for future client selection and MCP skill-resource consumers without requiring the current client to use `usage` as a selection signal.

### Requirement 20: Publish the current lifecycle reference

**User Story:** As a developer, I want a concise reference for the lifecycle currently implemented by Specle, so that I can understand statuses, workflow commands, and every supported spec flow without confusing it with planned delivery-policy work.

#### Acceptance Criteria

1. THE repository SHALL provide a root `LIFECYCLE.md` describing only the currently implemented lifecycle.
2. THE reference SHALL map each lifecycle-owning workflow command to its status transition or explicitly state when it does not transition status.
3. THE reference SHALL include vertically readable inline Mermaid diagrams for normal work, queued abbreviated bugfix and refactor work, and spikes.
4. THE reference SHALL identify the current Resolve completion paths for normal and abbreviated work, including reconciliation of completed dispatched actions and terminal independent-spec hand-offs, audit every lifecycle state for a valid transition or terminal outcome, and SHALL not describe planned delivery-policy statuses or commands as implemented.

### Requirement 21: Reconcile dispatched review actions

**User Story:** As a developer, I want Resolve to clearly tell me when to invoke it again after follow-up work, so that a reviewed item can progress out of `triaged` without relying on an implicit workflow step.

#### Acceptance Criteria

1. WHEN Resolve finds incomplete recorded follow-up work, THE workflow SHALL report the follow-up's next step and `resolve <target>` as the reconciliation step after that work is complete.
2. THE lifecycle reference SHALL show that later Resolve invocation as the transition from waiting for follow-up work to completion.

## Non-Functional Requirements

- Skills and steering remain reusable across projects and must not prescribe a project framework, tracker, or hosting service.
- The project uses Python tooling managed through `uv`; this specification does not add a new runtime dependency or external integration.
- Specifications and their artefacts remain committed under `.specle/`.
