---
name: status
specle_group: Coordination
requires: []
description: >-
  List pending and active Specle work with next stages.
usage: >-
  Use to inventory unfinished, active, queued, or dependent work and report its recorded next step; it never changes lifecycle state.
---

# List pending specs

Produce a read-only inventory of actionable specs under `.specle/specs/`. Do not change
`.specle/current-issue.json`, `.specle/context.json`, spec files, or the working tree.

## Workflow

1. Read `.specle/current-issue.json`, `.specle/context.json`, and `.agents/steering/lifecycle.md` first.
   Include the active spec whenever its recorded lifecycle status is not `complete`.
2. Enumerate immediate directories under `.specle/specs/`, ordered by their directory name.
3. For each spec, inspect `tasks.md` when present. Count Markdown task boxes at any indentation
   level:
   - no `tasks.md` — report its recorded lifecycle state when available, otherwise **defined**;
   - use checkbox counts only as progress; never infer lifecycle status or completion from them.
4. Report a compact table headed **Pending specs** with **Kind**, **Status**, **Spec**, **Size**,
   **Depends on**, **Progress**, and **Next** columns:
   - read `kind` from the matching current, queued, or recent context record; display `change`
     when a legacy record omits it;
   - display the spec's slug without its leading `YYYYMMDDHHMM-` directory prefix;
   - read the T-shirt size from `estimate.md` when present, otherwise display `—`;
   - read explicit dependencies from the queued-spec context record or an `## Dependencies`
     section in `estimate.md`, listing their short spec slugs, otherwise display `—`;
   - use the recorded lifecycle state as the status;
   - report checkbox progress only when `tasks.md` exists; and
   - use the matching context record's explicit non-empty `next` value when present; otherwise derive the next skill from recorded lifecycle status and kind using `lifecycle.md`.
5. After the table, state the count and identify the current spec and its recorded lifecycle status.
   If there are no pending entries, say so directly.

For the active spec, also list declared related sidecars: queued records whose `relationship.spec_path`
matches the active path. Show their relationship type, delivery mode, status, and next step. Do not infer
sidecars from shared files, ordering, or worktree state.

Also include any completed spec that is an explicit dependency of a pending spec, with `Next` shown
as `—`. Do not count that dependency-context row as pending work.

Task completion alone is not proof that an older spec was verified, reviewed, or committed. If the
user asks for a full audit, add a separate **Task-complete specs** section for omitted entries and
label them as requiring historical verification rather than calling them complete.

## Boundaries

- This is an inventory command, not a substitute for `verify`.
- Never activate, archive, edit, or delete a spec while listing it.
