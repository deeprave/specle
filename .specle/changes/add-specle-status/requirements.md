# Requirements: Add Specle status

## Problem

The installed `status` skill can orient an agent to selected change work and the local Git worktree, but that orientation is not available to people or tools through the `specle` CLI.

## Intended outcome

`specle status` provides a concise, read-only report of the currently selected change, explicitly linked active sidecars, recent durable lifecycle events, the derived next action, and compact Git worktree state.

## Scope

- Add a `status` CLI subcommand.
- Reuse the durable change-state and lifecycle readers used by existing CLI reporting.
- Report the local selector’s valid active or archived target; report an invalid selector without repairing or inferring it.
- For a selected normal change, include only sidecars explicitly declared by that change’s relationships, with their reciprocal-link validity and current lifecycle state.
- Render recent lifecycle events from recorded durable timestamps (`created_at`, `activated_at`, `updated_at`, and applicable terminal timestamps) rather than Git history or inferred task progress.
- Report the current branch or detached HEAD, plus a compact count of modified, added, deleted, renamed, and untracked worktree entries.

## Boundaries

- The command is read-only: it does not select, repair, mutate, activate, or otherwise advance change work.
- It does not enumerate every pending change; `specle changes` remains the inventory command.
- It does not list individual changed paths unless a later change adds an explicit verbose mode.
- “Recent milestones” initially means durable lifecycle timestamps. It does not introduce a new milestone store or consult optional hand-off context.

## User stories

### 1. Orient to selected work

As a developer, I want `specle status` to show the selected change’s name, kind, current stage, recent lifecycle milestones, and derived next action so I can quickly understand what work is active.

#### Acceptance criteria

1. WHEN a valid current-change selector identifies an active or archived record THEN `specle status` SHALL report its name, kind, recorded lifecycle status, derived next action, and available durable lifecycle timestamps.
2. WHEN no current-change selector exists THEN `specle status` SHALL report that no change is in progress without inferring a replacement.
3. WHEN the selector is invalid or its target lacks a valid status record THEN `specle status` SHALL report the invalid local selection without modifying it.

### 2. Show explicitly related active sidecars

As a developer, I want the status report to show active sidecars for selected normal work so I can see joint-delivery state without scanning every change.

#### Acceptance criteria

1. WHEN the selected normal change declares concurrent sidecars THEN `specle status` SHALL report each declared sidecar’s name, kind, lifecycle status, and reciprocal-link validity.
2. WHEN no explicit concurrent sidecar is declared THEN `specle status` SHALL NOT infer a sidecar from directories, branches, files, or task content.

### 3. Inspect compact worktree state

As a developer, I want the status report to show my branch and how much uncommitted work exists so I can judge whether the checkout is ready for another action.

#### Acceptance criteria

1. WHEN Git inspection succeeds THEN `specle status` SHALL report the current branch, or detached HEAD, and whether the worktree is clean.
2. WHEN the worktree is not clean THEN `specle status` SHALL report compact counts for modified, added, deleted, renamed, and untracked entries without listing paths.
3. WHEN a Git inspection command fails THEN `specle status` SHALL report that individual detail as unavailable while continuing to report other available status information.
