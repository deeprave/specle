# Rename status to changelist

## Problem

The current `status` skill lists every pending change, dependencies, and sidecars. That is valuable inventory behaviour, but it is not the focused answer a developer expects from a command named `status`.

## Goal

Rename the existing inventory workflow to `changelist` and introduce `status` as a compact, read-only current-work and worktree orientation skill.

## Direction

Move the existing managed skill directory and its inventory metadata from `status` to `changelist`, updating only references that mean the pending-change inventory. Create a new managed `status` skill that reads the local selector and lifecycle policy, reports the selected change's state and next action, optionally summarises it, and reports compact Git worktree information. It must distinguish the primary checkout from a linked worktree and summarise changes without dumping every path. Update the applicable human-facing lifecycle and workflow references so the two roles are discoverable outside skill source.

The blueprint remains canonical. Synchronise the active `.agents` inventory, remove the retired inventory skill, and regenerate the managed index. No runtime command, schema, compatibility alias, or legacy support is required.

## Verification

Review the renamed and new skills for unambiguous distinct roles, exact blueprint/installed synchronisation, read-only boundaries, lifecycle-next derivation, and compact worktree reporting. Validate the managed inventories and run the repository quality gates.
