# Summary: Link sidecar completion

## Summary

Concurrent bugfix and refactor sidecars now use reciprocal durable relationships for parent-led delivery and joint archival.

## Outcome

Eligible linked sidecars share their parent’s delivery and completion evidence, archive in the same finalisation, and do not require an independent completion cycle.

## What changed

- Added fresh relationship state updates and structural reciprocal validation for active records.
- Required the reciprocal `origin` role and documented the lifecycle boundaries for timestamps and completion evidence.
- Added focused lifecycle and schema regression coverage.
