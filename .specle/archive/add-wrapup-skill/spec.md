# Add wrapup skill

## Problem

In a branch-and-PR model, archival finalisation needs its own completion PR after the implementation PR merges. The workflow must prepare that archive record and PR once, then provide a clear final operation to merge it without mutating the now-archived record.

## Goal

Have `complete` perform all archival finalisation and submit any completion PR. Add `wrapup` to merge that recorded PR and synchronise the delivery branch only.

## Direction

After a committed change reaches its configured final delivery event, `complete` creates the human summary, records `archived_at`, safely moves the durable record into `.specle/archive/`, and uses a dedicated completion branch/PR where policy requires it. The selector remains until the completion PR finishes, so subsequent commands can resolve the archived change. The lifecycle then points to `wrapup`, which merges the recorded completion PR, synchronises the delivery branch, and clears the selector without changing archived artefacts. Status records gain optional `updated_at` for pre-archive mutation and `archived_at` for archival. Every lifecycle owner that mutates an activated record must write `updated_at`, while the versioned schema and registry distribute the contract. Targeted one-off backfills use existing `status.json` modification times. Packaged schemas use Specle-owned `specle://schemas/...` identifiers rather than GitHub-shaped URLs, and the unused common schema is removed.

## Verification

Test lifecycle transitions and next-action reporting, timestamp mutation and backfill rules, completion and wrapup preconditions, summary/archive behaviour, completion-branch/PR recovery paths, schema registry resolution, and preservation of unrelated working-tree content. Validate the updated skill inventory and lifecycle graph.
