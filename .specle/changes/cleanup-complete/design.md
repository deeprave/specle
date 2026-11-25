# Design: Cleanup complete

## Overview

Replace the two-PR `complete` then `wrapup` sequence with one PR lifecycle. The initial `commit` creates the delivery PR and records its identity. Until finalisation, external review uses the existing `triage` → `resolve` → corrective work → `verify` → `review` → `commit` loop on that same PR. `complete` performs archival finalisation on that same branch before the PR merges, then requests auto-merge where available.

`delivery.completion` remains part of the durable status contract. It records the immutable identity of the archival-finalisation submission on the original PR: its reference, head and target branches, and the archival commit. It has no mutable event field and does not create another PR.

## Architecture

```text
approved → commit → committed / original PR open
                       │
                       ├─ external feedback → triage → resolve → corrective loop → commit
                       │
                       └─ complete → archive + completion record + push to same PR
                                              │
                                              ├─ request auto-merge
                                              └─ later complete → inspect same PR → sync main after merge
```

For direct and local delivery, `complete` keeps the existing archival and dependency-reconciliation mutation but has no PR wait. For branch delivery, `complete` must not merge before archiving. It validates the recorded original PR and settled findings, re-reads active dependency records, generates the summary, marks the delivery set complete with `archived_at`, adds `delivery.completion` using the original PR identity and archival commit, moves the set to the archive, and commits and pushes that mutation to the original branch.

After a successful push, `complete` requests auto-merge through the repository’s available PR mechanism when permitted. It reports the exact external condition if auto-merge cannot be enabled. It does not poll or subscribe for notifications. A later named `complete` accepts the archived completed record, rechecks the same recorded PR, reports an outstanding CI/review/merge condition, or, after a merge, preserves tracked local work, fast-forwards the delivery branch, restores that work, and clears the matching selector.

## Data and lifecycle

- Retain the `delivery.completion` schema object and its current immutable fields. Do not add an event field or create a second state store.
- Remove the `wrapup` inventory entry and skill directories from installed and blueprint distributions.
- Update `complete` lifecycle metadata and policy so a named archived complete record is a valid resumption target for synchronisation, without changing its terminal status or archive contents.
- Keep archived records immutable after finalisation. A resumed `complete` performs only external inspection, checkout synchronisation, and selector cleanup.
- Preserve the existing reciprocal-sidecar discovery and exact dependency cleanup rules. The parent archives every valid committed sidecar with the same original PR and completion record.

## Failure handling

- If current external findings are not all terminally resolved, `complete` stops before archival mutation and directs the established triage path.
- If the original PR is open but CI, review, merge eligibility, or auto-merge enablement is blocked, `complete` reports that condition and leaves the single original PR as the delivery artefact.
- Before switching branches or synchronising after a merge, preserve tracked staged and unstaged work in one recoverable stash. Do not include untracked or ignored files.
- If synchronisation or stash restoration fails, retain the stash and selector and provide recovery instructions. Do not mutate the archive.

## Test strategy

- Add lifecycle and inventory coverage proving `wrapup` is absent while installed and blueprint inventories remain aligned.
- Add schema coverage that `delivery.completion` remains valid and continues to reject a completion event.
- Add focused workflow-contract coverage for the same-PR branch correction loop, archive-before-final-merge ordering, completion record contents, auto-merge request/resumption guidance, direct delivery, and exact dependency removal with sidecars.
- Run the full project quality gates, installed and blueprint validation, and a reference search to confirm that managed completion-PR and `wrapup` guidance is removed without touching historical archives.
