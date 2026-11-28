---
name: build
specle_group: Implementation
description: >-
  Implement active Specle tasks with TDD.
usage: >-
  Use for a planned or building normal change or explicitly named bugfix or refactor; execute its tasks and continue to verification.
lifecycle:
  accepts:
    - planned
    - building
    - review-findings
  transitions:
    - from: planned
      to: building
      next: build
    - from: building
      to: building
      next: verify
    - from: review-findings
      to: building
      next: verify
---

# Build change tasks

Work through the target change’s tasks one at a time, keeping its tracking files in sync. Apply test-first bugfix work and behaviour-preserving refactor safeguards.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-change` when present, the selected target's `status.json`, `.agents/policies/lifecycle.md`, applicable `.agents/steering/` overrides, and the relevant authoritative `.agents/project/` documents. Default to the selected normal change. A named non-selected committed normal target, bugfix, or refactor is permitted only when explicitly requested; update only that target and preserve the local selection. For an abbreviated target, require its kind-specific `spec.md` and `tasks.md` and the explicit reciprocal concurrent-delivery relationship if a different parent is selected. Otherwise report missing prerequisites or direct unlinked work to a separate worktree. Reject archived targets: archival records are immutable and cannot be built.
2. Run a lifecycle preflight before reading or changing `tasks.md`:
   - `defined` — advise `activate <change-name>` for abbreviated work or `estimate` for normal work.
   - `estimated` — stop and advise `design`.
   - `designed` — stop and advise `tasks`.
   - `planned`, `building`, or `review-findings` — continue only when `tasks.md` exists and has an
     uncompleted task.
   - `verified` — stop and advise `review`.
   - `complete` — stop and report that no build work remains.
   - Any missing, inconsistent, or unrecognised lifecycle state — stop and report the status-record defect.
   If `review-findings` has no uncompleted task, advise `triage` so the reviewed decisions
   can be routed and recorded. If `planned` or `building` has no uncompleted task, advise `verify`.
3. For a `planned` normal change, read its `spec.md`, `requirements.md`, `estimate.md`, `tasks.md`, and `design.md` when required or present, then present a concise alignment summary: intended outcome, scope and non-goals, acceptance direction, planned tasks, and material assumptions or limits. Require the user's explicit confirmation before changing implementation, task completion, or lifecycle state. This is a mandatory stop in every progression mode, including decision-gated. If the user corrects the summary, stop for revision rather than commencing the build.
4. For an explicitly named bugfix or refactor, register its name idempotently in the worktree-local sidecar registry under lifecycle policy before implementation. Preserve other entries and the normal selection; if registry validation or update fails, report it and stop. Read `tasks.md`; find the first uncompleted task (`- [ ]`).
5. For each task, in order:
   a. For a bugfix, reproduce the defect and write a failing regression test before the fix. For a refactor, establish its baseline and behaviour-preserving invariants before restructuring; retain equivalent coverage. For normal changes, use test-first development.
   b. Implement the task without speculative changes or intentional behaviour changes for refactors.
   c. Run the focused test and any project checks needed to keep the change safe.
   d. Mark the task complete: change `- [ ]` to `- [x]` in `tasks.md`.
   e. Update the target `status.json` with the new progress, the `building` transition, and current Unix-second `updated_at`. Invalidate
      prior verification and review evidence as `stale` when this task changes implementation.

## Critical

- Do not implement, create tasks, or change lifecycle state when the preflight says another skill
  is required.
- Always update `tasks.md` and the target `status.json` after each task.
- Use the project's documented command runner and non-interactive flags.
- Never delete the `.agents/` folder or its contents.

## Next

After all tasks complete, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `verify <change-name>`; otherwise report it and wait.

- When all tasks are complete: use `verify <change-name>` to confirm the implementation against the change.
- Use `review` for a quality pass on the diff.
