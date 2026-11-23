# Design: Link sidecar completion

## Overview

Make concurrent bugfix and refactor delivery explicit and symmetric. A sidecar is eligible for joint delivery only when the active parent and sidecar each carry matching relationship records with the same delivery mode and reciprocal role. Discovery uses the supplied state snapshot for reporting, while relationship mutation rereads each durable status record immediately before changing only its relationship data. Runtime validation enforces the structural reciprocal contract and delivery workflows provide the eligible sidecar set. `complete` then archives the parent and every eligible sidecar as one recoverable finalisation delivery; `wrapup` finalises the resulting single completion PR.

## Architecture

```text
bugfix/refactor creation
  -> write parent and sidecar relationship records together
  -> durable status.json records
  -> lifecycle helper discovers parent-declared candidates
  -> validates reciprocal matching relationship and readiness
  -> commit/complete use eligible sidecar set
  -> one archive mutation and one completion PR
  -> wrapup merges once and clears the parent selector
```

The change-state reader remains the sole scanner for active and archived records. A package-owned lifecycle helper will accept the already-read snapshot and a parent record, derive candidates only from the parent’s `relationships`, and return either the ordered eligible set or actionable diagnostics. It will not search unrelated records to infer membership.

## API / data

`change-status/1.0` will retain the generic relationship shape and explicitly document an optional `delivery` string. Concurrent delivery uses the literal `"with-related-change"`.

For a parent `example-change` and bugfix `fix-example`, the durable records are:

```json
// example-change/status.json
{
  "relationships": [
    {
      "change": "fix-example",
      "type": "bugfix",
      "delivery": "with-related-change"
    }
  ]
}

// fix-example/status.json
{
  "relationships": [
    {
      "change": "example-change",
      "type": "origin",
      "delivery": "with-related-change"
    }
  ]
}
```

The creation workflow rereads both current records, appends only the reciprocal relationship data, and writes both records as one planned mutation. If either record cannot be written, it reports an actionable failure and does not continue to execution with a silently half-created relationship. Specle does not support concurrent lifecycle updates or a crash-recovery transaction protocol.

The lifecycle helper validates that each parent declaration names a unique active bugfix/refactor, that the candidate’s type agrees, that it names the same parent with `type: "origin"` and `with-related-change`, and that it is in the delivery-ready state required by the caller. Runtime validation applies the structural relationship checks to active records that declare concurrent delivery; it does not duplicate caller-specific readiness checks or retroactively constrain archived legacy records. Missing, duplicate, mismatched, unsupported, or unready declarations are never included automatically.

## Delivery and archival flow

`commit` obtains the validated eligible sidecars from the parent record and records the same authorised delivery evidence on each delivered record. `complete` obtains the same set, moves the parent and eligible sidecars together from `.specle/changes/` to `.specle/archive/`, sets each to `complete`, and writes `archived_at` while preserving `updated_at`. Its completion PR contains the entire joint archival mutation, and its completion reference and event are recorded on every archived member. The parent remains the local selector; sidecars never replace it. `wrapup` merges or confirms the one recorded completion PR, synchronises the delivery branch, then clears the matching parent selector without modifying archives.

An ineligible sidecar stays in `.specle/changes/` with its own status and next workflow action. It is not an error to have an independent sidecar; it is an error to attempt joint parent delivery with a declared sidecar whose reciprocal contract is malformed or not ready.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Parent relationship has no active named sidecar | Stop the relevant joint operation with an actionable diagnostic. |
| Reciprocal record is missing, mismatched, duplicate, or lacks concurrent delivery mode | Exclude it and stop joint delivery/finalisation for correction. |
| Candidate kind is not `bugfix` or `refactor` | Reject it as an invalid sidecar declaration. |
| Candidate is not delivery-ready | Leave it active and report its recorded next action. |
| Atomic dual-record write fails | Preserve or restore the prior records and report the failed record. |
| Archive mutation fails | Retain or restore active directories and the parent selector, following existing recoverable completion behaviour. |

## Reporting and guidance

`changelist` and `status` will show declared concurrent sidecars beside their parent where useful, including status and next action. Lifecycle policy and the lifecycle/layout documentation will explain the reciprocal contract, parent-driven validation, joint archival, and the fact that an eligible sidecar has no separate `complete` or `wrapup` cycle.

The blueprint skills and installed `.agents/skills` copies for bugfix, refactor, commit, complete, wrapup, changelist, and status will remain synchronised. Existing unrelated sidecars are not migrated or inferred.

## Test strategy

Add focused production-code tests for reciprocal link creation, candidate discovery from the parent only, valid eligible sets, each invalid reciprocal condition, readiness rejection, shared delivery evidence, and one archive operation covering parent plus sidecars. Retain tests at package boundaries rather than testing Markdown instructions. Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty`, and installed/blueprint validation.
