---
name: spec
specle_group: Planning
description: >-
  Create normal feature specifications under `.specle/specs/`.
usage: >-
  Use to plan a normal unit of work and capture functional and non-functional requirements without commencing it.
lifecycle:
  creates:
    - defined
---

# Write a feature spec

Create a structured specification for a new piece of work, matching the conventions of the existing specs in `.specle/specs/`.

## Change independence

Changes are independent by default. A queued or future change must not create a dependency through ordering, conceptual overlap, or anticipated functionality. Record a dependency only for an obvious, already-implemented technical prerequisite or an explicit user decision, and make it visible in the affected spec artefacts and context. Constraints, features, expectations, and functionality from a future change must not constrain this change until that future change is implemented.

## Workflow

Before creating or recording lifecycle state, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.agents/steering/*.md`, especially `context.md` and `lifecycle.md`, then read the authoritative `.agents/project/*.md` documents relevant to the requested change.
2. Ask (or infer) the intent of the feature. If it is underspecified, ask 2–4 targeted clarifying questions before writing — propose sensible defaults so the user can confirm quickly.
3. Create the spec folder: `.specle/specs/YYYYMMDDHHMM-{feature-slug}/` (today's date/time, a 2–4 word slug).
4. Write `requirements.md` with:
   - **Introduction** — problem/context.
   - **Glossary** — key terms.
   - **Requirements** — numbered, each with a user story and EARS-style **Acceptance Criteria**
     (`THE … SHALL …`, `IF … THEN … SHALL …`). These are the conformance checklist `verify` uses.
   - **Non-Functional Requirements** — dependencies, applicable project rules, and unchanged behaviour.
5. Write `spec.md` (concise, well under 500 words) — the condensed intent for context retention after compression: problem, goal, key result keys, output, design sketch, verification.
6. Add a queued `.specle/context.json` record with `kind: "change"`, `status: "defined"`, and next `activate`. Do not write `.specle/current-issue.json`, select a current issue, invoke planning, or commence implementation.

If the user identifies a completed spike as the source of this spec, update that spike's `findings.json` `outcome_spec` with this spec's `.specle/specs/...` path.

Do not replace an unfinished active spec in `current-issue.json`.

## Next

- `activate <spec-name>` — explicitly commence the queued normal spec.
