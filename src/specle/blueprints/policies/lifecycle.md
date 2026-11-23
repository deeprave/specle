---
specle_policy: true
---

# Spec Lifecycle

This document is the authoritative lifecycle policy for all changes. Each change's versioned
`.specle/changes/<name>/status.json` (or archived equivalent) records its durable instance state;
skills apply these transitions and must not replace them with local rules.

## States and next skill

| Status | Meaning | Next |
| --- | --- | --- |
| `defined` | Required work artifact exists but work has not started. | `activate <change-name>` for an unselected normal change or spike; otherwise its named abbreviated owner. |
| `estimated` | Complexity has been assessed. | `design` for M/L/XL; otherwise `tasks`. |
| `designed` | Technical design exists. | `tasks`. |
| `planned` | `tasks.md` exists but implementation has not started. | `build` for a selected normal change; the named `bugfix` or `refactor` for an unselected abbreviated change. |
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
| `define` | Create an unselected normal change as `defined`, then report its concise summary; it never selects local work or commences planning. |
| `activate` | The sole writer of `.specle/current-change`. Select a named resumable normal change or `defined`/`spiking` spike in the local worktree. For a normal change, immediately invoke the first missing required estimate → design → tasks stage and set a fully prepared change to `planned` before invoking `build`; for a spike, invoke `spike`. |
| `spike` | Initialize an unselected `kind: "spike"` work item as `defined`. When invoked by `activate`, set it to `spiking` while conducting read-only research. On completion, record findings and optional stable outcome-change name, set verification and review to `not-applicable`, and mark it `complete`. |
| `estimate` | Mark the selected target `estimated`; selected normal work continues to design before tasks, while a named unselected normal estimate writes only its artifact and retains next `activate`. |
| `design` | Mark the selected change `designed`; a named unselected normal design writes only its artifact and retains next `activate`. |
| `tasks` | Require a design. Mark the selected change `planned`, set top-level task progress to `0/N`, and retain verification/review state unless the task plan revised implementation scope; named unselected normal tasks retain next `activate`. |
| `build` | For a planned normal change, first present a specification alignment summary and require explicit confirmation before implementation, including in decision-gated progression. Before or with the first implementation change, mark the active change `building`, set verification and review to `stale` if they previously held evidence, and update progress after every completed task. A named committed normal target may likewise be built in place without replacing the active issue. |
| `prepare` | Invoke `bugfix` or `refactor` without implementation, then set only its matching unselected record to `planned` with next `bugfix` or `refactor`. |
| `bugfix` / `refactor` | When invoked by `prepare`, create the abbreviated artifacts without execution. Otherwise, execute the abbreviated tasks and set only that record to `building` with next `verify`. |
| `verify` | For the selected change, on a clean pass set verification to `pass` and status to `verified`; on failure set verification to `fail` and status to `building`. For a named committed normal target, update only that record: pass becomes `verified` with next `review`; failure remains `building` with next `build`. For a named unselected abbreviated change, update only that record: pass becomes `verified` with next `review`; failure remains `building` with next set to its owning workflow. A stale or prior selected-change review becomes `not-run` after a new successful verification. |
| `review` | Run only against a verified implementation. Record raw findings in `review-findings.json`. `APPROVE` sets review to `pass` and status to `approved`; `REQUEST_CHANGES` sets review to `findings` and status to `review-findings`. A named non-selected target is updated in place and never replaces the local selection. |
| `commit` | Runs the selected delivery model for an `approved` target. It moves branch-and-pull-request work to `committed` after recording a reviewable delivery reference; local-only and direct delivery record their configured final event, then proceed to archive finalisation. |
| `complete` | For every delivery model with final delivery evidence, generate its summary and archive its durable record through one recoverable, authorised finalisation delivery. For a `committed` branch-and-pull-request target it may confirm the final delivery event, merge, and synchronise where authorised; it otherwise records already-evidenced delivery. A non-selected target never replaces the local selection. |
| `triage` | Consolidate review sources and record decisions without implementation. When all current findings are decided, set the target to `triaged`. A named `committed` normal target or abbreviated target is updated in place and never replaces the local selection. |
| `resolve` | Reconcile recorded accepted-action dispatches, then dispatch any pending accepted decisions through their selected workflows. Downstream workflows own their transitions, so dispatching accepted work does not complete the originating target. A `committed` target with accepted implementation work returns through build, verify, review, approval, and commit. An independent-change route creates unselected `defined` normal work after other findings are settled, then restores the origin according to delivery history. When every current finding is terminally no-action or has a completed dispatched follow-up, record the review as `resolved`: restore a locally reviewed target to `approved` with next `commit`, or restore a previously committed target to `committed` with next `complete`. Mark a target complete only when its configured delivery outcome is already confirmed. |
| `revise` | For a selected normal change, accepted requirement changes invalidate verification and review, then set the state to `defined`, `designed`, or `planned` according to the updated artifacts. For a named committed normal target, revise it in place and set only that record to `planned` with next `build`, retaining its delivery reference. For a named unselected abbreviated change, revise only its `spec.md` and `tasks.md`, then set only that record to `planned` with next `bugfix` or `refactor`. |
| `changelist` | List pending and dependency-context changes with their recorded next stages; it never advances state. |
| `status` | Report the selected change's recorded state and next action, plus compact local worktree state; it never advances state. |

## Invalidation

Any source, test, task, or accepted-requirement change after a successful verification invalidates
that verification and any review based on it. The next build transition records both as `stale`.
A fresh successful verification resets the review to `not-run`; a fresh review and the applicable delivery operation are required before the change can become `complete`.

## Dependency visibility

`status` lists unfinished changes and also includes a completed change when a pending change explicitly
depends on it. This preserves a readable dependency graph without treating a completed dependency
as pending work.
