# Requirements: add wrapup skill

## Introduction

For branch-and-pull-request delivery, archival work must be committed in a completion PR after the implementation PR merges. The current workflow leaves the developer needing to invoke `complete` repeatedly for that separate delivery. Completion should prepare and submit the archival finalisation once; a distinct final step should only merge that already-prepared completion PR and synchronise the delivery branch.

## Glossary

- **Final delivery:** the project-defined external event that delivers implementation work, such as merging its implementation pull request.
- **Archival finalisation:** generating the human summary, recording archival metadata, moving a completed change to `.specle/archive/`, and submitting its durable record in a completion PR when repository policy requires it.
- **Completion PR:** a pull request that contains only archival finalisation after the implementation PR has already merged.
- **Wrapup:** the final, non-mutating delivery step that merges an already-submitted completion PR and synchronises the configured delivery branch.

## Requirements

### Requirement 1: Complete final delivery and archival finalisation together

**User Story:** As a developer, I want `complete` to prepare the complete durable record and its completion PR in one run, so I do not need to rerun it to perform archival work.

#### Acceptance Criteria

1. `complete` SHALL confirm or perform the configured final delivery event for a committed change, including authorised implementation-PR merge and local delivery-branch synchronisation.
2. `complete` SHALL record an already-evidenced final delivery without attempting to merge it again.
3. After final delivery, `complete` SHALL generate the concise human-facing `summary.md`, set `archived_at`, move the change directory to `.specle/archive/<change-name>/`, retain the local selector through completion-PR delivery, and preserve every durable artefact and delivery field.
4. When archival finalisation must be committed separately, `complete` SHALL create a dedicated completion branch from the retained delivery head, commit only the archival finalisation, push it, and open or update its completion PR to the configured delivery branch.
5. `complete` SHALL preserve unrelated tracked, untracked, and ignored work with a named recoverable stash before any required branch switch or synchronisation, then restore it afterwards. On restore failure it SHALL retain the stash and report recovery steps.
6. `complete` SHALL avoid duplicate completion branches, completion PRs, summaries, or directory moves when re-entered after an interrupted or already-created finalisation.
7. Once a completion PR is open, the active lifecycle state SHALL direct the next action to `wrapup`.

### Requirement 2: Provide a wrapup skill

**User Story:** As a developer, I want `wrapup` to own only the final completion-PR merge and synchronisation, so it never mutates an archived change.

#### Acceptance Criteria

1. `wrapup` SHALL operate only when a completion PR has been recorded for a change already stored in `.specle/archive/`.
2. With explicit user authorisation and subject to delivery policy, `wrapup` SHALL merge the recorded completion PR and synchronise the local delivery branch.
3. `wrapup` SHALL recognise an externally merged completion PR and synchronise the local delivery branch without attempting another merge.
4. `wrapup` SHALL report an open completion PR with unresolved external feedback as requiring `triage`, rather than merging it.
5. `wrapup` SHALL clear `.specle/current-change` after a successful completion-PR merge and delivery-branch synchronisation, but SHALL not alter `status.json`, generate a summary, move directories, create commits, create pull requests, or otherwise mutate the archived change record.
6. `wrapup` SHALL be a Specle-managed skill, present in the package blueprints and the repository's managed `.agents/skills` inventory.

### Requirement 3: Record archival timestamps

**User Story:** As a developer, I want change timestamps to distinguish active status mutation from archival, so status listings can describe current and archived work reliably.

#### Acceptance Criteria

1. The change-status schema SHALL support optional numeric Unix-second `updated_at` and `archived_at` fields.
2. The versioned change-status JSON Schema, schema registry, packaged schema resources, and schema export SHALL describe and distribute both fields.
3. Every lifecycle owner that writes an activated change's `status.json` before archival SHALL set or update `updated_at` in the same write. This includes `activate`, `estimate`, `design`, `tasks`, `build`, `verify`, `review`, `triage`, `resolve`, `revise`, `commit`, and `complete`, plus the abbreviated and spike workflows whenever they mutate an activated record.
4. `updated_at` need not exist on a newly created record before its first post-activation status mutation.
5. Moving a change to `.specle/archive/` SHALL set `archived_at` to a numeric Unix-second timestamp. Archiving SHALL NOT update `updated_at`.
6. This repository's existing archived change records SHALL receive `archived_at` from the modification time of their `status.json` before it is changed.
7. This repository's activated active change record, if any, SHALL receive `updated_at` from the modification time of its `status.json` before it is changed. Other unactivated active records need not be backfilled.

### Requirement 4: Make lifecycle and delivery guidance unambiguous

**User Story:** As a developer, I want status and workflow guidance to identify archival work explicitly, so the next action is clear after a merge.

#### Acceptance Criteria

1. The lifecycle policy, state reporting, and relevant skill frontmatter SHALL declare `wrapup` as the owning next action after `complete` submits a completion PR, despite the archived record retaining `status: "complete"`.
2. `complete`, `wrapup`, `status`, `summary`, `commit`, and delivery guidance SHALL use consistent terms for final delivery, archival finalisation, and completion PRs.
3. The workflow SHALL not direct a developer to rerun `complete` solely because a submitted completion PR remains outstanding.
4. The lifecycle SHALL provide a recoverable path when a completion PR is already open, merged externally, or has unresolved external feedback.

### Requirement 5: Preserve usable final-stage context

**User Story:** As a developer, I want completion-PR work to retain its selected change until final wrapup, so follow-up commands can resolve the archived record without guessing.

#### Acceptance Criteria

1. While a completion PR is open, `.specle/current-change` SHALL continue to name the archived completed change.
2. Status and relevant local reporting workflows SHALL resolve that selector in `.specle/archive/` and report `wrapup` as the conditional next action when completion-delivery evidence is open.
3. Documentation SHALL explain this final stage and distinguish archival finalisation from the later completion-PR merge.
4. `.specle/.gitignore` SHALL ignore root-level JSON scratch files with `/*.json` while continuing to allow JSON in change and archive subdirectories.
5. The shared `.agents/AGENTS.md` guidance and its blueprint SHALL state that zsh snippets must not use `path` as a variable name.

### Requirement 6: Use package-owned schema identifiers

**User Story:** As a developer, I want schema identifiers to describe Specle's packaged contracts without implying that GitHub hosts a schema retrieval endpoint.

#### Acceptance Criteria

1. Every packaged public schema and its `$schema` instance references SHALL use the stable `specle://schemas/<name>/1.0` identifier form.
2. The schema registry and exported registry SHALL resolve those identifiers exclusively from packaged resources, without network retrieval.
3. The unused `common/1.0` schema SHALL be removed from the packaged schema inventory, registry, and exported schema tree.

## Non-Functional Requirements

- This change adds no implicit external writes: pushing, creating or updating a completion PR, merging it, and synchronising branches remain subject to delivery policy and explicit user authorisation.
- Completion and wrapup must not disturb unrelated worktrees or user-owned working-tree content.
- Existing completed archives remain readable and are not migrated solely for this workflow change.
- The change must update the packaged blueprints and this repository's active `.agents` inventory together.
