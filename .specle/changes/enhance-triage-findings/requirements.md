# Requirements: Enhance triage findings

## Introduction

`review-findings.json` already records review sources, consolidated items, decisions, and routes, but it cannot consistently show which part of the workflow missed a shortcoming, classify recurring types of build failure, or summarise the final result after resolution. Specle needs a compact, agent-authored analytical layer so historical triage records can be queried for workflow improvement without importing external review payloads.

## Glossary

- **Review source:** metadata identifying a local or externally supplied review, its assessed implementation revision, and its outcome. The supplied review content remains external evidence.
- **Consolidated item:** one durable, agent-authored finding linked to one or more review sources.
- **Analytical fields:** optional classifications and summaries that explain the confirmed cause, affected area, missed workflow stage, and eventual outcome of a consolidated item.
- **Resolution entry:** an append-only, agent-authored summary of one final review outcome and its decision and dispatch counts after `resolve` has reconciled its scoped items.

## Requirements

### Requirement 1: Define a versioned review-findings contract

**User Story:** As a developer, I want review records to have a stable, machine-readable shape so their history can be analysed across changes.

#### Acceptance Criteria

1. Specle SHALL package and register a `review-findings/1.0` JSON Schema contract for `review-findings.json`.
2. The contract SHALL recognise a top-level schema identifier, a `sources` collection, and an `items` collection while permitting future additional properties.
3. Source entries SHALL support optional `reviewed_at`, `review_phase`, and `implementation_revision` fields alongside existing source identity, kind, outcome, and revision information.
4. Item entries SHALL support optional `category`, `missed_by`, `cause`, `affected_areas`, and `outcome` fields alongside existing evidence, analysis, recommendation, decision, route, and dispatch information.
5. Every new analytical field SHALL be optional so historical and minimal review records remain valid.

### Requirement 2: Preserve the external-input boundary

**User Story:** As a developer, I want useful historical analysis without treating a reviewer’s payload as repository truth.

#### Acceptance Criteria

1. Triage SHALL retain source identity and a revision or content fingerprint for every supplied review.
2. Triage SHALL record analytical fields only as its own concise, confirmed assessment after applying external-input policy and user decisions.
3. Triage SHALL NOT copy, embed, or treat an externally supplied JSON or Markdown review payload as authoritative record content.
4. Source references and consolidated-item links SHALL remain sufficient to identify which review supplied a finding or duplicate relationship.

### Requirement 3: Document analysis-aware triage

**User Story:** As an agent, I want clear guidance for creating analysis-ready review records without changing delivery or implementation work during triage.

#### Acceptance Criteria

1. The portable and installed `triage` skills SHALL explain the purpose and optional use of every analytical source and item field.
2. The skills SHALL direct agents to classify only information they can support from repository evidence and recorded user decisions.
3. The skills SHALL preserve existing decisions, routes, dispatch details, source history, and unknown fields when updating a record.
4. The skills SHALL continue to consolidate clear duplicates by source reference without importing raw external content.

### Requirement 4: Record final resolution outcomes

**User Story:** As a developer, I want each resolved review to retain its final outcome and compact statistics so I can compare what triage decided with what was actually completed.

#### Acceptance Criteria

1. The contract SHALL support an optional top-level `resolutions` list of append-only resolution entries.
2. Resolution statistics SHALL support counts for total current items, accepted and varied decisions, terminal no-action decisions, and dispatched, completed, pending, or failed follow-up work.
3. Each resolution entry SHALL identify its final outcome, resolution timestamp, contributing source IDs, and scoped item IDs.
4. The portable and installed `resolve` skills SHALL append a resolution entry only after reconciling every item in that entry's scope, using durable item decisions and dispatch states rather than an external review's claims.
5. A resolution entry SHALL preserve source history and per-item decisions; it SHALL be a compact aggregate, not a replacement for the consolidated items or an earlier resolution entry.

## Boundaries

- This change adds the review-findings contract and triage and resolve guidance only.
- It does not change the `review` workflow, lifecycle transitions, review-record runtime validation, or archived records.
- It does not make analytical classification mandatory and does not add recurring workflow-simulation tests.
