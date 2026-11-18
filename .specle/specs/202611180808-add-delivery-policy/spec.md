# Delivery policy and completion workflow

## Problem

Local review approval currently marks work complete, even when a project must still commit, push, open a pull request, receive external feedback, and merge it. This prevents Specle from accurately representing delivery and safely revisiting submitted work while a different issue is active.

## Goal

Add portable delivery steering, project delivery guidance, and a lifecycle that distinguishes local approval, submitted reviewable work, and completed delivery.

## Behaviour

- Steering defines local-only, direct-to-main, and branch-and-pull-request delivery models; projects select and refine one in `project/delivery.md` through onboarding.
- A passing local review makes a change, bugfix, or refactor `approved`, rather than complete.
- `commit` applies the project delivery policy, including scoped staging, required checks, authorised external writes, commit conventions, and pull-request conventions.
- Branch-and-pull-request delivery becomes `committed`; local-only and direct-to-main delivery can become `complete` after the configured delivery event.
- `complete` operates only from the selected committed pull request's head branch. With authorised project policy it preserves any tracked or untracked local work in a recoverable stash, merges the pull request, switches to the configured delivery target branch, fast-forwards from upstream, restores the stash, and then marks delivery complete. A branch mismatch or stash-restoration conflict stops safe local operations and reports recovery steps without discarding work.
- Explicitly named submitted work can re-enter triage and resolution without replacing the current active issue, then follows verification, review, approval, and delivery again.
- When all findings from a local review are terminally no-action, Resolve restores the target to `approved` so it can enter `commit`; only a configured delivery event can make it `complete`.
- An explicitly named committed normal change can resume its scoped build and quality stages without replacing the unrelated active issue.
- An independent-spec hand-off creates separate queued normal work without completing its origin; the origin returns to `approved` or `committed` and follows its own delivery path.

## Constraints

Keep policy human-readable and project-owned. Keep operational delivery state with the spec under a documented versioned JSON contract. Do not prescribe a Git host, issue tracker, client, branch convention, or authority for external writes.

## Verification

Verify onboarding creates delivery guidance one question at a time, lifecycle transitions differ correctly by delivery model, commit blocks unapproved or unrelated work, externally submitted work re-enters through named triage without changing the current issue, and completion requires the configured final event.
