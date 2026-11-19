---
name: activate
specle_group: Planning
requires:
  - estimate
  - design
  - tasks
  - build
description: >-
  Explicitly commence a queued normal specification.
usage: >-
  Use with a named queued normal spec to make it current and begin its planning lifecycle.
lifecycle:
  accepts:
    - defined
  transitions:
    - from:
        status: defined
        kind: change
        scope: queued
      to:
        status: defined
        kind: change
        scope: active
      next: estimate
---

# Activate a normal spec

Make an explicitly named queued normal spec the current work item. Activation is the boundary between planning a spec and commencing it.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/context.json`, `.specle/current-issue.json` when present, and `.agents/steering/lifecycle.md`.
2. Require an explicit spec name. Locate its queued record and require `kind: "change"` and `status: "defined"`. Do not activate a bugfix, refactor, spike, completed spec, or an unrecorded directory.
3. If another unfinished current spec exists, stop and ask the user to resolve or explicitly replace that active selection; never displace it implicitly.
4. Move the named queued record to `current_spec`, write its path to `.specle/current-issue.json`, and retain `status: "defined"`, verification `not-run`, and review `not-run`.
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
- Preserve all unrelated queued records.

## Next

- The next planning or build stage is invoked by activation.
