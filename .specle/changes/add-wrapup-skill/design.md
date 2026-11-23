# Design: Add wrapup skill

## Overview

Separate archival finalisation from the last external delivery action. `complete` will merge or confirm the implementation delivery, prepare and submit one archival completion PR, then leave the archived record intact. The new managed `wrapup` skill will only merge that recorded completion PR and synchronise the delivery branch.

## Architecture

```text
committed change
    |
complete: merge implementation PR and synchronise delivery branch
    |
create summary + archive record + completion-PR delivery evidence
    |
completion PR open; archived status remains complete and selector remains set
    |
wrapup: validate recorded completion PR -> merge -> synchronise main -> clear selector
```

`complete` and `wrapup` each preserve unrelated tracked, untracked, and ignored work before any branch-changing Git operation. The archived record is written only by `complete`; `wrapup` uses its recorded completion-delivery evidence as input and does not mutate it. Until wrapup succeeds, `.specle/current-change` retains the archived name and status/reporting commands resolve it in `.specle/archive/`.

## API and data

### Archived completion delivery

When `complete` opens a completion PR, retain the archived record at `status: "complete"` and add a durable completion-delivery object under `delivery.completion` with its PR reference, completion head branch, target branch, archive commit, and `pull-request-open` event. After an externally completed delivery, `wrapup` uses that record to decide whether to merge or only synchronise.

`complete` must recognise existing summary, archived directory, and completion-delivery evidence and resume rather than duplicate them.

### Timestamps

Add optional numeric Unix-second `updated_at` and `archived_at` fields to the versioned change-status JSON Schema and registry-backed resources.

- Every lifecycle owner that mutates an activated active record writes `updated_at` in that same update.
- Archiving writes `archived_at` and does not alter `updated_at`.
- A targeted one-off backfill supplies `archived_at` for existing archives and `updated_at` for an activated active record from the relevant `status.json` modification time before the record changes.

### Schema identifiers

Packaged schemas use logical `specle://schemas/<name>/1.0` identifiers. The registry maps these identifiers directly to package resources, so validation and schema export remain entirely local. Remove `common/1.0`: it has no consumers and its generic record shape, including `path`, represents no Specle contract.

## Lifecycle contracts

- `wrapup` is a managed Integration skill with a lifecycle declaration accepting an archived `complete` record that has `delivery.completion` evidence and retaining `complete` after its external delivery succeeds.
- Lifecycle and status guidance state that an ordinary complete record has no next action, while a complete record with an open completion PR has next action `wrapup`.
- `complete` owns all state mutation, summary creation, archival move, completion-branch commit, and completion-PR creation. `wrapup` owns only completion-PR merge, delivery-branch synchronisation, and selector removal.

## Error handling

| Condition | Behaviour |
| --- | --- |
| No recorded completion PR | `wrapup` stops without inferring one. |
| Completion PR is open with unresolved feedback | `wrapup` directs the user to named `triage`; it does not merge. |
| Completion PR is already merged | `wrapup` synchronises the delivery branch without merging again. |
| Completion PR cannot merge or required checks fail | `wrapup` reports the external state and leaves the archive unchanged. |
| Stash creation or restoration fails | Retain the named stash, avoid destructive recovery, and report the exact recovery action. |

## Synchronisation

Create matching blueprint and installed `wrapup` skill directories, update the generated installed index, and update lifecycle, delivery, status, summary, complete, and changelog guidance together. Document the conditional final stage without inventing a second status value. Update `.specle/.gitignore` to ignore only root-level JSON scratch files and synchronise the zsh shell-safety instruction in `.agents/AGENTS.md` and its blueprint. Do not add compatibility aliases or mutate archived records after the archival commit.

## Test strategy

Add production-code tests for change-status timestamp schema validation, registry resolution of package-owned schema identifiers, runtime validation of completion-delivery evidence where needed, and any new package helper that derives the conditional `wrapup` next action. Do not add tests that inspect Markdown skills or workflow files. Run the repository quality gates and inventory validation.
