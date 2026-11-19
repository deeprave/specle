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

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the affected tasks and spec artefacts. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

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

After recording a complete plan, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `build <spec-name>`; otherwise report it and wait.

- `build` — start executing the tasks with TDD.
- `verify` — confirm the tasks cover every acceptance criterion.
