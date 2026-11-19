---
name: design
specle_group: Planning
description: >-
  Design a normal spec's technical implementation.
usage: >-
  Use after normal requirements exist, especially for M/L/XL or uncertain work, and before task planning.
lifecycle:
  accepts:
    - estimated
  transitions:
    - from: estimated
      to: designed
      next: tasks
---

# Create a technical design

Turn a normal spec's requirements into an actionable technical design, matching the `design.md`
files already in `.specle/specs/`.

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the affected design and spec artefacts. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/context.json` and `.specle/current-issue.json` to locate the active spec. A named queued normal spec is also valid for explicit planning; it must remain queued and unactivated.
2. Read `requirements.md` and `spec.md` from that folder.
3. Read `.agents/steering/*.md` and the authoritative `.agents/project/` documents relevant to the change so the design
   follows the repository's architecture, API, security, and testing conventions.
4. Write `design.md` in the spec folder with:
   - **Overview** — what changes, at a glance.
   - **Architecture** — component/call flow (a text diagram is fine).
   - **API / data** — applicable endpoints, result keys, and record shapes.
   - **Error handling** — map each failure to its documented policy.
   - **Report/output rendering** — if the feature has output, show relevant output shapes.
   - **Test strategy** — the behavioural tests and project quality gates to run.
5. For an active target, update `.specle/context.json` according to `context.md` and `lifecycle.md`: record that design is present and set its status to `designed`. For a named queued target, write only its design artifact and retain `status: "defined"` with next `activate`.

Keep the design faithful to every requirement — `verify` later checks design coverage.

## Next

After recording a successful design for the active target, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `tasks <spec-name>` unless a material design decision remains; otherwise report it and wait. For a named queued target, stop and report `activate <spec-name>`.

- `tasks` — generate the implementation tasks from this design.
- `verify` — confirm the design covers all requirements before building.
