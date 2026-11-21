# Summary: Simplified Specle change state

## Summary

Specle now uses concise change names instead of timestamp-prefixed directories, with durable timestamps and unambiguous change terminology throughout its workflow.

## Outcome

Active work is stored under `.specle/changes/` and completed work under `.specle/archive/`, both addressed by a short change name. Agents create changes with `define`, select local work through `current-change`, and keep creation and activation times in `status.json`.

## What changed

- Replaced timestamp-prefixed change directories and spec-state terminology with change-oriented paths, schema names, fields, and guidance.
- Added canonical Unix-second timestamps and explicit timestamp normalization for workflow writers.
- Updated change-name validation for Unicode NFC names, case-equivalent collisions, and Windows-reserved names.
- Migrated the managed skill inventory and project changelog guidance to the new terminology.

## Key decisions and limits

- Existing external installations are not supported through compatibility aliases or migration helpers because Specle is unreleased.
- Durable status records must already use canonical numeric timestamps; validation does not reinterpret stored values.
