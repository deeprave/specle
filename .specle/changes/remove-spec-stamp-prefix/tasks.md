# Tasks: remove spec stamp prefix

- [x] 1. Define failing change-state and schema contract tests.
  - [x] 1.1 Add tests for slug-only active/archive directories, cross-collection collision rejection, and `current-change` selection.
  - [x] 1.2 Add schema and runtime tests for `change-status`, required `created_at`, nullable `activated_at`, relationship `change`, and findings `outcome_change`.

- [x] 2. Rename the state reader and schema contracts.
  - [x] 2.1 Rename `spec_state.py` and its public types/helpers to change-state terminology, update callers, and scan `.specle/changes/`.
  - [x] 2.2 Replace the `spec-status` schema resource and registry contract with `change-status`; add timestamp and renamed structured-field validation with no fallback aliases.

- [x] 3. Update selection and change creation behaviour.
  - [x] 3.1 Rename the ignored selector and runtime handling to `current-change`; preserve the sole-writer activation boundary.
  - [x] 3.2 Rename the `spec` skill to `define`, update its creation path and lifecycle metadata, and record creation/first-activation timestamps.

- [x] 4. Rename tracked active and archived change records.
  - [x] 4.1 Move active directories to `.specle/changes/` and rename all active/archive directories to slugs, rejecting or resolving no collisions by inspection before the move.
  - [x] 4.2 Update status records, structured review/finding references, dependencies, relationships, summaries, tracker data, and durable selector state without retaining old identifiers.

- [x] 5. Update workflow guidance, packaged inventory, and generated resources.
  - [x] 5.1 Replace work-item terminology and paths in blueprint policies, skills, docs, tests, and runtime diagnostics while preserving `Specle` and `spec.md` references.
  - [x] 5.2 Synchronise the active `.agents/` inventory from the blueprints and regenerate `skills/specle/index.json`; prove `define` replaces `spec`.

- [x] 6. Add regression coverage for direct-renamed behaviour.
  - [x] 6.1 Cover change creation collisions, timestamp preservation, and selector validation through public runtime behaviour.
  - [x] 6.2 Cover package/index validation and schema export after the renamed resources and inventory are in place.

- [x] 7. Audit the final repository state and run complete verification.
  - [x] 7.1 Search tracked source and state for unintended work-item `spec` terminology, excluding the product name `Specle` and literal `spec.md` references.
  - [x] 7.2 Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, blueprint validation, installed-target validation, and whitespace validation.

- [x] 8. Implement accepted external-review revisions.
  - [x] 8.1 Add custom timestamp normalization for naive and offset-aware ISO 8601 input plus millisecond and nanosecond epochs; update the status contract and production tests for current accepted forms.
  - [x] 8.2 Replace ASCII-only change-name validation with Unicode word components separated by ASCII hyphen-minus, and cover current valid/invalid component behavior.
  - [x] 8.3 Update the project-local changelog skill and rewrite remaining active-document and structured-record references to current change names.
  - [x] 8.4 Regenerate the active inventory if needed and repeat the complete verification and review cycle.

- [x] 9. Canonicalize durable timestamps after local review.
  - [x] 9.1 Normalize accepted timestamp input to Unix seconds and reject date-only input; require numeric durable timestamps in the schema and reader.
  - [x] 9.2 Convert tracked status timestamps and update workflow writers in both blueprint and installed skills.
  - [x] 9.3 Cover the current timestamp contract and repeat verification and review.

- [x] 10. Apply accepted follow-up review corrections.
  - [x] 10.1 Keep timestamp normalization at explicit write boundaries and reject noncanonical durable timestamps.
  - [x] 10.2 Require NFC names, detect case-folded collisions, and reject Windows-reserved names.
  - [x] 10.3 Cover the corrected runtime contracts and repeat verification and review.
