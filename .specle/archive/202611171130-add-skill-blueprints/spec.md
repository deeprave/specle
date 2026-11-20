# Add skill blueprints

## Problem

Specle has reusable skill blueprints and a separate active inventory, but activating a skill without understanding its dependencies can leave agents unable to complete its workflow.

## Goal

Establish a deliberate workflow for reviewing a blueprint, resolving its required skill dependencies, and copying it into `.agents/skills/`.

## Behaviour

- `src/specle/skills/<skill>/SKILL.md` is the canonical blueprint.
- Review direct dependencies before installation; distinguish them from optional next steps.
- Install only ready blueprints by copying them unchanged to `.agents/skills/<skill>/SKILL.md`.
- Mark and group Specle blueprints with `specle_group`; the `specle` guide dynamically inventories only marked installed skills.
- Keep concise selection descriptions separate from detailed usage guidance in every skill's frontmatter.
- Classify work independently of lifecycle status with an extensible `kind`, initially covering changes, bugfixes, documentation, and releases.
- Reconcile accepted review actions through repeated Resolve runs, complete the selected normal or abbreviated item only when no action remains, and defer an independent-spec terminal hand-off until every other accepted action is settled.
- Publish a root lifecycle reference for the currently implemented normal, abbreviated, and spike flows, auditing every state for a valid transition or terminal outcome without presenting planned delivery-policy work as current behaviour.
- Make the later Resolve reconciliation invocation explicit whenever recorded follow-up work is incomplete.
- Keep project-specific facts in `.agents/project/`, not in reusable blueprints.

## Verification

For each installed skill, confirm its source and active copies match and that every required dependency is present in the active inventory.
