# Requirements: Add local branch model

## Problem

Specle currently distinguishes local-only delivery, direct shared-upstream delivery, and branch-and-pull-request delivery. The local-only model does not describe a developer who wants to use a local feature branch as a temporary work area: they may make incremental commits, switch back to local `main` for unrelated work, return to the delivery branch for review and correction loops, and finally merge it locally.

A pull request is not required for that workflow. Treating it as branch-and-PR delivery would invent remote review, PR identity, and an external merge wait that do not exist. Conversely, direct-to-main delivery gives up the branch isolation that makes concurrent local work practical.

## Desired outcome

Add two explicit delivery models:

- **Local branch:** implementation and correction commits remain on a recorded local branch; `complete` archive-finalises that branch and merges it into local `main`.
- **Local branch with upstream:** the same local merge is followed by an explicit push of merged `main`; successful push is the configured shared-delivery event and can be resumed safely after a failure.

Both models retain normal review and correction cycles on the delivery branch, need no pull request, and make local branch use a first-class configured workflow rather than an accidental variation of direct delivery.

## User stories and acceptance criteria

### 1. Deliver from a local branch without a pull request

As a developer who uses branches for temporary local work, I want to deliver a reviewed change from my local branch, so I can switch between independent work without committing directly to `main`.

1. A project SHALL be able to select a local-branch delivery model that records the configured local delivery branch and its implementation commit without creating, querying, or requiring a remote branch or pull request.
2. `commit` SHALL keep the approved change on the recorded local delivery branch and move it to `committed` with durable local branch and commit evidence.
3. A committed local-branch change SHALL continue through the existing triage, resolve, corrective-work, verification, review, and commit loop on that same local branch until finalisation.
4. The workflow SHALL not infer the delivery branch from checkout order, branch naming, or a reverse scan of change records.

### 2. Finalise the local branch safely

As a developer ready to finish local branch work, I want `complete` to archive finalisation before merging, so the merge contains both implementation and the durable lifecycle record.

1. `complete` SHALL require explicit delivery authority, verify that the checkout is on the recorded local delivery branch, archive the delivery set and matching dependency updates on that branch, and merge it into configured local `main`.
2. If local `main` has advanced, the workflow SHALL use normal Git merge behaviour and stop safely on a conflict; it SHALL not reset, force, or silently discard work.
3. Before a branch switch or merge that could disturb tracked staged or unstaged work, the workflow SHALL preserve that work recoverably and restore it to its originating branch after successful synchronisation.
4. After the local merge succeeds, the workflow SHALL clear only the matching selector. It SHALL not delete the delivery branch unless a project explicitly establishes that policy.
5. Local-branch completion evidence SHALL use the recorded implementation commit and branch identity. It SHALL not invent PR reference, PR event, or PR completion fields.

### 3. Support an explicit post-merge upstream push

As a developer who works locally but shares `main`, I want a local-branch-with-upstream model, so I can push the completed local merge only after it is finalised.

1. A project SHALL be able to select a local-branch-with-upstream model whose final shared-delivery event is a successful push of the merged local `main`.
2. `complete` SHALL push only after the authorised local merge and SHALL report a rejected or failed push without rewriting the archive, re-merging, or clearing the selector.
3. A later explicit `complete <change-name>` invocation SHALL identify the recorded pending push, re-check the configured upstream state, and resume only the missing push or report the exact conflict or rejection.
4. The model SHALL preserve the full local-branch behaviour when no upstream is configured.

## Boundaries

- This adds local delivery models; it does not replace local-only, direct shared-upstream, or branch-and-PR delivery.
- It does not create a pull request, poll remote state, or add a notification service.
- It does not make branch deletion automatic.
- The post-merge upstream push is a distinct delivery model, not an implicit side effect of local-branch completion.
- The existing direct-delivery evidence model remains the basis for non-PR completion; this change must not introduce a self-referential final-commit hash into archived state.

## Assumption

The upstream-push variant is modelled separately from local branch delivery because a failed push after a successful local merge has distinct recovery semantics.
