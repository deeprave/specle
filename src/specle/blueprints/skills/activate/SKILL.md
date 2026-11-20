---
name: activate
specle_group: Planning
requires:
  - estimate
  - design
  - tasks
  - build
description: >-
  Explicitly select and commence an unselected normal specification.
usage: >-
  Use with a named unselected normal spec to select it in this worktree and begin its planning lifecycle.
lifecycle:
  accepts:
    - defined
  transitions:
    - from:
        status: defined
        kind: change
      to:
        status: defined
        kind: change
      next: estimate
---

# Activate a normal spec

Make an explicitly named unselected normal spec the local work item. Activation is the boundary between planning a spec and commencing it.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-spec` when present, the named active directory under `.specle/specs/`, its `status.json`, and `.agents/steering/lifecycle.md`.
2. Require an explicit spec name. Require an active directory with that exact name, `kind: "change"`, and `status: "defined"`. Do not activate a bugfix, refactor, spike, archived spec, or an unrecorded directory.
3. If `.specle/current-spec` selects another unfinished spec, stop and ask the user to resolve it; never replace that local selection implicitly.
4. Write only the selected name and trailing newline to ignored `.specle/current-spec`. Do not change the selected spec's durable status solely because it was selected.
5. Validate the preparation chain in order, then immediately invoke the first missing stage with the selected spec name:
   - no `estimate.md` — `estimate`;
   - no `design.md` — `design`;
   - no `tasks.md` — `tasks`;
   - all three artifacts exist — `build`.
   A task plan without a design is not build-ready: invoke design first, then reconcile tasks after design. Do not skip a preparation stage based on T-shirt size.
   Activation deliberately commences the selected spec and invokes this stage regardless of manual or decision-gated progression policy.

## Boundaries

- `spec` creates planning artifacts only; it never activates or progresses a normal change.
- Do not implement, commit, or make external writes.
- Preserve all unrelated specs and status records.

## Next

- The next planning or build stage is invoked by activation.
