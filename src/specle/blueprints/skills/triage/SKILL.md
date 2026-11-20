---
name: triage
specle_group: Quality
description: >-
  Consolidate review findings into prioritised decisions.
usage: >-
  Use after local review or with supplied external feedback to deduplicate findings and record decisions without implementing fixes.
lifecycle:
  accepts:
    - review-findings
  transitions:
    - from: review-findings
      to: triaged
      next: resolve
---

# Triage review findings

Consolidate review feedback for one work item, decide what should happen to each finding, and leave implementation to `resolve` or the selected downstream workflow.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-spec` when present, the target `status.json`, `.agents/policies/{review,lifecycle}.md`, applicable `.agents/steering/` overrides, and `.agents/project/review.md`.
2. Select the target. Default to the locally selected normal spec. A non-selected target must be explicitly named. A `committed` normal change may be selected for external feedback without replacing `.specle/current-spec`; bugfixes and refactors also remain explicit. A spike does not enter triage.
3. Read `.specle/specs/<target>/review-findings.json` when it exists. Collect the internal review result and any explicitly named external review sources. If an external source cannot be connected to a target spec, ask the user rather than guessing.
4. Record each source with a stable `id`, `system`, `kind`, canonical `url` when available, and `revision` or content fingerprint. Do not create a new finding for an unchanged source item already recorded.
5. Consolidate source items into findings. Merge only clear duplicates, retain every source ID, and mark uncertain matches as possible duplicates for user judgement. Each finding records its P1–P6 severity, description, evidence, analysis, recommendation, state, decision, and route.
6. Present findings using project review guidance and the policy layouts:
   - **One at a time:** use the policy item/source/analysis/recommendation format and ask the user to accept, decline, skip, defer, or discuss each finding.
   - **Batch:** present all findings in severity order and record the user's decisions.
   - **Automatic:** record automatic decisions only where project policy permits; present any decision or open question using the one-at-a-time format.
7. Record decisions in `review-findings.json`. Accepted findings must have a proposed route; declined, skipped, deferred, and duplicate findings retain their rationale and source history. Do not implement anything.
8. When every current finding has a decision, set the target to `triaged`. For a non-selected target, update only its matching status with `status: "triaged"`; preserve `.specle/current-spec`. For a selected normal target, set its status to `triaged`.
9. Present a complete decision-and-route summary: every current finding's severity, decision, recorded rationale, and proposed route. Stop and wait for explicit `resolve` or a user-requested decision revision, including in decision-gated progression mode.

## Boundaries

- Do not implement code, tests, task steps, or external changes.
- Do not discard an external source item solely because it resembles an older finding; preserve it as a possible duplicate until the decision is clear.
- Do not create new bugfixes, refactors, or specs; `resolve` performs the approved routing later.

## Next

- `resolve` — route the triaged accepted findings to their selected workflows.
