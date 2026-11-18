# Requirements: delivery policy and completion workflow

## Introduction

Specle currently treats local review approval as completion. That is correct only for a local-only repository or a direct-to-main workflow without peer review. Projects with a shared upstream and pull requests need a clear distinction between locally approved work, work submitted for external review, and work that has actually been delivered.

## Glossary

- **Delivery model**: the project-selected way approved work reaches its users or shared repository.
- **Local approval**: approval from Specle's local `review` skill after verification passes.
- **Committed**: a reviewable delivery has been created or updated according to a branch-and-pull-request delivery model.
- **Completion**: the configured final delivery outcome has been confirmed.
- **External review**: feedback from peers, a hosted repository, cloud agents, or another source outside the local review skill.

## Requirements

### Requirement 1: Describe portable delivery models

**User Story:** As a developer, I want a small set of reusable delivery models, so that Specle can support ordinary repository workflows without prescribing a hosting service or local convention.

#### Acceptance Criteria

1. THE distribution SHALL provide `.agents/steering/delivery.md` describing these models briefly: local-only Git; shared upstream with direct commits to a main branch and no peer review; and shared upstream with branch-and-pull-request peer review.
2. THE steering SHALL distinguish portable model behaviour from project-selected policy.
3. THE steering SHALL explain the lifecycle meanings of `approved`, `committed`, and `complete` for each model.
4. THE steering SHALL permit projects to document another delivery model without requiring a distribution change.

### Requirement 2: Record project delivery policy

**User Story:** As a developer, I want delivery conventions recorded with the other project guidance, so that agents can prepare and deliver changes according to this project's rules.

#### Acceptance Criteria

1. THE project overlay SHALL include `.agents/project/delivery.md` and identify it in its README.
2. THE `onboard` skill SHALL inventory `delivery.md` and, when it is missing or incomplete, ask one delivery question at a time before writing the completed project guidance.
3. THE onboarding questions SHALL establish the selected delivery model and applicable policy for branch naming, commit title and message format, secrets or other pre-delivery checks, pull-request format and templates, final delivery event, and authority for agent-performed external writes.
4. THE project document SHALL retain unestablished preferences explicitly rather than inventing them.

### Requirement 3: Separate local approval from completion

**User Story:** As a developer, I want local review approval recorded without falsely claiming external delivery is complete.

#### Acceptance Criteria

1. THE lifecycle SHALL add `approved` after a successful local `review` of a normal change, bugfix, or refactor.
2. THE `review` skill SHALL transition an approved target to `approved`, record the local review evidence, and identify `commit` as the next delivery stage when the selected model requires it.
3. THE lifecycle SHALL reserve `complete` for the configured final delivery outcome, except for a spike whose findings are complete without implementation delivery.
4. A local-only model or direct-to-main model without peer review MAY transition an approved target to `complete` through its applicable `commit` operation.
5. WHEN a local review's findings are all terminally no-action, `resolve` SHALL restore the target to `approved` with next `commit`; it SHALL not mark the target complete without the configured delivery outcome.

### Requirement 4: Commit according to the delivery policy

**User Story:** As a developer, I want a `commit` skill that can prepare or perform the project-specific delivery action safely.

#### Acceptance Criteria

1. THE project SHALL provide a `commit` skill that operates only on an `approved` target and reads the selected project delivery policy.
2. THE skill SHALL inspect the target's scoped changes, avoid staging unrelated work, and run required pre-delivery checks, including configured secrets checks.
3. THE skill SHALL either provide exact delivery instructions or perform authorised commit, push, and pull-request actions; it SHALL not make an external write without user authorisation and applicable project policy.
4. FOR the branch-and-pull-request model, THE skill SHALL record the resulting delivery reference and set the target to `committed` after the branch and reviewable change request are successfully created or updated.
5. FOR local-only and direct-to-main models, THE skill SHALL record the applicable local commit or shared-upstream delivery evidence and transition the target to `complete` when the configured final event succeeds.
6. THE delivery record SHALL remain associated with its spec and use any applicable versioned JSON contract rather than an undocumented operational format.

### Requirement 5: Complete externally reviewed delivery

**User Story:** As a developer, I want an explicit finalisation step for a submitted pull request, so that `complete` means the project delivery policy has been satisfied.

#### Acceptance Criteria

1. THE project SHALL provide a `complete` skill for the branch-and-pull-request model.
2. THE skill SHALL require a named or selected target with `status: "committed"`, an associated reviewable delivery reference, and a checkout on that delivery's head branch before it performs merge or local branch operations.
3. IF the checkout is on another branch, including the delivery target branch, THEN the skill SHALL stop and report the current and expected branches without stashing, switching, merging, pulling, or otherwise modifying the worktree.
4. WHEN project policy and the user authorise delivery actions, THE skill SHALL merge the reviewable change request, switch to the configured delivery target branch, and fast-forward from upstream before changing the target to `complete`.
5. IF the checkout has tracked or untracked changes before an authorised merge-and-sync operation, THEN the skill SHALL preserve them with a recoverable stash, restore them after the target branch is synchronised, and retain the stash with a clear recovery report if restoration conflicts or fails.
6. IF external findings remain unresolved, the final event cannot be evidenced, or a required external action is not authorised, THEN the skill SHALL not mark the target complete and SHALL direct the user to the applicable next action. Lack of merge authority SHALL not prevent confirmation of an already evidenced external merge.
7. THE skill SHALL preserve the active current issue when completing a non-active target.

### Requirement 6: Re-enter submitted work safely

**User Story:** As a developer, I want to triage feedback on a submitted earlier change while another issue is active, so that external review does not disrupt current work.

#### Acceptance Criteria

1. `triage`, `resolve`, and their downstream workflows SHALL support an explicitly named `committed` normal change as well as abbreviated bugfix or refactor work.
2. New external findings SHALL move only the selected submitted target to `review-findings`; they SHALL not replace the active current issue.
3. AFTER accepted feedback is resolved and implementation changes occur, the target SHALL return through verification, local review, `approved`, and `commit` before it may again become `committed` or `complete`.
4. The workflow SHALL retain source identity and delivery references so unchanged external findings are not reintroduced.
5. A named non-active committed normal change SHALL be able to resume its required build, verification, review, approval, and commit stages without replacing the active current issue.
6. WHEN `resolve` creates an independent-spec hand-off, it SHALL create the new normal spec as a queued `defined` record and preserve the origin at `approved` or `committed` according to its delivery history; only that origin's configured delivery event may mark it `complete`.

## Non-Functional Requirements

- Delivery steering and skills remain agent-client, hosting-provider, and tracker agnostic.
- Project delivery policy is human-maintained Markdown; operational delivery and review state is agent-managed JSON.
- External writes remain explicit, authorised, and scoped to the selected delivery target.
- The change must preserve the ability to work on one active issue while submitted work awaits peer review or receives feedback.
- Exact operational JSON shapes must conform to the versioned JSON-contract work when that contract is available; this change must not establish undocumented ad-hoc runtime records.
