---
name: design
specle_group: Planning
requires: []
description: >-
  Design a normal spec's technical implementation.
usage: >-
  Use after normal requirements exist, especially for M/L/XL or uncertain work, and before task planning.
---

# Create a technical design

Turn the current spec's requirements into an actionable technical design, matching the `design.md`
files already in `.specle/specs/`.

## Workflow

1. Read `.specle/context.json` and `.specle/current-issue.json` to locate the active spec.
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
5. Update `.specle/context.json` according to `context.md` and `lifecycle.md`: record that design
   is present and set the active spec status to `designed`.

Keep the design faithful to every requirement — `verify` later checks design coverage.

## Next

- `tasks` — generate the implementation tasks from this design.
- `verify` — confirm the design covers all requirements before building.
