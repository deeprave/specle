---
name: prepare
specle_group: Alternatives
requires: [bugfix, refactor]
description: >-
  Prepare non-active bugfixes or refactors for later work.
usage: >-
  Use to create an explicitly named queued repair or behaviour-preserving restructure without implementation changes.
---

# Prepare abbreviated side work

Create a named, implementation-ready bugfix or refactor without executing its tasks or changing the active current issue.

## Workflow

1. Read `.specle/current-issue.json`, `.specle/context.json`, the relevant steering, and applicable authoritative `.agents/project/` documents.
2. Determine the work kind. Use `bugfix` for a bounded defect whose intended behaviour is known. Use `refactor` for a behaviour-preserving structural change. Ask the user if that distinction is unclear.
3. Invoke the selected owning workflow in prepare mode. It must create the timestamped spec directory, write the abbreviated `spec.md` and `tasks.md`, and register the matching queued record without executing any task.
4. Confirm the queued record has the generated name and path, the selected `kind`, `status: "planned"`, and `next: "implement"`. Preserve `current_spec` and `.specle/current-issue.json`.
5. Report the exact generated spec name. Later invocation must name that item explicitly: `implement <spec-name>` resumes its tasks, and `verify <spec-name>` verifies it after those tasks are complete.

## Critical

- Never implement code, tests, or task steps in this workflow.
- Do not use this skill for a normal feature, documentation change, or release; use the normal `spec` workflow instead.
- Do not choose an existing queued abbreviated item implicitly.

## Next

- `implement <spec-name>` — resume the prepared bugfix or refactor.
