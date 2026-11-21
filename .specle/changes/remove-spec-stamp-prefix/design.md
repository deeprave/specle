# Design: remove spec stamp prefix

## Overview

Replace timestamp-prefixed work-item directories with short unique change slugs. Active changes move from `.specle/specs/` to `.specle/changes/`; archived changes remain in `.specle/archive/`. Rename work-item state and workflow terminology from `spec` to `change`, while retaining the product name `Specle` and the literal planning document `spec.md`.

## Architecture

```text
.specle/changes/<slug>/status.json ─┐
.specle/archive/<slug>/status.json ─┼─ change-state reader ─ lifecycle validation
.specle/current-change              ┘

change-state schema ─ schema registry ─ status validation
define skill ─ creates an unselected change
```

Rename `spec_state.py` to `change_state.py` and its public types and helpers to `ChangeRecord`, `ChangeStateSnapshot`, `read_change_state`, `resolve_change`, and `selected_change`. The reader scans `.specle/changes/` and `.specle/archive/`, validates one filesystem-compatible Unicode name component whose words are separated by ASCII hyphen-minus, and rejects duplicate names across both collections. The ignored selector becomes `.specle/current-change` and contains one active change name.

Rename the schema resource and registry key from `spec-status` to `change-status`. Its `status.json` contract gains required `created_at` and `activated_at` fields. A custom timestamp normalizer accepts full naive or offset-aware ISO 8601 datetimes and millisecond or nanosecond Unix epochs, then returns Unix seconds as a JSON number, using a fractional value only for sub-second precision. Workflow writers persist that canonical number; the reader also normalizes accepted input before exposing a record. Date-only input is invalid. `activated_at` is otherwise `null`. Relationship `spec` becomes `change`. The findings schema changes `outcome_spec` to `outcome_change`; structured review references become `resulting_change`.

## Repository update

This is a direct tracked-source update, not a distributed migration feature. Rename all six active and seventeen archived directories, rewrite all structured references, and remove every old path or identifier. Convert historical timestamp values to Unix seconds; set historical `activated_at` to `null` unless tracked state proves an activation time. Set the newly selected change's `activated_at` at activation. Do not add aliases, fallback readers, compatibility schema identifiers, or a migration command.

Rename `src/specle/blueprints/skills/spec/` to `define/`, update frontmatter, lifecycle declarations, direct dependencies, all skill references, and the installed mirror. `define` continues to create an unselected normal change with `requirements.md`, `spec.md`, and initial `status.json`. It owns collision preflight; `activate` owns first-activation timestamp preservation. These are agent-enforced workflow rules rather than Python runtime validation.

## Error handling

- Reject invalid active or archive change-name components with a concise runtime diagnostic.
- Reject a duplicate name across active and archive collections; never choose one based on collection or modification time.
- Reject status records that omit a timestamp or use an unaccepted timestamp input form, including date-only strings.
- `define` fails before writing when its name appears in either collection.
- A missing `current-change` remains valid; a selector naming an archived or unknown change is invalid.

## Test strategy

- Test Unicode change-name validation and duplicate-name diagnostics without asserting retired names are rejected.
- Test custom timestamp normalization to canonical Unix seconds for naive and offset-aware ISO 8601 datetimes and millisecond/nanosecond epochs, including `activated_at: null` and rejected date-only input.
- Test direct skill inventory/index output contains `define` and no `spec` skill.
- Test repository state and schema registry validation after the tracked-directory and structured-reference update, including the project-local changelog guidance.
- Run `pytest`, `ruff check`, `ruff format --check`, `ty`, blueprint validation, installed-target validation, and a deliberate stale-term inventory limited to work-item vocabulary.
