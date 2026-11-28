# Refactor change record

Specle currently reads `status.json` into a small `ChangeRecord`, but consumers have no common object for tasks, estimates, requirements, spec, and other change artifacts. Next-action logic is separate and cannot deterministically distinguish completed from unfinished build tasks without another artifact reader.

Build a reusable async module and `ChangeRecord` interface around the existing change-state representation. Load basic status initially; load tasks, estimate, requirements, spec, and other needed artifacts lazily and cache them. Clearly distinguish missing, unreadable or malformed, and empty artifacts. Provide a bounded LRU record cache, a common lookup interface, per-change invalidation and whole-cache clearing, and documented behaviour for held records and external edits. Cache identity must distinguish projects and active/archive locations; durable files remain authoritative.

The record provides a next-action operation using lifecycle state, kind, selection, and relevant artifacts. Use the existing lifecycle graph and skill metadata where they can express the decision, addressing gaps for kind, selection, and artifact-dependent actions rather than maintaining a competing lifecycle map. In particular, a readable task plan with no unfinished tasks leads a building normal change to `verify`; unfinished tasks lead to `build`. Missing, unreadable, malformed, or empty plans must not be mistaken for completed work, and checked boxes never imply a verified lifecycle state.

Use the common interface in existing listing and lifecycle consumers, preserving discovery, validation, and output contracts except for the intended next-action correction. LRU capacity, cache ownership, invalidated-handle behaviour, and artifact parsing details belong in design. The cache is process-local; no filesystem watcher or cross-process coherence mechanism is assumed. `consolidate-state-enums` and the in-flight listing change remain independent, without inferred dependencies.

Verification should cover lazy reads, artifact errors, LRU reuse and eviction, isolation, explicit invalidation, next-action decisions, and existing CLI behaviour.
