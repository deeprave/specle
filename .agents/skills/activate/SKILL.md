---
name: activate
specle_group: Planning
requires:
  - estimate
  - design
  - tasks
  - spike
  - build
  - bugfix
  - refactor
description: >-
  Commence a named change using the workflow appropriate to its kind.
usage: >-
  Use with a named normal change, spike, bugfix, or refactor to begin or resume its applicable workflow.
lifecycle:
  accepts:
    - defined
    - estimated
    - designed
    - planned
    - spiking
  transitions:
    - from:
        status: defined
        kind: change
      to:
        status: defined
        kind: change
      next: estimate
    - from:
        status: defined
        kind: bugfix
      to:
        status: planned
        kind: bugfix
      next: build
    - from:
        status: defined
        kind: refactor
      to:
        status: planned
        kind: refactor
      next: build
    - from:
        status: planned
        kind: bugfix
      to:
        status: planned
        kind: bugfix
      next: build
    - from:
        status: planned
        kind: refactor
      to:
        status: planned
        kind: refactor
      next: build
---

# Activate a change

Commence an explicitly named change using the route for its kind. Normal changes and spikes are selected; bugfixes and refactors remain non-selected.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-change` when present, the named active directory under `.specle/changes/`, its `status.json`, `.agents/policies/{lifecycle,context}.md`, and applicable `.agents/project/context.md`. Context remains optional and never blocks activation.
2. Require an explicit active directory with that exact name. A normal change may be activated from `defined`, `estimated`, `designed`, or `planned`; a spike may be activated from `defined` or resumed from `spiking`; a bugfix or refactor may be activated from `defined` or `planned`. Reject archived, missing, terminal, ineligible, and unsupported kinds with a clear diagnostic.
3. For a normal change or spike, if `.specle/current-change` selects another change that is not terminal, stop and ask the user to resolve it; never replace that local selection implicitly. An archived complete record with an unconfirmed original or recovery delivery PR remains resumable through `complete` and blocks replacement. An archived cancelled record is terminal and may be replaced.
4. For a normal change or spike, write only the selected name and trailing newline to ignored `.specle/current-change`. Set `activated_at` to current Unix seconds as a JSON number when it is `null`, retain the first activation timestamp on later resumes, and write `updated_at` in the same status update. Activation is the sole selector writer except for complete's matching post-merge cleanup and cancel's matching terminal cleanup.
5. For a named bugfix or refactor, preserve `.specle/current-change` even when absent. Read the abbreviated `spec.md` and `tasks.md`; invoke the owning `bugfix` or `refactor` with the internal preparation-only hand-off to complete missing prerequisites and return here. On failure stop without marking the target ready. Once ready, set the record to `planned` if needed and update `updated_at`. Register the sidecar in the worktree-local registry as specified by lifecycle policy. If a normal change is selected, automatically link the pair using the procedure below before proceeding; then invoke `build <change-name>` and return. Do not audit, stash, or move the user’s work.
6. For a spike, immediately invoke `spike <change-name>` and return; the spike skill owns its durable progress and completion.
7. For a normal change, inspect the worktree-local sidecar registry. For each valid unlinked active sidecar, automatically link the pair using the procedure below before continuing. Report stale entries and do not infer activity from other worktrees or queued records.
8. For a normal change, validate the preparation chain in order, then immediately invoke the first missing stage with the selected change name:
   - no `estimate.md` — `estimate`;
   - no `design.md` and estimate is M/L/XL — `design`;
   - no `tasks.md` — `tasks`;
   - required artifacts exist — set `status` to `planned` if it is not already planned, then invoke `build`.
   S-sized normal changes skip design; M/L/XL changes require design before tasks. If the estimate is missing or unclear, resolve it before proceeding.
   Activation deliberately commences the selected change and invokes this stage regardless of manual or decision-gated progression policy. `build` owns the sole confirmation boundary before implementation.

## Link concurrent work

For each eligible concurrently active parent/sidecar pair, automatically establish its reciprocal joint-delivery relationship without a prompt. Re-read both status records, validate kinds and existing relationships, and update the pair in a recoverable way as required by lifecycle policy. A matching pair is a no-op; report conflicts without overwriting or leaving half a pair. Do not audit which code the user includes in a delivery or automatically stash or move work. Completion determines whether links remain after together or separate delivery.

## Local sidecar stop

When the user explicitly asks to stop local work on a named sidecar, remove only that name from the worktree-local registry under lifecycle policy. This is not cancellation: preserve its durable status, relationships, selection, and files. A later activation or named build registers it again.

## Boundaries

- `define` and `spike` create planning artifacts only; neither writes `.specle/current-change`.
- Do not implement, commit, or make external writes.
- Preserve all unrelated changes and status records.

## Next

- The next planning or build stage is invoked by activation.
