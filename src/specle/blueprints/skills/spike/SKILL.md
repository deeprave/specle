---
name: spike
specle_group: Discovery
requires: []
description: >-
  Investigate a question within a time-box, without implementation.
usage: >-
  Use before committing to a solution when a bounded investigation is needed; produce findings and recommendations, not production changes.
---

# Spike an investigation (don't implement)

Research a question for decision-making as active work. **Do not implement anything.**

## Workflow

1. Read `.specle/current-issue.json`, `.specle/context.json`, and the relevant steering and project guidance. Do not replace an unfinished active work item unless the user intends to do so; retain it in `queued_specs` when switching the current issue.
2. Establish the investigation question, hypothesis, scope, and an S/M/L/XL effort budget. The budget bounds research effort; it is not a delivery estimate or due date.
3. Create `.specle/specs/YYYYMMDDHHMM-{slug}/findings.json` with `question`, `hypothesis`, `effort`, `scope`, `status: "defined"`, `findings`, `recommendations`, `risks`, and `outcome_spec: null`.
4. Set `.specle/current-issue.json` to the new path and initialise the matching `current_spec` with `kind: "spike"`, `status: "defined"`, and verification and review both `not-applicable`.
5. Set the active spike status to `spiking`, then research the question using code, documentation, and read-only experiments only. Update `findings.json` with concrete evidence, recommendations, and risks.
6. On completion, set `findings.json.status` to `complete`. If a resulting normal spec, bugfix, or refactor exists, set `outcome_spec` to its `.specle/specs/...` path; otherwise leave it `null`. Update the active context to `complete` without changing verification or review to an implementation state.

Research only — no production code, tests, task plans, or implementation changes.

## Next

- `spec` — create an outcome feature spec when the findings recommend one, then record its path in `outcome_spec`.
- Move on — when the spike recommends no follow-up work.
