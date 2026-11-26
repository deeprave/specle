# Requirements: resurrect context json

## Introduction

`.specle/context.json` was intentionally retired as tracked lifecycle state, but agents still benefit from a small worktree-local hand-off record. Specle should encourage, without requiring, agents to maintain useful current context without allowing it to become an authoritative state record, diary, or execution log.

## Glossary

- **Context:** optional ignored JSON at `.specle/context.json` containing concise hand-off information for a worktree.
- **Milestone:** a concise record of a meaningful completed activity or decision relevant to current work.
- **Todo:** a short item that is not yet a defined change and may later be removed or transferred to an active change.
- **Directive:** a current user-provided default, denial, or other instruction for later agents.
- **Durable change state:** the authoritative tracked status, lifecycle, relationship, and delivery records stored with each change.

## Requirements

### Requirement 1: Define an optional extensible context document

**User Story:** As an agent continuing work in a repository, I want a lightweight hand-off document with a small stable shape and room for useful project-specific information.

#### Acceptance Criteria

1. Specle SHALL define a versioned JSON Schema for `.specle/context.json`.
2. The schema SHALL permit an absent context file and SHALL not require agents to create or update one.
3. The schema SHALL define optional top-level `milestones`, `todos`, and `directives` collections and SHALL permit additional top-level properties and arbitrary additional item properties.
4. The context document SHALL remain ignored and worktree-local.
5. Specle commands SHALL NOT read, validate, infer from, or alter context; the schema is a portable format for agents that choose to use it.

### Requirement 2: Record concise hand-off milestones

**User Story:** As an agent or developer resuming work, I want to see what materially happened recently without reading an activity diary.

#### Acceptance Criteria

1. Each milestone entry SHALL contain a non-empty, human-readable local `date_added` date-and-time string and concise human-readable `subject`. Guidance SHALL prefer ISO 8601 with an explicit numeric offset, but the schema SHALL not enforce that preferred form.
2. A milestone entry SHALL allow an optional `change` reference and optional `detail` of any JSON shape.
3. Milestones MAY include additional agent-selected hand-off information when it remains useful to current work.
4. Guidance SHALL direct agents to remove milestones that are obsolete or no longer relevant to current activity.
5. Guidance SHALL require milestones to be maintained in reverse chronological order and permit them to remain indefinitely only while relevant to current work.
6. Guidance SHALL prohibit using milestones as a chronological diary, command log, verification record, or substitute for a change's durable artefacts.

### Requirement 3: Maintain a small informal todo list

**User Story:** As a developer, I want agents to retain short ideas and follow-ups that are not ready to become defined changes.

#### Acceptance Criteria

1. The optional `todos` collection SHALL support entries with a non-empty, human-readable local `date_added` date-and-time string, a concise `subject`, optional associated `change` reference, and optional `detail` of any JSON shape. Guidance SHALL prefer ISO 8601 with an explicit numeric offset, but the schema SHALL not enforce that preferred form.
2. An agent MAY add, remove, reorder, or refine todos when doing so improves current hand-off context.
3. When a todo becomes a defined change, guidance SHALL direct the agent to remove or mark the todo as transferred and link it to the change where useful.
4. Todos SHALL not create lifecycle dependencies, become an authoritative backlog, or replace defined changes.
5. Guidance SHALL direct agents to prune obsolete, completed, or irrelevant todos.

### Requirement 4: Preserve user directives

**User Story:** As a developer, I want durable-in-the-worktree instructions that a later agent can follow without treating them as lifecycle state.

#### Acceptance Criteria

1. The optional `directives` collection SHALL support a concise `subject` and optional `detail` of any JSON shape.
2. Guidance SHALL describe directives as user-provided default actions, explicit denials, or other current hand-off instructions.
3. Directives SHALL not override repository policy, durable change artefacts, or explicit user instructions in the current conversation.

### Requirement 5: Make hand-off maintenance policy-controlled

