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

1. Read `.specle/current-change` when present, `.agents/policies/{lifecycle,delivery}.md`, applicable `.agents/steering/` overrides, `.agents/project/delivery.md`, and the selected target's `status.json` delivery evidence.
2. Select the locally selected delivery-complete target by default. A non-selected target must be explicitly named and never replaces `.specle/current-change`. Require the evidence appropriate to the configured delivery model. For branch-and-pull-request delivery, require a reference, head branch, and target branch.
3. For branch-and-pull-request delivery, check that the checkout is on the recorded delivery head branch. If it is on any other branch, including the delivery target branch, stop immediately and report the current and expected branches. Do not stash, switch, merge, pull, fetch, or otherwise modify the worktree.
4. Confirm that external findings are resolved and establish whether the final delivery event is already evidenced. A confirmed final event makes the target effectively complete for later activation, even before archival finalisation is delivered.
5. If the delivery is not already final, describe the precise final action and require both project policy and explicit user authorisation before performing it. Without both, leave the target ready for delivery and provide the required human action.
6. Before an authorised merge-and-sync operation, detect tracked and untracked work. Preserve it with a named, recoverable stash that includes untracked files. If creating the stash fails, stop before merging, switching, or synchronising.
7. Perform the authorised final delivery action. For branch-and-pull-request delivery, merge the reviewable delivery, switch to the configured delivery target branch, and fast-forward from upstream without reset or force operations. Restore the stash afterwards. If restoration conflicts or fails, retain the stash, record a recovery note, and report concrete recovery steps without deleting work.
8. Generate `summary.md`, stage a complete directory move from `.specle/changes/<name>` to `.specle/archive/<name>`, update the archived `status.json` with final delivery evidence and `status: "complete"`, and stage local selector removal when it selected the target. Preserve every artifact, relationship, and delivery field. Treat this as one recoverable operation: on failure, retain or restore the active directory and selector.
9. Present the exact finalisation file list and obtain delivery authorisation before committing any archive mutation. For direct-main policy, commit finalisation on main. For a delivery branch already merged into main, create `<delivery-branch>-completion` from the retained delivery head, commit and push only the archival finalisation, and open a completion PR to main; then synchronise local main so unrelated work may proceed.
10. A named non-selected target remains non-selected throughout.

## Boundaries

- Never act when the branch guard fails.
- Never discard staged, unstaged, untracked, or ignored work; retain the stash if restoration is incomplete.
- For a branch-and-pull-request delivery that has not reached its final event, do not direct the user to merge manually; `complete` owns the authorised merge and archival finalisation sequence.
- Lack of merge authority does not prevent preparing archive finalisation for an already evidenced external merge.
- Do not create or consume a separate delivery record, or depend on queued future schema work.

## Next

- No lifecycle step remains after completion.
- `triage <change-name>` — when new external feedback arrives before the final event.
