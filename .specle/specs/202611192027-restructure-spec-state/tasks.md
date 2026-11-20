# Tasks: restructure Specle spec state

- [x] 1. Add and register the versioned `spec-status/1.0` schema; retire context/current-issue contracts and tests. (`src/specle/schemas/`, `src/specle/schema_registry.py`, `tests/test_schema_registry.py`)
- [x] 2. Implement active/archive discovery, stable-name resolution, and an ignored local current-spec selector. (`src/specle/spec_state.py`, `tests/test_lifecycle.py`)
- [x] 3. Refactor lifecycle and CLI validation around durable per-spec records and verbose active/archive selection reporting. (`src/specle/lifecycle.py`, `src/specle/main.py`, tests)
- [x] 4. Migrate repository records to `status.json`, archive completed specs, preserve delivery/relationship evidence, and retire shared runtime files. (`.specle/`)
- [x] 5. Document the state model, archive finalisation, and worktree-local selection. (`docs/`, `src/specle/blueprints/policies/`)
- [x] 6. Refactor workflow blueprints to resolve stable names, mutate target status only, and remove the obsolete context command. (`src/specle/blueprints/skills/`)
- [x] 7. Remove stale managed skills on forced installation, synchronise `.agents/`, and rebuild the skill index. (`src/specle/inventory.py`, `.agents/`, tests)
- [x] 8. Verify with `specle validate --verbose`, `pytest`, `ruff check`, `ruff format --check`, and `ty check`.
- [x] 9. Separate package-owned policies from user-owned steering; migrate this repository and make installation initialise only local runtime ignore rules. (`src/specle/inventory.py`, blueprints, `.agents/`, tests)
- [x] 10. Close state-transition gaps for activation, spikes, delivery finalisation, archive-aware summaries, pending reporting, and duplicate stable-name blocking. (`src/specle/`, blueprints, docs, tests)
- [x] 11. Rebuild the active inventory and re-run all project checks after the review revision. (`.agents/`, tests)
