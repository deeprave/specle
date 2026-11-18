---
name: estimate
specle_group: Planning
requires: []
description: >-
  Estimate Specle work complexity and planning depth.
usage: >-
  Use before implementation to size an active spec and decide whether design is warranted; it is advisory and performs no implementation.
---

# Estimate complexity

Provide an advisory complexity assessment for the current (or described) work. This does not block
anything.

## Workflow

1. Read `.specle/context.json` for current state.
2. Read `requirements.md` (or `spec.md`) thoroughly.
3. Read the relevant authoritative `.agents/project/` documents and the codebase to understand the
   current state, project constraints, and blast radius.
4. Skim relevant past-work memory (`.specle/specs/*/memory.json`, prior specs) for similar efforts.
5. Read `.agents/steering/lifecycle.md` before recording state.

## Output

Write `estimate.md` in the spec folder with:

- **T-shirt size**: S / M / L / XL
- **Breakdown**: new files (~N), modified files (~N), estimated tasks (~N), key risks.
- **Confidence**: High / Medium / Low
- **Recommendation**:
  - S: skip design, go straight to `tasks`.
  - M: consider `design`.
  - L/XL: `design` recommended; consider splitting into smaller specs.
- **Similar past work**: reference relevant memory/specs.

If estimating the active spec, update its lifecycle status to `estimated`. A named queued-spec
estimate records only that spec's artifact; it does not change `.specle/current-issue.json`.

## Next

- `design` — for M+ work.
- `tasks` — for small work, go straight to tasks.
