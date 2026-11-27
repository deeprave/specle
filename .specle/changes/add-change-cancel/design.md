# Design: Add change cancellation

## Overview

Add `cancel` as the explicit lifecycle owner for terminal cancellation. It archives one named active change as `cancelled`, without representing cancellation as delivery. Before it mutates durable state, the skill gathers the dependency and in-flight cleanup facts needed for a user-directed decision.

## Architecture

```text
cancel <stable-name>
        |
        +-- resolve one active record by exact name
        |     +-- reject missing or archived terminal targets
        |
        +-- preflight
        |     +-- re-read active dependency and reciprocal relationship records
        |     +-- inspect unowned local worktree and recorded delivery facts
        |     +-- query only the recorded PR reference when present
        |
        +-- user direction
        |     +-- confirm removal from direct dependents and an explicit reciprocal partner
        |     +-- direct any worktree, branch, or PR cleanup
        |
        +-- cancellation mutation
              +-- re-read and remove only confirmed dependency entries or reciprocal link
              +-- write target status cancelled, updated_at, cancelled_at
              +-- move target to archive
              +-- remove matching selector only
```

The `cancel` skill is an agent workflow, not a new Python CLI command or background service. Its portable blueprint and installed copy remain the executable guidance for agents. It performs no commit, push, branch, pull-request, tracker, or worktree cleanup operation unless the user separately and explicitly directs that action.

## Lifecycle and record contract

Add `cancelled` to the shared inventory lifecycle-status set. The `cancel` skill declares every active non-terminal status as accepted and declares transitions from each to terminal `cancelled`. Runtime status derivation must allow that generic terminal transition for every accepted kind, including spikes, without admitting unrelated planning or implementation states to a spike. `complete` remains a distinct terminal state whose semantics are successful delivery; `cancelled` has no next action and is never accepted by active-work skills.

The change-status schema continues to permit extensible lifecycle metadata, and documents `cancelled_at` as an optional numeric Unix-second timestamp alongside `updated_at` and `archived_at`. Normal cancellation writes it, but runtime validation accepts cancelled archives when optional lifecycle timestamps are absent. Runtime validation still requires a cancelled record to be archived, while archive validation accepts only registered terminal statuses. It retains diagnostics for any other archived status.

The cancellation target records `status: "cancelled"`, current `updated_at`, and current `cancelled_at`, then moves to `.specle/archive/<name>/`. It does not add `archived_at`, `delivery.completion`, a summary, a delivery event, or fabricated review/verification data. Existing data is retained unchanged.

## Preflight and user-directed cleanup

`cancel` requires the stable target name and resolves it only among active records. It does not select a target from `.specle/current-change`; that selector is only consulted to decide whether to remove an exact matching selection after cancellation.

The preflight reads every active `status.json` to find direct dependency arrays containing the target name. An unreadable or malformed active record stops cancellation before any durable write. If dependents are found, it presents their names and statuses and pauses for explicit confirmation. A negative response or different user-directed resolution ends the operation before durable state changes. After confirmation, it re-reads each affected file, removes only the target entry, and preserves its lifecycle state, timestamps, delivery evidence, relationships, and other fields.

The preflight recognises matching explicit concurrent-delivery declarations in either direction. It never infers a sidecar, but a missing reciprocal declaration does not block cancellation: for every active partner with a matching declaration, it presents that partner and requires separate confirmation before removing only the matching relationship that exists on the surviving record. If a committed normal parent has committed sidecars, cancellation stops before mutation and explains the required order: handle the shared PR as directed, explicitly cancel each sidecar, then retry the parent. The confirmed dependency updates, optional relationship removals, and target archive move form one local recoverable mutation.

For a current target or one with recorded delivery evidence, inspect `git status --short --untracked-files=all`, the checked-out branch, and commits ahead of the recorded delivery target. Direct/local delivery evidence (`delivery.branch` and `delivery.commit`) is also presented as an already-landed commit whose branch disposition needs user direction. Present every pre-existing staged, unstaged, and untracked path as user-owned and unattributed. Do not infer ownership from current selection, directory names, or branch names. When the target is non-selected and lacks recorded delivery-branch evidence, do not treat the current checkout as target-related.

When delivery evidence contains a PR reference, inspect that specific PR. An open PR must not merge; report it and request user direction for closure or other handling. A merged PR remains historical fact: report that any delivered code remains in the target branch and ask the user to choose subsequent remediation. If the PR cannot be inspected, report that fact and request direction rather than inferring its state.

No cleanup action is automatic. On explicit user direction, ordinary Git or GitHub actions follow their existing authorisation and safety boundaries. Without such a direction, cancellation must stop before durable mutation whenever preflight identifies worktree content, branch commits, or a recorded PR requiring a decision.

## Guidance and reporting

Synchronise the portable and installed lifecycle policy, `cancel` skill, skill index, entrypoint workflow sequence, activation, explanation, and lifecycle documentation. A selected archived cancelled record is terminal and replaceable by activation. `changes` should continue to list active actionable work only, but describe both terminal archive states accurately and include a cancelled archive only as explicit dependency context. Read-only tools may explain cancelled records by name; lifecycle owners reject them.

## Error handling

- A missing, archived, or already terminal target stops without mutation.
- An invalid dependency record or refusal to confirm its removal stops before any write.
- An unavailable Git, branch, or PR inspection is reported as unavailable; it is not replaced with inferred facts.
- A failure while writing the local archive mutation leaves the original active record and confirmed dependents recoverable for user inspection; no cleanup command discards work to recover.

## Test strategy

- Add inventory and lifecycle-graph coverage for the `cancelled` terminal state and `cancel` metadata.
- Add schema and runtime lifecycle coverage for optional `cancelled_at`, archive-only cancelled records, every supported cancellation kind, and continued rejection of non-terminal archived records.
- Add focused executable fixtures for generic terminal-kind handling, archive invariants, and relationship validation.
- Manually exercise the workflow guidance against explicit-name selection, direct dependency and one-sided reciprocal-link confirmation, committed parent-sidecar ordering, clean and dirty checkouts, direct delivery, open PRs, and merged PRs without adding recurring CI workflow simulation to the project test suite.
- Run the focused tests and the project quality gates: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and `uv run specle validate --verbose .`.
