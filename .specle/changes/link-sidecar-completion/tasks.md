# Tasks: Link sidecar completion

- [x] 1. Extend the durable relationship contract
  - [x] 1.1 Add focused schema-registry tests for an optional relationship `delivery` value and the concurrent-delivery literal. (`tests/test_schema_registry.py`)
  - [x] 1.2 Update `change-status/1.0` to describe the optional `relationships[].delivery` field without changing the unreleased schema version. (`src/specle/schemas/change-status/1.0.json`)

- [x] 2. Add reciprocal sidecar discovery and validation
  - [x] 2.1 Add production tests for parent-only candidate discovery, valid reciprocal links, missing/mismatched/duplicate links, wrong kinds, and unready sidecars. (`tests/test_lifecycle.py` or a focused lifecycle helper test module)
  - [x] 2.2 Implement a package-owned helper over the already-read change-state snapshot that returns validated, delivery-ready sidecars or actionable diagnostics. (`src/specle/lifecycle.py` and, where appropriate, `src/specle/change_state.py`)

- [x] 3. Make linked abbreviated creation atomic
  - [x] 3.1 Add focused production tests for writing reciprocal parent/sidecar records and safely reporting an incomplete dual-record write. (`tests/` lifecycle/state coverage)
  - [x] 3.2 Implement the shared durable-record mutation helper used when a bugfix or refactor is linked to selected parent work. (`src/specle/`)

- [x] 4. Apply the validated delivery set to completion
  - [x] 4.1 Add production tests that a valid parent discovers reciprocal sidecars in both `approved` and `committed` delivery-ready states, while ineligible candidates remain excluded. (`tests/` lifecycle coverage)
  - [x] 4.2 Integrate the validated helper's parent-led delivery set into the commit, complete, and wrapup workflow instructions so one completion PR finalises every eligible member. (`src/specle/blueprints/skills/`, `.agents/skills/`)

- [x] 5. Update managed workflow guidance and documentation
  - [x] 5.1 Update blueprint and installed bugfix/refactor/commit/complete/wrapup/changelist/status skills with reciprocal creation, validation, reporting, and joint archival ownership. (`src/specle/blueprints/skills/`, `.agents/skills/`)
  - [x] 5.2 Update lifecycle policy and repository lifecycle/layout documentation with the relationship delivery contract and no separate eligible-sidecar completion cycle. (`src/specle/blueprints/policies/lifecycle.md`, `.agents/policies/lifecycle.md`, `docs/LIFECYCLE.md`, `docs/LAYOUT.md`)
  - [x] 5.3 Regenerate the active managed skill index after blueprint updates. (`.agents/skills/specle/index.json`)

- [x] 6. Verify the completed behaviour
  - [x] 6.1 Run focused lifecycle and schema tests, then `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, and `uv run ty`.
  - [x] 6.2 Run installed and blueprint Specle validation and confirm that no unrelated active changes or project-owned files were altered.
