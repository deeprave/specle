---
name: bugfix
specle_group: Alternatives
requires: []
description: >-
  Fix bounded defects with abbreviated test-first work.
usage: >-
  Use for a clear, bounded defect that needs a reproduction and regression test; use spec when the work introduces new behaviour or broader scope.
---

# Bugfix (abbreviated TDD)

Resolve a defect with a lightweight, reproduce-first flow without displacing unrelated active work.

## Workflow

1. Read `.specle/current-issue.json` and `.specle/context.json`. Preserve the recorded active
   current spec; this workflow must not replace it.
2. Read the relevant authoritative `.agents/project/` documents, then understand the bug from the description and inspect the codebase to find the relevant area.
   If the user names an existing queued bugfix, locate its matching `kind: "bugfix"` record and read its `spec.md` and `tasks.md`; reuse those artefacts and skip directly to step 6. Do not create another directory or queued record.
3. Create a spec folder `.specle/specs/YYYYMMDDHHMM-{slug}/` with a short `spec.md` containing:
   - Bug description.
   - Expected behaviour and actual behaviour.
   - Steps to reproduce, if inferable.
   - Root-cause analysis and fix approach.
   - Regression-test evidence to establish during the work.
4. Add a matching `queued_specs` record to `.specle/context.json` with `kind: "bugfix"`,
   `status: "defined"`, and `next: "bugfix"`. Do not change `current_spec` or
   `.specle/current-issue.json`.
   When active work exists, do not execute unlinked abbreviated work in that worktree. Require an
   explicit relationship to the active spec before execution, or direct the user to `prepare` it
   for later named execution in a separate worktree. A linked sidecar records its origin `spec_path`,
   relationship `type`, and `"delivery": "with-related-spec"`.
5. Create `tasks.md` (test-first):
   - Write a failing test that reproduces the bug.
   - Implement the fix.
   - Confirm existing tests still pass.
6. Before implementation while active work exists, require the user to establish the explicit relationship in step 4; otherwise prepare the bugfix without implementation and direct later named execution in a separate worktree.
7. If the user asks to prepare the bugfix without implementation, update only the matching queued record to `status: "planned"` and `next: "bugfix"`, then report its generated timestamped name and stop. Later `bugfix` and `verify` requests must name that bugfix explicitly.
8. Otherwise, execute the linked tasks immediately (TDD); mark them `- [x]` as you go. Update only the matching
   queued record to `status: "building"` and `next: "verify"` when implementation starts.

## Critical

- Write the failing test **first**, then fix. A bug fix without a regression test is incomplete.
- Run the regression test and the project's documented quality gates.
- A bugfix is non-active work. Never replace the active feature's `current_spec` or
  `.specle/current-issue.json`.

## Next

- `bugfix <spec-name>` — resume a prepared named bugfix.
- `verify` — verify the named bugfix against this abbreviated contract and update its queued record without activating it.

After successful execution, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `verify <spec-name>`; otherwise report it and wait.
