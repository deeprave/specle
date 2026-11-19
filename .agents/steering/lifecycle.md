# Spec Lifecycle

This document is the authoritative lifecycle policy for all specs. `.specle/context.json` records
an instance of this state; skills apply these transitions and must not replace them with local rules.

## States and next skill

| Status | Meaning | Next |
| --- | --- | --- |
| `defined` | Required work artifact exists but work has not started. | `spike` for a spike; otherwise `estimate` or `design`/`tasks` for small, understood work. |
| `estimated` | Complexity has been assessed. | `design` for M/L/XL; otherwise `tasks`. |
| `designed` | Technical design exists. | `tasks`. |
| `planned` | `tasks.md` exists but implementation has not started. | `build` for an active normal spec; the next `bugfix` or `refactor` for a queued abbreviated spec. |
| `spiking` | A time-boxed investigation is in progress. | `spike`. |
| `building` | Implementation changed or remains incomplete. | `build`, then `verify`. |
| `verified` | Every acceptance criterion and quality gate passed for the current implementation. | `review`. |
| `approved` | Local Specle review passed; external delivery is not necessarily complete. | `commit`. |
| `committed` | A branch-and-pull-request delivery was created or updated and awaits its configured final event. | `complete`, or named `triage` for external feedback. |
| `review-findings` | Review found actionable issues that need decisions. | `triage`. |
| `triaged` | Review decisions are recorded and routes are ready. | `resolve`. |
| `complete` | The configured delivery outcome was confirmed, Resolve found no remaining review action, or a spike delivered its findings. | None. |

## Ownership and transitions

| Skill | Required transition |
| --- | --- |
| `spec` | Initialize a new active spec as `defined`, with verification and review both `not-run`. |
| `spike` | Initialize an active `kind: "spike"` work item as `defined`, then set it to `spiking` while conducting read-only research. On completion, record findings and optional outcome spec, set verification and review to `not-applicable`, and mark it `complete`. |
| `estimate` | Mark the active target `estimated`; estimating a named queued spec does not change the active spec. |
| `design` | Mark the active spec `designed`. |
| `tasks` | Mark the active spec `planned`, set top-level task progress to `0/N`, and retain verification/review state unless the task plan revised implementation scope. |
| `build` | Before or with the first implementation change, mark the active spec `building`, set verification and review to `stale` if they previously held evidence, and update progress after every completed task. A named committed normal target may likewise be built in place without replacing the active issue. |
| `prepare` | Invoke `bugfix` or `refactor` without implementation, then set only its matching queued record to `planned` with next `bugfix` or `refactor`. |
| `bugfix` / `refactor` | When invoked by `prepare`, create the abbreviated artefacts without execution. Otherwise, execute the abbreviated tasks and set only that record to `building` with next `verify`. |
| `verify` | For the active spec, on a clean pass set verification to `pass` and status to `verified`; on failure set verification to `fail` and status to `building`. For a named committed normal target, update only that record: pass becomes `verified` with next `review`; failure remains `building` with next `build`. For a named queued abbreviated spec, update only that record: pass becomes `verified` with next `review`; failure remains `building` with next set to its owning workflow. A stale or prior active-spec review becomes `not-run` after a new successful verification. |
| `review` | Run only against a verified implementation. Record raw findings in `review-findings.json`. `APPROVE` sets review to `pass` and status to `approved`; `REQUEST_CHANGES` sets review to `findings` and status to `review-findings`. A named non-active target is updated in place and never replaces the active current issue. |
| `commit` | Runs the selected delivery model for an `approved` target. It moves branch-and-pull-request work to `committed` after recording a reviewable delivery reference; local-only and direct delivery move to `complete` after their configured final event. |
| `complete` | For a `committed` branch-and-pull-request target, confirm the configured final delivery event. Where authorised, it may merge and synchronise the delivery branch; it otherwise records already-evidenced delivery. A non-active target never replaces the active current issue. |
| `triage` | Consolidate review sources and record decisions without implementation. When all current findings are decided, set the target to `triaged`. A named `committed` normal target or abbreviated target is updated in place and never replaces the active current issue. |
| `resolve` | Reconcile recorded accepted-action dispatches, then dispatch any pending accepted decisions through their selected workflows. Downstream workflows own their transitions, so dispatching accepted work does not complete the originating target. A `committed` target with accepted implementation work returns through build, verify, review, approval, and commit. An independent-spec route creates queued `defined` normal work after other findings are settled, then restores the origin according to delivery history. When every current finding is terminally no-action or has a completed dispatched follow-up, record the review as `resolved`: restore a locally reviewed target to `approved` with next `commit`, or restore a previously committed target to `committed` with next `complete`. Mark a target complete only when its configured delivery outcome is already confirmed. |
| `revise` | For an active normal spec, accepted requirement changes invalidate verification and review, then set the state to `defined`, `designed`, or `planned` according to the updated artifacts. For a named committed normal target, revise it in place and set only that record to `planned` with next `build`, retaining its delivery reference. For a named queued abbreviated spec, revise only its `spec.md` and `tasks.md`, then set only that record to `planned` with next `bugfix` or `refactor`. |
| `context` | Reconcile recorded evidence with this policy; it does not manufacture a transition. |
| `status` | Report the recorded state and the next skill from this table; it never advances state. |

## Invalidation

Any source, test, task, or accepted-requirement change after a successful verification invalidates
that verification and any review based on it. The next build transition records both as `stale`.
A fresh successful verification resets the review to `not-run`; a fresh review and the applicable delivery operation are required before the spec can become `complete`.

## Dependency visibility

`status` lists unfinished specs and also includes a completed spec when a pending spec explicitly
depends on it. This preserves a readable dependency graph without treating a completed dependency
as pending work.
