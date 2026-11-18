---
name: tasks
specle_group: Planning
requires: []
description: >-
  Generate task plans from normal specs and designs.
usage: >-
  Use after normal requirements and any necessary design exist to create or reconcile an ordered TDD task plan; do not infer completed work from a diff.
---

# Generate implementation tasks

Produce a `tasks.md` of atomic, independently verifiable, test-first tasks for the current spec,
matching the existing `tasks.md` files in `.specle/specs/`.

## Workflow

1. Read `.specle/context.json` and `.specle/current-issue.json` to locate the active spec.
2. Read `requirements.md`, `spec.md`, and `design.md` if present (for architecture and dependency
   ordering).
   Read applicable authoritative `.agents/project/` documents for project constraints that the
   implementation tasks must preserve.
3. Inspect relevant repository changes before planning: use `git status --short`, staged and unstaged diffs, and recent commits for the code affected by the spec. Account for relevant existing implementation or partial work, but ignore unrelated changes.
4. Write or reconcile `tasks.md` in the spec folder:
   - Checkbox format: `- [ ] N. <task>` with nested `- [ ] N.M` subtasks.
   - **TDD**: each implementation slice is "add tests" then "implement", never implementation first.
   - Logical ordering (data/records → processor → report/output → CLI wiring).
   - Note the files each task touches.
   - Do not mark a task complete solely because a diff or existing code appears to satisfy it; reconcile that evidence into the plan and leave completion to `build` and `verify`.
5. Update `.specle/context.json` with the top-level task count (`0/N`) and set the active spec
   status to `planned` according to `context.md` and `lifecycle.md`.

Tasks must be atomic and independently verifiable — one behavior per cycle.

## Next

- `build` — start executing the tasks with TDD.
- `verify` — confirm the tasks cover every acceptance criterion.
