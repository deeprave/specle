# Add change cancel

## Problem

An active change can be deliberately abandoned or superseded, but the current lifecycle has only delivery completion as a terminal archive outcome. Removing its directory loses durable context, while calling it complete misstates what happened.

## Goal

Add `cancel <change-name>` and a terminal `cancelled` state so any explicitly named active change can be archived immediately and truthfully without relying on the local selection or delivery workflow.

## Direction

Extend lifecycle status recognition, schema support, archive validation, portable lifecycle guidance, and generated skill inventory for `cancelled`. The new skill requires a stable name and operates on that active record regardless of its non-terminal status. It records `cancelled_at`, archives the record, and clears the selector only if it exactly matches the named target.

Before mutation, the skill discovers active records that explicitly depend on the target. It presents those records and requires the user's explicit confirmation to remove the dependency from them. Once confirmed, it re-reads and updates only those precise arrays, preserving all other lifecycle data, and includes those changes with the archive mutation.

For an in-flight target, cancellation first inspects the relevant checkout and delivery facts: every staged, unstaged, and untracked worktree change; current branch; commits ahead on a recorded delivery branch; and an identified PR. It presents existing worktree content separately from its own planned mutation. Current selection does not establish ownership of that content: the agent must not attribute any of it to the named change without the user's explicit direction. It explains the consequences and requests the user's cleanup direction before changing durable lifecycle records. This makes the user responsible for the decision without silently leaving them with an unpredictable worktree.

The user may direct preservation, stashing or discarding local work, branch retention or removal, or PR closure. Cancellation itself never resets, stashes, restores, switches, cleans, stages, commits, pushes, reverts, rewrites, or deletes branches unless that separate action is explicitly requested and authorised. An open PR must not merge and requires the user's direction; a merged PR is historical fact that cancellation cannot undo. For a non-selected target without recorded delivery-branch evidence, it does not speculate that the current checkout belongs to that target.

## Verification

Exercise the status schema, lifecycle archive rules, skill metadata inventory, and cancellation workflow behaviour for named and selected/non-selected targets. Prove that dependency removal requires confirmation and is limited to the affected records; that in-flight cleanup facts require user direction; and that cancellation neither changes user-owned worktree or delivery state nor creates completion evidence without authorisation.
