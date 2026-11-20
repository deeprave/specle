---
name: estimate
specle_group: Planning
description: >-
  Estimate Specle work complexity and planning depth.
usage: >-
  Use before implementation to size an active spec and decide whether design is warranted; it is advisory and performs no implementation.
lifecycle:
  accepts:
    - defined
  transitions:
    - from: defined
      to: estimated
      next: design
---

# Estimate complexity

Provide an advisory complexity assessment for the current (or described) work. This does not block
anything.

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the estimate and affected spec artefacts. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-spec` when present and the target's `status.json`. Default to the selected normal spec. A named unselected normal spec is valid for advisory estimation only; it must remain unselected.
2. Read `requirements.md` (or `spec.md`) thoroughly.
3. Read the relevant authoritative `.agents/project/` documents and the codebase to understand the
   current state, project constraints, and blast radius.
4. Skim relevant archived specs under `.specle/archive/` for similar efforts.
5. Read `.agents/policies/lifecycle.md` and any applicable `.agents/steering/` override before recording state.

## Output

Write `estimate.md` in the spec folder with:

- **T-shirt size**: S / M / L / XL
- **Breakdown**: new files (~N), modified files (~N), estimated tasks (~N), key risks.
- **Confidence**: High / Medium / Low
- **Recommendation**: describe the planning risks and any reason to split the work. Active normal work always continues through design before tasks.
- **Similar past work**: reference relevant memory/specs.

If estimating the selected spec, update its lifecycle status to `estimated`. A named unselected
estimate records only that spec's artifact; it does not change `.specle/current-spec`.

## Next

After recording a successful estimate for the selected spec, read `.agents/project/automation.md`. In `decision-gated` mode, invoke `design <spec-name>`; otherwise report it and wait. For a named unselected spec, stop and report `activate <spec-name>` regardless of progression policy.

- `design` — required before tasks for active normal work.
