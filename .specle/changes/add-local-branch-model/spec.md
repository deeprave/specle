# Add local branch model

## Problem

Developers often use local feature branches as isolated temporary work areas even when they do not want a remote branch or pull request. Specle has no delivery model for that workflow: direct delivery commits to `main`, while branch delivery assumes a remote review request.

## Goal

Define local-branch delivery, where work is committed and reviewed on a recorded local branch and `complete` archive-finalises then merges it into local `main`. Define local-branch-with-upstream separately, where that merge is followed by a resumable push of `main`.

## Direction

Extend delivery policy, lifecycle guidance, commit and complete instructions, runtime validation, schema only where a constrained record contract needs it, documentation, and tests. Preserve explicit branch identity, normal Git merge/conflict behaviour, recoverable handling of unrelated tracked work, and narrow selector cleanup. Do not infer branches, create PRs, or delete branches.

## Verification

Cover model selection, recorded branch evidence, branch-only correction loops, archive-before-local-merge ordering, changed-local-main conflict handling, selector cleanup, and the upstream-push failure/resumption path. Run the project quality gates and installed/blueprint validation.
