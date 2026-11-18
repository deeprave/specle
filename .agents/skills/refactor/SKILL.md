---
name: refactor
specle_group: Alternatives
requires: []
description: >-
  Restructure code without changing observable behaviour.
usage: >-
  Use for structural cleanup protected by documented invariants and tests; use spec when new behaviour is needed.
---

# Refactor (no behaviour change)

Improve structure while keeping behaviour identical, with explicit invariants and tests as the guardrail, without displacing unrelated active work.

## Workflow

1. Read `.specle/current-issue.json` and `.specle/context.json`. Preserve the recorded active current spec; this workflow must not replace it.
2. Read the relevant authoritative `.agents/project/` documents and the codebase area being refactored.
   If the user names an existing queued refactor, locate its matching `kind: "refactor"` record and read its `spec.md` and `tasks.md`; reuse those artefacts and skip directly to step 6. Do not create another directory or queued record.
3. Create a spec folder `.specle/specs/YYYYMMDDHHMM-{slug}/` with a short `spec.md` containing:
   - Current state and target state.
   - Behavioural invariants that must remain true.
   - Baseline or characterisation evidence to establish before restructuring.
   - Refactor approach.
4. Add a matching `queued_specs` record to `.specle/context.json` with `kind: "refactor"`, `status: "defined"`, and `next: "refactor"`. Do not change `current_spec` or `.specle/current-issue.json`.
   When active work exists, do not execute unlinked abbreviated work in that worktree. Require an explicit relationship to the active spec before execution, or direct the user to `prepare` it for later named execution in a separate worktree. A linked sidecar records its origin `spec_path`, relationship `type`, and `"delivery": "with-related-spec"`.
5. Create `tasks.md` with incremental steps:
   - Confirm the relevant baseline tests pass or add focused characterisation coverage.
   - Record the behaviour-preserving invariants for each affected area.
   - Make one small cohesive production-code or test-code restructure at a time.
   - Run focused checks after every cycle, then repeat until the target structure is reached.
   - Run the documented quality gates before verification.
6. Before implementation while active work exists, require the user to establish the explicit relationship in step 4; otherwise prepare the refactor without implementation and direct later named execution in a separate worktree.
7. If the user asks to prepare the refactor without implementation, update only the matching queued record to `status: "planned"` and `next: "implement"`, then report its generated timestamped name and stop. Later `implement` and `verify` requests must name that refactor explicitly.
8. Otherwise, execute the linked tasks immediately; mark them `- [x]` as you go. Update only the matching queued record to `status: "building"` and `next: "verify"` when implementation starts.

## Critical

- Do not intentionally change observable behaviour or add features. If that becomes necessary, stop and use the normal `spec` workflow.
- Tests may be restructured alongside production code, including renaming fixtures, helpers, and test cases that expose renamed internals, when their coverage remains equivalent or stronger for the recorded invariants.
- A refactor is non-active work. Never replace the active feature's `current_spec` or `.specle/current-issue.json`.

## Next

- `implement` — resume a prepared named refactor.
- `verify` — verify the named refactor against its abbreviated contract and update its queued record without activating it.
