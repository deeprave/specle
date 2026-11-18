---
name: commit
specle_group: Integration
requires: [review]
description: >-
  Deliver approved Specle work according to project policy.
usage: >-
  Use after local review approves a change, bugfix, or refactor to prepare or perform its configured commit, push, and pull-request delivery actions.
---

# Commit approved work

Prepare or perform delivery only for an approved target, using the selected project delivery policy. This skill distinguishes local approval from final external delivery.

## Workflow

1. Read `.specle/context.json`, `.specle/current-issue.json`, `.agents/steering/{lifecycle,delivery,testing}.md`, and `.agents/project/{delivery,security,testing}.md`.
2. Select the active approved target by default. A non-active target must be explicitly named, have `status: "approved"`, and must not replace the active current issue. Stop if delivery policy is missing or incomplete; direct the user to `onboard`.
3. Read the target's tasks, review evidence, and, where present, its `delivery` field in the selected target's existing context record. Do not infer a delivery reference from a branch or pull request.
4. Inspect only the target's scoped changes and any related approved sidecars that explicitly declare the selected target's path with `delivery: "with-related-spec"`. Do not stage, commit, stash, or otherwise include unrelated work. Run project-required pre-delivery checks, including any configured secret check.
5. Explain the exact planned action and obtain explicit user authorisation before any external write. If authority or policy is absent, provide exact instructions and leave the target approved.
6. Apply the selected model:
   - **Local-only Git:** create the authorised local commit and record its evidence. When the policy defines that commit as final delivery, mark the target `complete`.
   - **Direct shared upstream:** create the authorised delivery-branch commit and push it. Record the shared-upstream evidence; mark the target `complete` only after the configured final event succeeds.
   - **Branch and pull request:** create or update the approved branch delivery, push it, and create or update the reviewable change request. Record its delivery reference, head branch, target branch, and current delivery event in the selected target's existing context record and every included related approved sidecar, then move every delivered member to `committed` with next `complete`.
7. Preserve the active current issue whenever the selected target is non-active. Report the delivery members, evidence recorded, and next delivery action.

When a local-only or direct-delivery operation completes an included queued abbreviated sidecar, move that sidecar from `queued_specs` to `recent_specs` while retaining its relationship and delivery evidence.

## Boundaries

- Never make an external write without explicit user authorisation and applicable project policy.
- Never stage unrelated files or infer a branch, destination, pull-request format, or secret-scanning policy.
- Do not merge a pull request; `complete` owns final branch-and-pull-request delivery.
- Do not create a separate delivery record or depend on queued future schema work.

## Next

- `complete` — for a committed branch-and-pull-request delivery.
- `triage <spec-name>` — when external review feedback arrives for a committed target.