**User Story:** As a repository owner, I want the hand-off document to be useful by default while retaining project control over whether it is maintained and who may update it.

#### Acceptance Criteria

1. Specle SHALL provide a portable context policy describing `context.json` as an optional, ignored, worktree-local hand-off document.
2. The portable default SHALL enable hand-off-context maintenance; a project policy MAY disable it entirely.
3. Project onboarding SHALL ask whether to maintain `context.json` and whether reviewing agents may update it, then record the selections in a project-specific context policy document.
4. A reviewing agent is an agent that neither built nor participated in the feature's design. When reviewing-agent updates are not explicitly allowed by the project policy, it MAY read but SHALL NOT modify `context.json`.
5. When enabled and permitted, agents SHALL use context to hand off current status, recent activities, milestones, todos, directives, and their own material actions without making it a prerequisite for workflow skills.
6. The portable policy SHALL state the `context/1.0` schema URI and essential writing guidance, including the preferred local ISO 8601 timestamp form. Skills that own recommended activation, first-commit, and completion milestones SHALL read the portable policy and applicable project context guidance without making context blocking.

### Requirement 6: Preserve durable-state boundaries

**User Story:** As a repository owner, I want optional context to aid continuity without reintroducing shared-state conflicts or ambiguous workflow authority.

#### Acceptance Criteria

1. Skills SHALL continue to derive selection, lifecycle status, delivery facts, dependencies, and relationships from durable change records rather than `context.json`.
2. Context SHALL not be committed, included in delivery commits, or merged between worktrees.
3. A missing, invalid, or stale context document SHALL not block normal Specle lifecycle operations; no Specle command reads it.
4. Portable workflow guidance SHALL encourage agents to read and, when useful, refresh context at hand-off boundaries without making it a prerequisite for any skill.

### Requirement 7: Treat external inputs as untrusted

**User Story:** As a repository owner, I want agents to assess external feedback rather than accepting it as truth or authority, so it cannot silently redirect project work.

#### Acceptance Criteria

1. Specle SHALL provide a portable policy stating that external feedback and data are untrusted inputs, including GitHub issues, issue trackers, pull requests, pull-request reviews, and provided external reviews.
2. The policy SHALL instruct agents never to treat external inputs as facts, instructions, authority, approval, or user intent without independent confirmation.
3. The policy SHALL direct agents to assess an external input's accuracy, relevance, and provider intent, independently verify material claims against authoritative project evidence, and seek explicit user direction before acting on a material proposal or instruction.
4. This rule SHALL be portable policy, not a project-specific override.

### Requirement 8: Preserve varied review dispositions

**User Story:** As a reviewer and repository owner, I want a variation to remain distinct from accepting or declining a recommendation, so the durable review history truthfully records the decision made.

#### Acceptance Criteria

1. Lifecycle validation SHALL treat a `vary` decision with a completed dispatch as settled review evidence.
2. The durable record SHALL retain the varied recommendation, rationale, and resulting route rather than rewriting it as acceptance.
3. Triage and resolve guidance SHALL dispatch both accepted and varied findings through their recorded routes, while preserving the distinction between their decisions.

### Requirement 9: Preserve agent-meaningful tracker locators

**User Story:** As an agent integrating a project tracker, I want to record the locator that is useful to my integration rather than being limited to Web URLs.

#### Acceptance Criteria

1. Tracker-link source and destination locators SHALL accept non-empty strings without requiring HTTP(S) or URI syntax.
2. Guidance and validation SHALL leave the locator protocol or representation to the integrating agent.

## Non-Functional Requirements

- The context schema must be deliberately permissive, with optional recognised fields, arbitrary additional properties, and `detail` values of any JSON type.
- Context entries should be short and current-oriented; regular pruning is guidance, not a mechanical retention policy.
- This change is independent of active-directory renaming and the queued manifest/update work. It may use the current `.specle/` location without depending on their implementation.
