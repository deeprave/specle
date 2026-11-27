# Add change cancel

## Problem

An active change can be deliberately abandoned or superseded, but the current lifecycle has only delivery completion as a terminal archive outcome. Removing its directory loses durable context, while calling it complete misstates what happened.

## Goal

Add `cancel <change-name>` and a terminal `cancelled` state so any explicitly named active change can be archived immediately and truthfully without relying on the local selection or delivery workflow.

## Direction

Extend lifecycle status recognition, schema support, archive validation, portable lifecycle guidance, and generated skill inventory for `cancelled`. The new skill requires a stable name and operates on that active record regardless of its non-terminal status. Normal cancellation records `cancelled_at`, but timestamp absence remains valid historical metadata; it archives the record and clears the selector only if it exactly matches the named target.

Before mutation, the skill discovers active records that explicitly depend on the target and stops if an active record cannot be read safely. It presents those records and requires the user's explicit confirmation to remove the dependency from them. It also detects matching explicit concurrent-delivery declarations in either direction, tolerates a missing reciprocal declaration, and requires separate confirmation to unlink only a surviving matching declaration. A committed parent with committed sidecars stops and explains that the user must handle the shared PR as directed, cancel each sidecar explicitly, then retry the parent. Once confirmed, it re-reads and updates only those precise arrays or relationship entries, preserving all other lifecycle data, and includes those changes with the archive mutation.

For an in-flight target, cancellation first inspects the relevant checkout and delivery facts: every staged, unstaged, and untracked worktree change; current branch; commits ahead on a recorded delivery branch; a recorded direct-delivery branch and commit; and an identified PR. It presents existing worktree content separately from its own planned mutation. Current selection does not establish ownership of that content: an explicitly named selected target is valid, but the agent must not attribute any worktree content to it without the user's explicit direction. It explains the consequences and requests the user's cleanup direction before changing durable lifecycle records. This makes the user responsible for the decision without silently leaving them with an unpredictable worktree.

The user may direct preservation, stashing or discarding local work, branch retention or removal, or PR closure. Cancellation itself never resets, stashes, restores, switches, cleans, stages, commits, pushes, reverts, rewrites, or deletes branches unless that separate action is explicitly requested and authorised. An open PR must not merge and requires the user's direction; a merged PR is historical fact that cancellation cannot undo. For a non-selected target without recorded delivery-branch evidence, it does not speculate that the current checkout belongs to that target.

## Verification

Exercise the status schema, lifecycle archive rules, and skill metadata inventory for all cancellation-supported kinds and cancellation archive invariants. Manually prove that explicit named targets, dependency removal, reciprocal unlinking, and direct-delivery and in-flight cleanup facts require confirmation and user direction; cancellation must neither change user-owned worktree or delivery state nor create completion evidence without authorisation.
