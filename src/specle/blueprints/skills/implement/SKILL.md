---
name: implement
specle_group: Implementation
requires: [estimate, design, tasks, build, bugfix, refactor, context]
description: >-
  Advance existing specs through planning and implementation.
usage: >-
  Use to advance a normal spec through missing stages or an explicitly named abbreviated sidecar; do not repeat completed work.
---

# Implement a spec

Take an existing specification through the missing lifecycle stages up to and including `build`.
Reuse valid estimates, designs, and task plans; do not recreate them merely because this skill was
invoked.

## Workflow

1. Select and classify the target spec. Use the active spec by default. For an explicitly named target, resolve it against `current_spec` and `queued_specs`, then read its `kind` (defaulting a missing kind to `change`). A normal named target may become current when necessary; a queued `bugfix` or `refactor` must be explicitly named, remain non-active, and never replace another current issue. Never choose an abbreviated queued item implicitly.
2. Read `.specle/current-issue.json`, `.specle/context.json`, the lifecycle, and applicable authoritative `.agents/project/` documents. For a normal spec, read `requirements.md`, `spec.md`, and any `estimate.md`, `design.md`, and `tasks.md`. For an abbreviated target, read its `spec.md` and `tasks.md`. Confirm the artefact set and recorded status agree; use `context` if they do not.
3. Advance only the missing stages, following the selected skill's full instructions:
   - For a normal spec, use `estimate` when no valid estimate exists. Treat its sizing recommendation as advisory: design is normally needed for M/L/XL work; small, understood work may proceed to tasks.
   - For a normal spec, use `design` when needed and `design.md` is absent or invalidated.
   - For a normal spec, use `tasks` when `tasks.md` is absent, incomplete as a plan, or invalidated by the requirements or design.
   - For a normal spec with an unchecked, buildable task list, use `build` until every planned task is complete.
   - For a named queued `bugfix` or `refactor`, invoke the matching owning workflow to resume its existing abbreviated tasks. Do not run `estimate`, `design`, `tasks`, or `build` for abbreviated work.
4. Stop rather than inventing a decision when requirements are ambiguous, a material design choice
   needs user direction, or untriaged review feedback affects the target. Route completed review
   decisions through `resolve`; it may in turn use `revise`, `bugfix`, or `refactor` before
   this skill resumes the build path.
5. Do not repeat completed stages. If all normal or abbreviated tasks are already complete, do not rebuild; report `verify` as the next step. If the spec is already `verified`, report `review`; if it is
   `complete`, report that no implementation work remains.

## Boundaries

- This skill operates on an existing spec; use `spec` to create a new normal spec, or `bugfix`/`refactor` to create abbreviated side work.
- Preserve the target spec's directory and history. Corrections to a normal spec's requirements, design, or plan stay in that spec through `revise`, rather than becoming a separate review-fix change. Never activate a queued abbreviated target.
- Delegate stage-specific state updates to the selected skills. Do not silently skip their
  required tests, lifecycle updates, or decision points.
- Stop after `build`; verification, review, delivery, and pull-request operations remain their own
  explicit stages.

## Next

- `verify` — when all normal or abbreviated implementation tasks are complete.
- `review` — when verification has already passed.
