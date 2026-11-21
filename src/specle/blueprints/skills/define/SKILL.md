---
name: define
specle_group: Planning
description: >-
  Create unselected normal feature changes under `.specle/changes/`.
usage: >-
  Use to plan a normal unit of work and capture functional and non-functional requirements without commencing it.
lifecycle:
  creates:
    - defined
---

# Write a feature change

Create a structured change for a new piece of work, matching the conventions of the existing changes in `.specle/changes/`.

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the affected change artefacts and context. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

## Workflow

Before creating or recording lifecycle state, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.agents/policies/*.md`, especially `lifecycle.md`, then `.agents/steering/*.md` and the authoritative `.agents/project/*.md` documents relevant to the requested change.
2. Ask (or infer) the intent of the feature. If it is underspecified, ask 2–4 targeted clarifying questions before writing — propose sensible defaults so the user can confirm quickly.
3. Create the change folder: `.specle/changes/<change-slug>/`, using a concise 2–4 word slug that is unique across `.specle/changes/` and `.specle/archive/`.
4. Write `requirements.md` with:
   - **Introduction** — problem/context.
   - **Glossary** — key terms.
   - **Requirements** — numbered, each with a user story and EARS-style **Acceptance Criteria**
     (`THE … SHALL …`, `IF … THEN … SHALL …`). These are the conformance checklist `verify` uses.
   - **Non-Functional Requirements** — dependencies, applicable project rules, and unchanged behaviour.
5. Write `spec.md` (concise, well under 500 words) — the condensed intent for context retention after compression: problem, goal, key result keys, output, design sketch, verification.
6. Add versioned `status.json` with `kind: "change"`, `status: "defined"`, `created_at` set to the current ISO 8601 timestamp with UTC offset, `activated_at: null`, empty progress, `not-run` verification/review, `delivery: null`, and empty `relationships` and `dependencies`. Do not select it in `.specle/current-change`, invoke planning, or commence implementation.

If the user identifies a completed spike as the source of this change, update that spike's `findings.json` `outcome_change` with this change's stable name.

Do not replace an unfinished local selection in `.specle/current-change`.

## Next

- `activate <change-name>` — explicitly commence the unselected normal change.
