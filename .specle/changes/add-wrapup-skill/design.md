# Design: Add wrapup skill

## Overview

Separate archival finalisation from the last external delivery action. `complete` will merge or confirm the implementation delivery, prepare and submit one archival completion PR, then leave the archived record intact. The new managed `wrapup` skill will only merge that recorded completion PR and synchronise the delivery branch.

## Architecture

```text
committed change
    |
complete: merge implementation PR and synchronise delivery branch
    |
create summary + archive record + archive commit
    |
open one completion PR, then commit its delivery evidence to the same branch
    |
completion PR open; archived status remains complete and selector remains set
    |
wrapup: validate recorded completion PR -> merge -> synchronise main -> clear selector
```

`complete` preserves unrelated tracked, untracked, and ignored work in one stash for the entire finalisation sequence. The archived record is written only by `complete`; `wrapup` uses its recorded completion-delivery evidence as input and does not mutate it. Until wrapup succeeds, `.specle/current-change` retains the archived name and status/reporting commands resolve it in `.specle/archive/`. A direct delivery without a completion PR removes the matching selector during finalisation.

## API and data

### Archived completion delivery

When `complete` opens a completion PR, it first creates and pushes the archival commit, then opens or identifies one completion PR. It records the resulting reference in a follow-up commit on that same branch. The archived record remains at `status: "complete"` and holds durable completion-delivery evidence: PR reference, completion head branch, target branch, archive commit, and `pull-request-open` event. After an externally completed delivery, `wrapup` uses that record to decide whether to merge or only synchronise.

`complete` must recognise existing summary, archived directory, completion branch, completion PR, and delivery evidence, resuming the next missing step without duplicating any of them.

### Completion-review delivery

An explicit archived triage writes only the archive's `review-findings.json`. Accepted decisions create named related bugfix or refactor work outside the archive. Once those decisions are resolved, `commit` uses the selected archived completion record by default and commits its `review-findings.json` plus the resolved related corrective work to the recorded completion branch, updating the same completion PR. It does not change the archived status, timestamps, delivery evidence, summary, or other archived artifacts.

`wrapup` then has a narrow role: validate that the recorded completion PR is ready, preserve local tracked, untracked, and ignored work with `git stash --all`, merge the PR, switch to the recorded delivery branch, fast-forward from upstream, restore the stash, and remove `.specle/current-change` only when restoration succeeds and the selector still names the archived record.

### Timestamps

Add optional numeric Unix-second `updated_at` and `archived_at` fields to the versioned change-status JSON Schema and registry-backed resources.

- Every lifecycle owner that mutates an activated active record writes `updated_at` in that same update.
- Archiving writes `archived_at` and does not alter `updated_at`.
- A targeted one-off backfill supplies `archived_at` for existing archives and `updated_at` for an activated active record from the relevant `status.json` modification time before the record changes.
- Every delivery model writes `updated_at` when it records active delivery evidence. `complete` alone transitions the record to `complete` and writes `archived_at`.

### Schema identifiers

Packaged schemas use logical `specle://schemas/<name>/1.0` identifiers. The registry maps these identifiers directly to package resources, so validation and schema export remain entirely local. Remove `common/1.0`: it has no consumers and its generic record shape, including `path`, represents no Specle contract.

## Lifecycle contracts

- `wrapup` is a managed Integration skill with a lifecycle declaration accepting an archived `complete` record that has `delivery.completion` evidence and retaining `complete` after its external delivery succeeds.
- Lifecycle and status guidance state that an ordinary complete record has no next action, while a complete record with an open completion PR has next action `wrapup`.
- `complete` owns all state mutation, summary creation, archival move, completion-branch commit, and completion-PR creation for every committed delivery model. Its metadata and introduction describe that general scope; only the branch-and-pull-request steps are model-specific. `wrapup` owns only completion-PR merge, delivery-branch synchronisation, and selector removal.
- A selected archived record with pending wrapup is unfinished: `activate` cannot replace its selector, and `changelist` reports it as pending work.
- An archive is immutable except for explicit completion-PR triage, which writes only `review-findings.json`. `revise`, `build`, and local `review` reject archived targets. Accepted corrective decisions become independent changes.

## Error handling

| Condition | Behaviour |
| --- | --- |
| No recorded completion PR | `wrapup` stops without inferring one. |
| Completion PR is open with unresolved feedback | `wrapup` directs the user to named `triage`; it does not merge. |
| Completion PR is already merged | `wrapup` synchronises the delivery branch without merging again. |
| Completion PR cannot merge or required checks fail | `wrapup` reports the external state and leaves the archive unchanged. |
| Stash creation or restoration fails | Retain the named stash, avoid destructive recovery, and report the exact recovery action. |

## Synchronisation

Create matching blueprint and installed `wrapup` skill directories, update the generated installed index, and update lifecycle, delivery, status, changelist, triage, resolve, commit, complete, and changelog guidance together. Document the conditional final stage without inventing a second status value. Update `.specle/.gitignore` to ignore only root-level JSON scratch files and synchronise the zsh shell-safety instruction in `.agents/AGENTS.md` and its blueprint. Do not add compatibility aliases or mutate archived records after archival finalisation except for separately delivered external-triage findings.

## Test strategy

Add production-code tests for change-status timestamp schema validation, registry resolution of package-owned schema identifiers, runtime validation of completion-delivery evidence where needed, and any new package helper that derives the conditional `wrapup` next action. Do not add tests that inspect Markdown skills or workflow files. Run the repository quality gates and inventory validation.
