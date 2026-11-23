# Link sidecar completion

## Problem

A sidecar bugfix or refactor can be delivered with a parent change's completion PR but remain an active `committed` record afterwards. The parent has no durable inventory of its sidecars, so finalisation cannot deterministically archive the complete delivery set.

## Goal

Make concurrent, explicitly linked sidecars complete and archive atomically with their parent change, using reciprocal durable relationship records rather than inference from a directory scan.

## Direction

Bugfix and refactor creation will record both sides of a sidecar relationship: the sidecar declares its parent and the parent declares the sidecar. The unreleased `change-status/1.0` schema will make the optional relationship `delivery` value explicit. Commit and complete will use the parent declaration only when the reciprocal sidecar declaration agrees and delivery is explicitly `with-related-change`.

During parent archival finalisation, every eligible linked sidecar will move to `.specle/archive/`, receive `status: "complete"` and `archived_at`, and share the parent's delivery evidence and completion-PR path. Unlinked, incomplete, or inconsistent sidecars remain excluded with an actionable diagnostic.

## Verification

Test production lifecycle helpers for reciprocal-link validation, eligible-sidecar discovery, joint archival, delivery evidence, and rejection of mismatched or unlinked records. Run the repository quality gates and installed/blueprint validation.
