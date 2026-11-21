# Requirements: resurrect context json

## Introduction

`.specle/context.json` was intentionally retired as tracked lifecycle state, but agents still benefit from a small worktree-local handoff record. Specle should encourage, without requiring, agents to maintain useful current context without allowing it to become an authoritative state record, diary, or execution log.

## Glossary

- **Context:** optional ignored JSON at `.specle/context.json` containing concise handoff information for a worktree.
- **Milestone:** a concise record of a meaningful completed activity or decision relevant to current work.
- **Todo:** a short item that is not yet a defined change and may later be removed or transferred to an active change.
- **Durable change state:** the authoritative tracked status, lifecycle, relationship, and delivery records stored with each change.

## Requirements

### Requirement 1: Define an optional extensible context document

**User Story:** As an agent continuing work in a repository, I want a lightweight handoff document with a small stable shape and room for useful project-specific information.

#### Acceptance Criteria

1. Specle SHALL define a versioned JSON Schema for `.specle/context.json`.
2. The schema SHALL permit an absent context file and SHALL not require agents to create or update one.
3. The schema SHALL define optional top-level `milestones` and `todos` collections and SHALL permit additional top-level properties and additional item properties.
4. The context document SHALL remain ignored and worktree-local.
5. Context validation, when explicitly performed, SHALL validate only its JSON structure and declared lightweight fields; it SHALL not infer or alter lifecycle state.

### Requirement 2: Record concise handoff milestones

**User Story:** As an agent or developer resuming work, I want to see what materially happened recently without reading an activity diary.

#### Acceptance Criteria

1. Each milestone entry SHALL contain a `created_at` timestamp and concise human-readable summary.
2. A milestone entry SHALL allow an optional `change` reference when it relates to a defined or active change.
3. Milestones MAY include additional agent-selected handoff information when it remains useful to current work.
4. Guidance SHALL direct agents to remove milestones that are obsolete or no longer relevant to current activity.
5. Guidance SHALL prohibit using milestones as a chronological diary, command log, verification record, or substitute for a change's durable artefacts.

### Requirement 3: Maintain a small informal todo list

**User Story:** As a developer, I want agents to retain short ideas and follow-ups that are not ready to become defined changes.

#### Acceptance Criteria

1. The optional `todos` collection SHALL support concise entries with a summary and optional associated `change` reference.
2. An agent MAY add, remove, reorder, or refine todos when doing so improves current handoff context.
3. When a todo becomes a defined change, guidance SHALL direct the agent to remove or mark the todo as transferred and link it to the change where useful.
4. Todos SHALL not create lifecycle dependencies, become an authoritative backlog, or replace defined changes.
5. Guidance SHALL direct agents to prune obsolete, completed, or irrelevant todos.

### Requirement 4: Preserve durable-state boundaries

**User Story:** As a repository owner, I want optional context to aid continuity without reintroducing shared-state conflicts or ambiguous workflow authority.

#### Acceptance Criteria

1. Skills SHALL continue to derive selection, lifecycle status, delivery facts, dependencies, and relationships from durable change records rather than `context.json`.
2. Context SHALL not be committed, included in delivery commits, or merged between worktrees.
3. A missing, invalid, or stale context document SHALL not block normal Specle lifecycle operations.
4. Portable workflow guidance SHALL encourage agents to read and, when useful, refresh context at handoff boundaries without making it a prerequisite for any skill.

## Non-Functional Requirements

- The context schema must be deliberately permissive, with optional recognised fields and additional properties allowed.
- Context entries should be short and current-oriented; regular pruning is guidance, not a mechanical retention policy.
- This change is independent of active-directory renaming and the queued manifest/update work. It may use the current `.specle/` location without depending on their implementation.
