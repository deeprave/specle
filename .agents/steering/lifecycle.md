# Spec Lifecycle

This document is the authoritative lifecycle policy for all specs. `.specle/context.json` records
an instance of this state; skills apply these transitions and must not replace them with local rules.

## States and next skill

| Status | Meaning | Next |
| --- | --- | --- |
| `defined` | Required work artifact exists but work has not started. | `spike` for a spike; otherwise `estimate` or `design`/`tasks` for small, understood work. |
| `estimated` | Complexity has been assessed. | `design` for M/L/XL; otherwise `tasks`. |
| `designed` | Technical design exists. | `tasks`. |
| `planned` | `tasks.md` exists but implementation has not started. | `build` for an active normal spec; `implement` for a queued abbreviated spec. |
| `spiking` | A time-boxed investigation is in progress. | `spike`. |
| `building` | Implementation changed or remains incomplete. | `build`, then `verify`. |
| `verified` | Every acceptance criterion and quality gate passed for the current implementation. | `review`. |
| `review-findings` | Review found actionable issues that need decisions. | `triage`. |
| `triaged` | Review decisions are recorded and routes are ready. | `resolve`. |
| `complete` | A normal implementation passed verification and review, Resolve found no remaining review action, or a spike delivered its findings. | None. |

## Ownership and transitions

| Skill | Required transition |
| --- | --- |
| `spec` | Initialize a new active spec as `defined`, with verification and review both `not-run`. |
| `spike` | Initialize an active `kind: "spike"` work item as `defined`, then set it to `spiking` while conducting read-only research. On completion, record findings and optional outcome spec, set verification and review to `not-applicable`, and mark it `complete`. |
| `estimate` | Mark the active target `estimated`; estimating a named queued spec does not change the active spec. |
| `design` | Mark the active spec `designed`. |
| `tasks` | Mark the active spec `planned`, set top-level task progress to `0/N`, and retain verification/review state unless the task plan revised implementation scope. |
| `build` | Before or with the first implementation change, mark the spec `building`, set verification and review to `stale` if they previously held evidence, and update progress after every completed task. |
| `prepare` | Invoke `bugfix` or `refactor` without implementation, then set only its matching queued record to `planned` with next `implement`. |
| `bugfix` / `refactor` | When invoked by `prepare`, create the abbreviated artefacts without execution. Otherwise, execute the abbreviated tasks and set only that record to `building` with next `verify`. |
| `verify` | For the active spec, on a clean pass set verification to `pass` and status to `verified`; on failure set verification to `fail` and status to `building`. For a named queued abbreviated spec, update only that record: pass becomes `verified` with next `review`; failure remains `building` with next set to its owning workflow. A stale or prior active-spec review becomes `not-run` after a new successful verification. |
| `review` | Run only against a verified implementation. Record raw findings in `review-findings.json`. For the active spec, `APPROVE` sets review to `pass` and status to `complete`; `REQUEST_CHANGES` sets review to `findings` and status to `review-findings`. For a named queued abbreviated spec, `APPROVE` moves only that record to `recent_specs` as `complete`; `REQUEST_CHANGES` leaves only that record queued as `review-findings` with next `triage`. |
| `triage` | Consolidate review sources and record decisions without implementation. When all current findings are decided, set the active target to `triaged`; for a named queued abbreviated target, set only its record to `triaged` with next `resolve`. |
| `resolve` | Reconcile recorded accepted-action dispatches, then dispatch any pending accepted decisions through their selected workflows. Downstream workflows own their transitions, so dispatching accepted work does not complete the originating target. An independent `spec` route from the active normal target is a terminal hand-off only after every other current finding is terminally no-action or has a completed follow-up; then complete that target before initialising the new current spec. When every current finding is terminally no-action, has a completed follow-up, or is such a settled hand-off, record the review as `resolved` and complete the selected target: set an active normal target to `complete`, or move a named queued abbreviated target to `recent_specs` as `complete` without changing the active current issue. |
| `revise` | For an active normal spec, accepted requirement changes invalidate verification and review, then set the state to `defined`, `designed`, or `planned` according to the updated artifacts. For a named queued abbreviated spec, revise only its `spec.md` and `tasks.md`, then set only that record to `planned` with next `implement`. |
| `context` | Reconcile recorded evidence with this policy; it does not manufacture a transition. |
| `status` | Report the recorded state and the next skill from this table; it never advances state. |

## Invalidation

Any source, test, task, or accepted-requirement change after a successful verification invalidates
that verification and any review based on it. The next build transition records both as `stale`.
A fresh successful verification resets the review to `not-run`; a fresh review is required before
the spec can become `complete`.

## Dependency visibility

`status` lists unfinished specs and also includes a completed spec when a pending spec explicitly
depends on it. This preserves a readable dependency graph without treating a completed dependency
as pending work.
