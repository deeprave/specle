# Tasks: Cleanup complete

- [x] 1. Add focused regression coverage for the revised completion lifecycle: same-PR correction loops, archive-before-final-merge finalisation, later synchronisation through `complete`, and removal of the `wrapup` inventory entry. (`tests/test_lifecycle.py`, `tests/test_inventory_metadata.py`)
- [x] 2. Preserve the `delivery.completion` contract with schema coverage for immutable original-PR finalisation evidence and rejection of a completion event. (`src/specle/schemas/change-status/1.0.json`, `tests/test_schema_registry.py`)
- [x] 3. Replace branch-delivery `complete` guidance in installed and blueprint skills so it archives, records completion evidence, pushes to the original PR, requests auto-merge, and later resumes synchronisation without a second PR. (`.agents/skills/complete/SKILL.md`, `src/specle/blueprints/skills/complete/SKILL.md`)
- [x] 4. Remove the managed `wrapup` skill and every retired archival-feedback lifecycle route, then revise lifecycle, delivery, commit, triage, resolve, status, summary, and reporting guidance for one-PR completion while preserving external-feedback handling on the original PR. (`.agents/`, `src/specle/blueprints/`, `docs/LIFECYCLE.md`)
- [x] 5. Regenerate the installed skill index and validate installed/blueprint inventory alignment after the removal. (`.agents/skills/specle/index.json`)
- [x] 6. Confirm historical archived records remain untouched, run focused regressions and all project quality gates, then validate installed and blueprint Specle distributions.
