---
name: complete
specle_group: Integration
requires:
  - commit
  - triage
  - resolve
description: >-
  Confirm final delivery of a committed Specle change.
usage: >-
  Use for a committed branch-and-pull-request delivery after external review is settled, to confirm or perform the policy-authorised final delivery event.
lifecycle:
  accepts:
    - committed
  transitions:
    - from: committed
      to: complete
  terminal:
    - complete
---

# Complete committed delivery

Confirm that a committed branch-and-pull-request delivery reached the final event configured by the project. It may merge and synchronise only when both project policy and the user explicitly authorise that work.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/context.json`, `.specle/current-issue.json`, `.agents/steering/{lifecycle,delivery}.md`, `.agents/project/delivery.md`, and the `delivery` evidence in the selected target's existing context record.
2. Select the active committed target by default. A non-active committed target must be explicitly named and never replaces the active current issue. Require a branch-and-pull-request model, a delivery reference, a delivery head branch, and a delivery target branch. Stop if any is absent.
3. Check that the checkout is on the recorded delivery head branch. If it is on any other branch, including the delivery target branch, stop immediately and report the current and expected branches. Do not stash, switch, merge, pull, fetch, or otherwise modify the worktree.
4. Confirm that external findings are resolved and establish whether the final delivery event is already evidenced. If it is, record that evidence and continue only with policy-authorised local synchronisation.
5. If the delivery is not already final, describe the precise merge action and require both project policy and explicit user authorisation before performing it. Without both, leave the target committed and provide the required human action.
6. Before an authorised merge-and-sync operation, detect tracked and untracked work. Preserve it with a named, recoverable stash that includes untracked files. If creating the stash fails, stop before merging, switching, or synchronising.
7. Merge the reviewable delivery when authorised, switch to the configured delivery target branch, and fast-forward from upstream without reset or force operations. Restore the stash afterwards. If restoration conflicts or fails, retain the stash, record a recovery note, and report concrete recovery steps without deleting work.
8. Record final delivery evidence in the selected target's existing context record and set the selected target to `complete`. A non-active target remains non-active throughout.
   Move every completed included queued abbreviated sidecar from `queued_specs` to `recent_specs`, retaining its relationship and delivery evidence.

## Boundaries

- Never act when the branch guard fails.
- Never discard staged, unstaged, untracked, or ignored work; retain the stash if restoration is incomplete.
- Lack of merge authority does not prevent recording an already evidenced external merge.
- Do not create or consume a separate delivery record, or depend on queued future schema work.

## Next

- No lifecycle step remains after completion.
- `triage <spec-name>` — when new external feedback arrives before the final event.
