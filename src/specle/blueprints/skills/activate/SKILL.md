---
name: activate
specle_group: Planning
requires:
  - estimate
  - design
  - tasks
  - spike
  - build
description: >-
  Explicitly select and commence an unselected normal change.
usage: >-
  Use with a named unselected normal change to select it in this worktree and begin its planning lifecycle.
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
---

# Activate a normal change

Make an explicitly named unselected normal change the local work item. Activation is the boundary between planning a change and commencing it.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-change` when present, the named active directory under `.specle/changes/`, its `status.json`, and `.agents/policies/lifecycle.md`.
2. Require an explicit active directory with that exact name. A normal change may be activated from `defined`, `estimated`, `designed`, or `planned`; a spike may be activated from `defined` or resumed from `spiking`. Do not activate a bugfix, refactor, archived change, or unrecorded directory.
3. If `.specle/current-change` selects another change that is not effectively complete, stop and ask the user to resolve it; never replace that local selection implicitly. A confirmed final delivery event makes a selected item effectively complete pending archive finalisation.
4. Write only the selected name and trailing newline to ignored `.specle/current-change`. Set `activated_at` to the current ISO 8601 timestamp with UTC offset when it is `null`; retain the first activation timestamp on later resumes. This is the sole workflow writer of the selector.
5. For a spike, immediately invoke `spike <change-name>`; the spike skill owns its durable progress and completion.
6. For a normal change, validate the preparation chain in order, then immediately invoke the first missing stage with the selected change name:
   - no `estimate.md` — `estimate`;
   - no `design.md` — `design`;
   - no `tasks.md` — `tasks`;
   - all three artifacts exist — set `status` to `planned` if it is not already planned, then invoke `build`.
   A task plan without a design is not build-ready: invoke design first, then reconcile tasks after design. Do not skip a preparation stage based on T-shirt size.
   Activation deliberately commences the selected change and invokes this stage regardless of manual or decision-gated progression policy.

## Boundaries

- `define` and `spike` create planning artifacts only; neither writes `.specle/current-change`.
- Do not implement, commit, or make external writes.
- Preserve all unrelated changes and status records.

## Next

- The next planning or build stage is invoked by activation.
