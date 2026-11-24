# Tasks: Solve perpetual open completion change

- [x] 1. Add a schema regression covering completion PR identity without a completion event. (`tests/test_schema_registry.py`)
- [x] 2. Remove completion events and their open-event lifecycle semantics from completion, wrapup, changelist, status, activation, triage, resolve, commit, and lifecycle guidance in installed and blueprint copies; clarify that wrapup is explicit completion-PR handling rather than a lifecycle transition. (`src/specle/schemas/change-status/1.0.json`, `.specle/archive/`, `.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 3. Make `complete` remove explicitly fulfilled dependencies from active records as part of its existing archival-finalisation commit, preserving unrelated dependencies and lifecycle metadata. (`.agents/skills/complete/SKILL.md`, `.agents/policies/lifecycle.md`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
