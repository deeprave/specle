---
name: resolve
specle_group: Quality
requires: [triage, revise, prepare, bugfix, refactor, spec]
description: >-
  Dispatch accepted review decisions to follow-up workflows.
usage: >-
  Use only after triage has recorded decisions for all current findings; route accepted work without implementing it directly.
---

# Resolve triaged review findings

Dispatch recorded review decisions without revisiting the triage or silently implementing work outside the selected workflows.

## Workflow

1. Read `.specle/context.json`, `.specle/current-issue.json`, `.agents/steering/{lifecycle,review}.md`, `.agents/project/review.md`, and the target's `review-findings.json`.
2. Select the target. Default to the active normal spec. A non-active target must be explicitly named. A committed normal change, bugfix, or refactor never replaces the active current issue. Require `status: "triaged"` and a decision for every current finding. Otherwise, stop and direct the user to `triage`.
3. Reconcile existing accepted-action dispatches before dispatching new work. For each recorded resulting work item, determine whether it is complete, incomplete, or failed. Record completed outcomes and do not dispatch them again. Incomplete or failed follow-up work keeps the target `triaged`; report that work item's next step and `resolve <target>` as the reconciliation step after it completes.
4. Identify accepted findings without a completed dispatch. Group ordinary follow-up routes by their recorded route and process groups in P1–P6 order. Keep an independent `spec` route pending until every other current finding is terminally no-action or has a completed follow-up. Do not reopen declined, skipped, deferred, duplicate, or completed-dispatch findings.
5. Dispatch each pending accepted group according to its decision:
   - `revise` — revise the target normal spec or explicitly named abbreviated target in place.
   - `prepare-bugfix` or `prepare-refactor` — create a named prepared sidecar; this is the default for new bounded follow-up work.
   - `bugfix` or `refactor` with `execution: "execute"` — execute the selected abbreviated workflow only when the user decision or automatic policy explicitly authorises it.
   - `spec` — only after every other current finding is settled, create the independent normal spec as queued `defined` work. Do not complete the origin: restore it to `approved` when it has only local review history or `committed` when it has a submitted delivery, then direct it to its own delivery step. Until then, leave the route pending and report the remaining work. A named non-active target must preserve the unrelated active current issue.
6. Update each dispatched finding in `review-findings.json` with its dispatch state, selected workflow, execution mode, resulting spec path when applicable, and any failure or deferred reason. Preserve all source history and decisions.
7. Let each downstream workflow own its lifecycle transition. Do not mark the originating review target complete merely because accepted decisions were dispatched. A committed normal change with accepted implementation work returns through build, verification, review, approval, and commit. When every current finding is terminally no-action (`decline`, `skip`, `defer`, or `duplicate`) or has a completed dispatched follow-up, record `review.status: "resolved"` with `findings: 0`. Restore a previously committed target to `committed` and direct the user to `complete`; restore a locally reviewed target to `approved` and direct the user to `commit`. Only a target whose configured delivery outcome is already evidenced may become `complete`. Never change the active current issue for a named non-active target. Report the terminal dispositions and every resulting work item.

## Boundaries

- Do not re-triage, alter decisions, or downgrade severity.
- Do not implement code, tests, or task steps directly; only the selected downstream workflow may do so.
- Do not write to external review sources, pull-request threads, or tracker records.
- Do not dispatch a direct execution route without explicit recorded authorisation.

## Next

After explicit invocation and successful dispatch, read `.agents/project/automation.md`. In `decision-gated` mode, continue only through the selected downstream local workflow; never bypass a downstream preflight or delivery boundary.

- If a dispatched follow-up remains incomplete, follow its reported next step, then invoke `resolve <target>` to reconcile it.
- When Resolve completes the selected target, no lifecycle step remains.
