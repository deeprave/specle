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
2. Select the target. Default to the active normal spec. A queued bugfix or refactor must be explicitly named; never select a sidecar implicitly. Require `status: "triaged"` and a decision for every current finding. Otherwise, stop and direct the user to `triage`.
3. Reconcile existing accepted-action dispatches before dispatching new work. For each recorded resulting work item, determine whether it is complete, incomplete, or failed. Record completed outcomes and do not dispatch them again. Incomplete or failed follow-up work keeps the target `triaged`; report that work item's next step and `resolve <target>` as the reconciliation step after it completes.
4. Identify accepted findings without a completed dispatch. Group ordinary follow-up routes by their recorded route and process groups in P1–P6 order. Keep an independent `spec` route pending until every other current finding is terminally no-action or has a completed follow-up. Do not reopen declined, skipped, deferred, duplicate, or completed-dispatch findings.
5. Dispatch each pending accepted group according to its decision:
   - `revise` — revise the target normal spec or explicitly named abbreviated target in place.
   - `prepare-bugfix` or `prepare-refactor` — create a named prepared sidecar; this is the default for new bounded follow-up work.
   - `bugfix` or `refactor` with `execution: "execute"` — execute the selected abbreviated workflow only when the user decision or automatic policy explicitly authorises it.
   - `spec` — only after every other current finding is settled, record a terminal independent-work hand-off for an active normal target, complete that target, then create the new normal spec. Do not treat the new spec as a follow-up that the completed origin must await. Until then, leave the route pending and report the remaining work. A named abbreviated target must use a route that preserves the unrelated active current issue.
6. Update each dispatched finding in `review-findings.json` with its dispatch state, selected workflow, execution mode, resulting spec path when applicable, and any failure or deferred reason. Preserve all source history and decisions.
7. Let each downstream workflow own its lifecycle transition. Do not mark the originating review target complete merely because accepted decisions were dispatched. When every current finding is terminally no-action (`decline`, `skip`, `defer`, or `duplicate`), has a completed dispatched follow-up, or is an independent-work hand-off whose every other finding is settled, record `review.status: "resolved"` with `findings: 0` and complete the selected target. Set an active normal target to `complete`; for a named queued abbreviated target, move only that record to `recent_specs` as `complete` without changing the active current issue. Report the terminal dispositions and every resulting work item.

## Boundaries

- Do not re-triage, alter decisions, or downgrade severity.
- Do not implement code, tests, or task steps directly; only the selected downstream workflow may do so.
- Do not write to external review sources, pull-request threads, or tracker records.
- Do not dispatch a direct execution route without explicit recorded authorisation.

## Next

- If a dispatched follow-up remains incomplete, follow its reported next step, then invoke `resolve <target>` to reconcile it.
- When Resolve completes the selected target, no lifecycle step remains.
