# Requirements: add Specle reconcile

## Introduction

Git can retain both `.specle/specs/<name>/` and `.specle/archive/<name>/` when branches independently modify an active spec and archive it. Git tracks files rather than a spec's stable identity, so a merge or branch switch can leave two durable directories with the same name. Ordinary lifecycle commands must not guess which copy is authoritative or silently discard work.

## Glossary

- **Duplicate spec:** the same stable spec name appears under both active and archived locations.
- **Reconciliation:** a user-confirmed recovery operation that analyses duplicate records and applies a selected safe remedy.
- **Candidate remedy:** a non-mutating recommendation based on durable state, artifacts, and relevant Git history.

## Requirements

### Requirement 1: Detect and block duplicate durable identities

**User Story:** As a developer, I want Specle to identify duplicate spec names clearly, so ordinary workflow commands do not operate on ambiguous state.

#### Acceptance Criteria

1. `specle validate` SHALL report every stable name found in both `.specle/specs/` and `.specle/archive/`.
2. Lifecycle-mutating workflows SHALL stop for an ambiguous target until reconciliation has resolved its duplicate identity.
3. Status reporting SHALL surface a duplicate as requiring reconciliation rather than listing either copy as ordinary pending work.
4. Detection SHALL preserve both directories and every artifact without modifying either copy.

### Requirement 2: Provide read-only reconciliation analysis

**User Story:** As a developer, I want an agent to inspect why a duplicate exists and recommend a safe remedy, so I can recover without losing work.

#### Acceptance Criteria

1. `specle reconcile <spec-name>` SHALL require an explicit stable spec name and perform no writes by default.
2. The command SHALL report both locations, their durable statuses and delivery evidence, artifact inventories, and material file differences.
3. The command SHALL inspect relevant Git history and report available ancestry or merge context without claiming certainty where evidence is incomplete.
4. The command SHALL identify exact duplicates and present candidate remedies, including their consequences.
5. The command SHALL produce machine-readable output suitable for an agent to explain and discuss with the user.

### Requirement 3: Apply only explicitly selected safe remedies

**User Story:** As a developer, I want reconciliation changes to be deliberate and recoverable, so automatic recovery cannot discard newer or divergent work.

#### Acceptance Criteria

1. `specle reconcile` SHALL not delete, move, or rewrite a duplicate directory without an explicit user-selected remedy and confirmation.
2. An exact active/archive duplicate MAY offer removal of the redundant copy only after confirmation.
3. Divergent records or artifacts SHALL remain blocked for user-directed resolution; the command SHALL NOT automatically choose the archive merely because of its location.
4. Applied operations SHALL use staged temporary paths and recovery backups, leaving the original copy intact if replacement fails.
5. A successful remedy SHALL leave exactly one durable location for the stable spec name and restore ordinary lifecycle validation.

## Non-Functional Requirements

- Reconciliation must be conservative: preservation of durable artifacts is more important than automation.
- The command must work without network access; Git history inspection is local.
- This change is independent of the currently reviewed state-restructure change, but will use the state model once it is merged.
