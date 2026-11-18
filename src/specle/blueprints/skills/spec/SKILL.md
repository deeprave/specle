---
name: spec
specle_group: Planning
requires: []
description: >-
  Create normal feature specifications under `.specle/specs/`.
usage: >-
  Use to start a normal unit of work and capture functional and non-functional requirements; do not replace unfinished active work without user intent.
---

# Write a feature spec

Create a structured specification for a new piece of work, matching the conventions of the existing specs in `.specle/specs/`.

## Workflow

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
6. When ready to commence, set the active spec: write `.specle/current-issue.json` as a JSON record with its `spec_path` set to `.specle/specs/YYYYMMDDHHMM-<slug>`, then initialise `.specle/context.json` according to `context.md` and `lifecycle.md` (status `defined`; verification and review `not-run`). When Resolve dispatches an independent-spec hand-off while its origin must remain active for delivery, create the new normal spec as a queued record with `kind: "change"`, `status: "defined"`, and next `estimate`; do not replace `.specle/current-issue.json`.

If the user identifies a completed spike as the source of this spec, update that spike's `findings.json` `outcome_spec` with this spec's `.specle/specs/...` path.

Do not replace an unfinished active spec in `current-issue.json` unless the user intends it.

## Next

- `design` — add a technical design (recommended for L/XL work).
- `tasks` — generate the implementation task list.
- `verify` — sanity-check the spec's acceptance criteria before building.
