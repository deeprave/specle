# Requirements: link sidecar completion

## Introduction

Related bugfix and refactor sidecars can be delivered with a parent change, but the current workflow leaves each sidecar as an independent active `committed` record after the parent completion PR merges. That creates false pending work and requires a redundant archival cycle.

## Glossary

- **Parent:** the normal change whose delivery includes explicitly related corrective work.
- **Sidecar:** a bugfix or refactor explicitly delivered with its parent.
- **Reciprocal relationship:** matching durable relationship records on both the parent and sidecar.
- **Joint archival:** moving the parent and its eligible sidecars to `.specle/archive/` in one finalisation delivery.

## Requirements

### Requirement 1: Record reciprocal sidecar relationships

**User Story:** As a developer, I want both members of a concurrent delivery to identify each other, so completion can discover the intended set without guessing.

#### Acceptance Criteria

1. When a bugfix or refactor is created for concurrent delivery, it SHALL record a relationship to its parent change with `delivery: "with-related-change"`.
2. The same operation SHALL record the inverse relationship on the parent record, naming the sidecar and its relationship type.
3. Creation SHALL not leave only one relationship side written when the companion record is writable; a failure SHALL leave an actionable diagnostic rather than silently creating an incomplete link.
4. Unlinked bugfixes and refactors SHALL remain independent work and SHALL never be treated as parent sidecars through ordering, shared files, or directory scanning.
5. The unreleased `change-status/1.0` schema SHALL explicitly describe the optional relationship `delivery` property and permit `with-related-change` as its concurrent-delivery value; no schema-version increment is required.

### Requirement 2: Validate explicit delivery membership

**User Story:** As a developer, I want completion to include only deliberate, mutually declared sidecars, so unrelated work is never delivered or archived accidentally.

#### Acceptance Criteria

1. Package-owned lifecycle code SHALL identify a parent's candidate sidecars from the parent record's inverse relationships.
2. A candidate sidecar SHALL be eligible only when its reciprocal record names the same parent and declares `delivery: "with-related-change"`.
3. Missing, mismatched, duplicate, unapproved, or otherwise ineligible sidecars SHALL be excluded and reported with an actionable diagnostic before parent delivery or archival proceeds.
4. The implementation SHALL not infer sidecar membership by scanning all active records for matching names alone.

### Requirement 3: Archive concurrent sidecars atomically

**User Story:** As a developer, I want delivered sidecars to complete with their parent, so one completion PR finalises the entire related delivery.

#### Acceptance Criteria

1. When `complete` finalises a parent delivery, it SHALL jointly archive every eligible delivered sidecar with that parent in the same archival commit.
2. Joint archival SHALL move each eligible sidecar to `.specle/archive/<name>/`, set its status to `complete`, and write its `archived_at` without changing its prior `updated_at`.
3. Each jointly archived sidecar SHALL retain its reciprocal relationship and record delivery evidence consistent with the parent finalisation.
4. When archival uses a completion PR, the sidecars and parent SHALL be present in that one PR; `wrapup` SHALL finalise that shared delivery without a separate sidecar completion cycle.
5. A sidecar that is not eligible for joint archival SHALL remain active with its own recorded next step and SHALL not block unrelated queued changes.

### Requirement 4: Preserve clear reporting and workflow guidance

**User Story:** As a developer, I want lifecycle reporting to make concurrent delivery visible and avoid false residual work after finalisation.

#### Acceptance Criteria

1. `changelist` and `status` guidance SHALL present declared concurrent sidecars with their parent where that clarifies pending delivery.
2. After successful joint archival, neither the parent nor its jointly archived sidecars SHALL appear as active pending work.
3. `.agents/policies/lifecycle.md` and `docs/LIFECYCLE.md` SHALL describe reciprocal sidecar links, joint archival, and the absence of a separate sidecar completion cycle.
4. `docs/LAYOUT.md` SHALL document the relationship `delivery` property in the `change-status/1.0` contract.
5. The managed skills that create, validate, deliver, archive, or report sidecars, their blueprint copies, and the active `.agents` inventory SHALL describe reciprocal linking and joint archival consistently.

## Non-Functional Requirements

- The workflow must not introduce compatibility aliases, migration paths, or inferred relationships for prior records.
- Relationship validation and joint-archival behaviour require production-code tests; do not add tests that inspect Markdown workflow prose.
- The implementation must preserve unrelated active changes and project-owned files.
