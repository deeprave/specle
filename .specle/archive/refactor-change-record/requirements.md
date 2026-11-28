# Requirements: Refactor change record

## Why

Specle already represents each discovered change as a `ChangeRecord`, but the current object contains only its name, directory, parsed `status.json`, and archive flag. `read_change_state` constructs a snapshot from those records, while lifecycle code separately derives a next action from the record and selection. There is no shared API for reading or interpreting a change's task plan, estimate, requirements, or specification. Consumers that need those artifacts must rediscover and parse them independently.

Provide a reusable asynchronous change-record module and a common cache-managed interface. A record should load basic state initially, load additional artifacts only when requested, and provide the next logical action using the relevant lifecycle and artifact evidence. The cache must be bounded by least-recently-used eviction, and consumers must be able to invalidate a change after its files are modified.

## Scope and boundaries

- Refactor the existing change-state reader and lifecycle consumers into a shared module and `ChangeRecord` interface, rather than introducing an unrelated parallel representation.
- Support status, tasks, estimate, requirements, and spec through the common record interface; include design and other existing change artifacts where needed by actual consumers. Keep narrative artifacts as text unless a consumer needs a parsed interpretation.
- Preserve the existing validation, selection, active/archive discovery, and diagnostic contracts except where the requested artifact-aware next action deliberately makes the result more precise.
- Cache state is process-local and disposable. Durable change artifacts and lifecycle policy remain authoritative; a cache is not a new state store or a reason to infer that work is verified or complete.
- `consolidate-state-enums` and the currently selected changes-listing work are independent changes. This definition does not assume either has been implemented or require either as a prerequisite.
- Filesystem access follows the project's async and AnyIO conventions. Do not introduce worker-thread wrappers for synchronous filesystem operations.

## Requirements

### 1. Provide a common lazy-loaded change record

**User story:** As a Specle consumer, I want one representation of a change so I can access its artifacts without implementing another change reader.

1. THE system SHALL provide a reusable module and `ChangeRecord` class representing a change's stable name, project and active-or-archived location, and basic durable state.
2. WHEN a record is initially obtained, THE reader SHALL load and validate the basic durable state needed to identify the change without eagerly reading its optional narrative and planning artifacts.
3. WHEN a consumer requests tasks, estimate, requirements, or spec, THE record SHALL load that artifact asynchronously on demand and reuse the loaded result until it is invalidated or the record is evicted.
4. THE interface SHALL support the other existing change artifacts needed by its consumers without requiring each consumer to implement its own filesystem reader.
5. THE record SHALL distinguish an absent artifact, an unreadable or malformed artifact, and an artifact that exists but is empty. An unreadable or malformed artifact SHALL provide an actionable failure or diagnostic rather than being silently treated as empty or missing.
6. WHEN consumers read changes, THE shared interface SHALL preserve safe change-name validation, duplicate-name detection, explicit selection, and the existing distinction between active and archived records.

### 2. Manage records through a bounded LRU cache

**User story:** As a Specle consumer, I want to reuse records safely and invalidate them after changes so that cached data remains useful without becoming an unbounded or misleading source of state.

1. THE module SHALL expose a common interface for obtaining change records and managing the record cache.
2. WHEN the same change is requested again while its entry is retained and valid, THE cache SHALL reuse its record and its previously loaded artifacts.
3. THE cache SHALL have a bounded capacity and SHALL evict least-recently-used entries when capacity is exceeded. Capacity and its default SHALL be selected during design.
4. THE cache SHALL distinguish records from different project roots and active or archived locations so a lookup cannot return another project's or location's state.
5. THE interface SHALL support invalidating a specific change and clearing the cache. WHEN a consumer reports that a change's status or artifacts were created, edited, deleted, or moved, subsequent access SHALL not silently return the invalidated cached state.
6. THE design SHALL specify how a previously obtained record handle behaves after invalidation or eviction, including how it avoids silently presenting invalidated artifacts as current.
7. Cache management SHALL document what callers must do after their own writes and how callers refresh after external changes. Do not assume cross-process notifications or a filesystem watcher without an explicit design decision.

### 3. Derive the next action from the record and relevant artifacts

**User story:** As a developer, I want a change record to provide its next logical step so that listing and other consumers use one consistent interpretation.

1. THE `ChangeRecord` interface SHALL provide a next-action operation that uses recorded lifecycle status, kind, selection context, and relevant lazily loaded artifacts.
2. WHEN a normal change is `building` and an existing readable task plan contains no unfinished tasks, THE next action SHALL be `verify`; WHEN the plan contains unfinished tasks, it SHALL be `build`.
3. WHEN the relevant task plan is missing, unreadable, malformed, or empty, THE next-action operation SHALL distinguish that condition and SHALL NOT silently treat it as a completed plan.
4. WHEN estimating or preparation artifacts affect the applicable next action, THE operation SHALL obtain only the artifacts needed for that decision and follow the lifecycle policy in force when the change is implemented.
5. THE next-action operation SHALL preserve the owning workflow for spikes, bugfixes, and refactors and the distinction between selected and unselected normal changes.
6. THE operation SHALL NOT infer `verified`, `approved`, or `complete` lifecycle status from task checkboxes and SHALL NOT mutate change state.
7. THE existing change-listing and runtime lifecycle consumers SHALL use the common record and next-action interface where applicable, without changing their output formats merely as a consequence of this refactor.
8. THE design SHALL use the existing lifecycle graph and skill metadata where they can express the applicable decision, and SHALL identify and address gaps for kind, selection, and artifact-dependent actions rather than maintaining a separate competing lifecycle map.

## Verification direction

Exercise lazy loading and reuse; missing, unreadable, malformed, and empty artifacts; project and active/archive cache isolation; LRU eviction; explicit per-change and whole-cache invalidation; held-record behaviour after invalidation; and lifecycle next actions for complete and incomplete task plans. Verify existing discovery, diagnostics, and CLI output remain compatible, aside from the requested next-action correction. Run the project's documented quality gates.
