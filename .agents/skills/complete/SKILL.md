---
name: complete
specle_group: Integration
requires:
  - commit
  - triage
  - resolve
description: >-
  Finalise or resume archival delivery for a committed Specle change.
usage: >-
  Use after a committed delivery to archive it on its existing delivery path, request final merge where applicable, or resume synchronisation after that merge.
lifecycle:
  accepts:
    - committed
    - complete
  transitions:
    - from: committed
      to: complete
  terminal:
    - complete
---

# Complete delivery

Complete archival finalisation on the delivery already recorded by `commit`. A branch-and-pull-request delivery stays on its original PR: completion archives the record on that branch, pushes the archival commit to that PR, and requests auto-merge when permitted. A later explicit invocation synchronises after that same PR merges.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-change` when present, `.agents/policies/{lifecycle,delivery}.md`, applicable `.agents/steering/` overrides, `.agents/project/delivery.md`, and the selected target's `status.json` delivery evidence.
2. Select a locally selected or explicitly named target. An active target must be `committed`; an archived target must be `complete` and have `delivery.completion`. A named non-selected target never replaces `.specle/current-change`. For an active normal parent, derive sidecars only from its own reciprocal concurrent-delivery declarations and require them to be `committed` with consistent delivery evidence.
3. For an active branch-delivery target, require the recorded original PR reference, head branch, and target branch, and require the checkout to be on that recorded head branch. Confirm all current external findings are terminally resolved before mutating the archive.
4. For an active delivery, form the delivered-name set, then re-read every other active `status.json` and remove only matching explicit dependencies. Generate the parent summary, add `delivery.completion` with the original PR reference and branches, set `status: "complete"` and `archived_at`, and move the parent and validated sidecars to `.specle/archive/` as one recoverable mutation. Preserve `updated_at` and all unrelated fields.
5. Present the exact finalisation file list and require project policy plus explicit delivery authority before committing it. For direct delivery, commit finalisation on the delivery branch and clear the matching selector. For branch delivery, commit and push finalisation to the existing recorded head branch, then add each archived record's `delivery.completion.commit` in a follow-up commit on that same branch. Never create another branch or PR.
6. After the archival update is pushed, request auto-merge for the original PR when the repository permits it. If CI, review, merge eligibility, or auto-merge enablement is outstanding, report that exact condition and retain the selector. Do not poll or subscribe for external updates.
7. For an archived complete target, inspect its recorded original PR. If it is not merged, report its exact external condition. If it is merged, preserve tracked staged and unstaged work in one recoverable stash, switch to the recorded target branch, fast-forward from upstream without reset or force operations, restore the stash, and remove the matching selector. Do not alter the archive.
8. A named non-selected target remains non-selected throughout.

## Boundaries

- Never act when the active-delivery branch guard fails.
- Never discard staged or unstaged work; retain the stash if restoration is incomplete. Do not shuffle untracked or ignored generated files merely to guard against a rare branch-switch collision.
- Do not merge the original PR before its archival finalisation is pushed; request auto-merge instead.
- Do not add a delivery-tracking store, notification service, second PR, or mutable completion event.
- A jointly archived sidecar has no separate completion cycle; its parent owns the shared finalisation delivery.

## Next

- `complete <change-name>` — recheck the same PR after an external merge or report its outstanding condition.
- `triage <change-name>` — when new external feedback arrives before archival finalisation.
