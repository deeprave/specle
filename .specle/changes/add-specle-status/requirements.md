# Requirements: Add Specle status

## Problem

The installed `status` skill can orient an agent to selected change work and the local Git worktree, but that orientation is not available to people or tools through the `specle` CLI.

## Intended outcome

`specle status` provides a concise, read-only report of the currently selected change, locally registered active sidecars, the derived next action, compact Git worktree state, and concise optional hand-off context.

## Scope

- Add a `status` CLI subcommand and update the installed and packaged `status` skills so both present the same information.
- Reuse the durable change-state and lifecycle readers used by existing CLI reporting.
- Report the local selector’s valid active or archived target; report an invalid selector without repairing or inferring it.
- Use the local sidecar registry as the authority for active sidecars, regardless of delivery links; show each sidecar with name, kind, status and next action.
- Display available lifecycle timestamps from the selected record without inventing terminal events.
- Summarise optional `.specle/context.json`: show milestones first, then todos and other lists of objects. Group consecutive entries by date and change or subject, indent details, and keep plain-text lines shorter than 80 characters.
- Report the current branch or detached HEAD, plus a compact count of modified, added, deleted, renamed, and untracked worktree entries.

## Boundaries

- The command is read-only: it does not select, repair, mutate, activate, or otherwise advance change work.
- It does not enumerate every pending change; `specle changes` remains the inventory command.
- It does not list individual changed paths unless a later change adds an explicit verbose mode.
- Treat context as optional display data; do not introduce a milestone store or a validation workflow.

## User stories

### 1. Orient to selected work

As a developer, I want `specle status` to show the selected change’s name, kind, current stage, recent lifecycle milestones, and derived next action so I can quickly understand what work is active.

#### Acceptance criteria

1. WHEN a valid current-change selector identifies an active or archived record THEN `specle status` SHALL report its name, kind, recorded lifecycle status, derived next action, and available durable lifecycle timestamps.
2. WHEN no current-change selector exists THEN `specle status` SHALL report that no change is in progress without inferring a replacement.
3. WHEN the selector is invalid or its target lacks a valid status record THEN `specle status` SHALL report the invalid local selection without modifying it.

### 2. Show locally active sidecars

As a developer, I want to see the sidecars active in this worktree regardless of delivery links.

1. WHEN the local sidecar registry contains active sidecars THEN show each once with its name, kind, lifecycle status and derived next action using the same labelled format as the selected change.
2. WHEN a sidecar is not registered locally THEN do not present it as locally active based on a relationship or directory.

### 3. Inspect compact worktree state

As a developer, I want the status report to show my branch and how much uncommitted work exists so I can judge whether the checkout is ready for another action.

#### Acceptance criteria

1. WHEN Git inspection succeeds THEN `specle status` SHALL report the current branch, or detached HEAD, and whether the worktree is clean.
2. WHEN the worktree is not clean THEN `specle status` SHALL report compact counts for modified, added, deleted, renamed, and untracked entries without listing paths.
3. WHEN a Git inspection command fails THEN `specle status` SHALL report that individual detail as unavailable while continuing to report other available status information.

### 4. Summarise optional context

As a developer, I want a compact view of recent context without opening the hand-off document.

1. WHEN context milestones exist THEN display them first, grouped by date without time and change, with indented details.
2. WHEN todos exist THEN display them after milestones, grouped by date without time and subject, with indented details when present.
3. WHEN other keys contain lists of objects THEN display them after todos, grouped by date and subject, with indented details when present.
4. Avoid repeating dates and change names or subjects until they change. Plain-text context lines SHALL be shorter than 80 characters; Markdown labels may exceed that limit. Truncate details only as needed and tolerate absent optional fields.
5. Missing optional context SHALL NOT prevent other status output. The command SHALL display status rather than perform additional validation.

### 5. Keep status interfaces aligned

1. THE `status` skill and `specle status` SHALL present the same categories of change, sidecar, worktree and optional context information, including the same date-only grouping and context line-length limits.
2. THE installed and packaged skill instructions SHALL remain aligned.

### 6. Markdown output

WHEN invoked with `--markdown`, `specle status` SHALL output Markdown source with headings and grouped context bullets; plain text remains the default.
