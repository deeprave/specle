---
name: estimate
specle_group: Planning
description: >-
  Estimate Specle work complexity and planning depth.
usage: >-
  Use before implementation to size an active spec and decide whether design is warranted; it is advisory and performs no implementation.
---

# Estimate complexity

Provide an advisory complexity assessment for the current (or described) work. This does not block
anything.

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the estimate and affected spec artefacts. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

## Workflow

1. Read `.specle/context.json` for current state. Default to the active normal spec. A named queued normal spec is valid for advisory estimation only; it must remain queued and unactivated.
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
- **Recommendation**: describe the planning risks and any reason to split the work. Active normal work always continues through design before tasks.
- **Similar past work**: reference relevant memory/specs.

If estimating the active spec, update its lifecycle status to `estimated`. A named queued-spec
estimate records only that spec's artifact; it does not change `.specle/current-issue.json`.

## Next

After recording a successful estimate for the active spec, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `design <spec-name>`; otherwise report it and wait. For a named queued spec, stop and report `activate <spec-name>` regardless of progression policy.

- `design` — required before tasks for active normal work.
