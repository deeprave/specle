# Link sidecar completion

## Problem

A sidecar bugfix or refactor can be delivered with a parent change's completion PR but remain an active `committed` record afterwards. The parent has no durable inventory of its sidecars, so finalisation cannot deterministically archive the complete delivery set.

## Goal

Make concurrent, explicitly linked sidecars complete and archive atomically with their parent change, using reciprocal durable relationship records rather than inference from a directory scan.

## Direction

Bugfix and refactor creation will record both sides of a sidecar relationship from freshly read durable records: the sidecar declares its parent with `type: "origin"` and the parent declares the sidecar. The unreleased `change-status/1.0` schema will make the optional relationship `delivery` value explicit. Runtime validation will diagnose malformed declared reciprocal relationships in active records without retroactively constraining archived legacy records, while commit and complete retain the targeted readiness checks for parent delivery.

During parent archival finalisation, every eligible linked sidecar will move to `.specle/archive/`, receive `status: "complete"` and `archived_at`, and record the same delivery and completion-PR evidence as its parent. Unlinked, incomplete, or inconsistent sidecars remain excluded with an actionable diagnostic.

## Verification

Test production lifecycle helpers for reciprocal-link validation, runtime structural diagnostics, eligible-sidecar discovery, joint archival, delivery evidence, and rejection of malformed or unlinked records. Run the repository quality gates and installed/blueprint validation.
