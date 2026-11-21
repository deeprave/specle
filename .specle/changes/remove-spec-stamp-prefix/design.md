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

Rename `spec_state.py` to `change_state.py` and its public types and helpers to `ChangeRecord`, `ChangeStateSnapshot`, `read_change_state`, `resolve_change`, and `selected_change`. The reader scans `.specle/changes/` and `.specle/archive/`, validates a short slug pattern, and rejects duplicate slugs across both collections. The ignored selector becomes `.specle/current-change` and contains one active slug.

Rename the schema resource and registry key from `spec-status` to `change-status`. Its `status.json` contract gains required `created_at` and `activated_at` fields. `created_at` is an ISO 8601 date-time with explicit offset; `activated_at` is either the same shape or `null`. Relationship `spec` becomes `change`. The findings schema changes `outcome_spec` to `outcome_change`; structured review references become `resulting_change`.

## Repository update

This is a direct tracked-source update, not a distributed migration feature. Rename all six active and seventeen archived directories, rewrite all structured references, and remove every old path or identifier. Existing timestamp prefixes encode the creation minute only; write that minute with the project-local explicit offset into `created_at`. Set historical `activated_at` to `null` unless tracked state proves an activation time. Set the newly selected change's `activated_at` at activation. Do not add aliases, fallback readers, compatibility schema identifiers, or a migration command.

Rename `src/specle/blueprints/skills/spec/` to `define/`, update frontmatter, lifecycle declarations, direct dependencies, all skill references, and the installed mirror. `define` continues to create an unselected normal change with `requirements.md`, `spec.md`, and initial `status.json`.

## Error handling

- Reject invalid active or archive directory slugs with a concise runtime diagnostic.
- Reject a duplicate slug across active and archive collections; never choose one based on collection or modification time.
- Reject status records that omit or malformedly encode either timestamp or use the retired `change-status` contract incorrectly.
- Creation fails before writing when its slug appears in either collection.
- A missing `current-change` remains valid; a selector naming an archived or unknown change is invalid.

## Test strategy

- Test slug-only creation, cross-collection collision rejection, selection through `current-change`, and duplicate-slug diagnostics.
- Test the renamed schema, timestamps, relationship and findings field validation, including `activated_at: null` and preservation after reactivation.
- Test direct skill inventory/index output contains `define` and no `spec` skill.
- Test repository state and schema registry validation after the tracked-directory and structured-reference update.
- Run `pytest`, `ruff check`, `ruff format --check`, `ty`, blueprint validation, installed-target validation, and a deliberate stale-term inventory limited to work-item vocabulary.
