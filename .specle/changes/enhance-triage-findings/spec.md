# Enhance triage findings

## Problem

Review findings retain decisions and routes but lack consistent classifications for identifying what build, verification, or review stages repeatedly miss, and they do not retain a compact final-resolution outcome. External review files are useful evidence but must remain untrusted and must not be imported wholesale into durable repository records.

## Goal

Introduce a versioned `review-findings/1.0` contract and update `triage` and `resolve` guidance so records can hold optional, agent-authored analytical fields for source context, confirmed causes, affected areas, missed stages, per-item outcomes, and append-only final-resolution statistics.

## Direction

The schema will register the review-findings contract and recognise optional source fields `reviewed_at`, `review_phase`, and `implementation_revision`; optional item fields `category`, `missed_by`, `cause`, `affected_areas`, and `outcome`; and an optional top-level `resolutions` list. Each resolution entry records final outcome, timestamp, contributing source and item IDs, and counts for its scoped items, accepted or varied decisions, terminal no-action decisions, and dispatched, completed, pending, or failed follow-up work. Entries are append-only so separate local, subagent, PR-human, and PR-AI review cycles remain independently analysable. Existing source identity, revision or fingerprint, evidence, analysis, recommendation, decision, duplicate/source references, route, and dispatch fields remain intact.

The portable blueprint and installed `triage` skills will explain that analysis fields are concise, agent-authored assessments based on confirmed repository evidence and user decisions. The matching `resolve` skills will append an aggregate resolution entry only after reconciling its scoped item decisions and dispatches. These skills retain source identity and fingerprints, consolidate clear duplicates, and preserve unknown fields, but do not copy external review payloads into `review-findings.json`.

## Boundaries

This is deliberately limited to the review-findings schema and triage and resolve guidance. It does not add runtime validation of review records, alter the review workflow or lifecycle transitions, rewrite archived history, or add recurring workflow-simulation tests.

## Verification

Validate the new schema through the registry with minimal historical-compatible records and records containing every optional analytical field and a resolution summary. Confirm that both triage and resolve skill copies remain identical and that their guidance preserves the external-input boundary.
