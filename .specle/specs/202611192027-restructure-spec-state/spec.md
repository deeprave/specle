# Restructure Specle spec state

## Problem

Shared runtime context duplicates current-selection and per-spec delivery data. It creates merge pressure across worktrees and is necessarily dirtied when external delivery completes after a PR merge.

## Goal

Make specs self-describing, make worktree selection local, and make completion derivable from delivery evidence rather than a mandatory post-merge tracked mutation.

## Open questions

The proposal must decide the single local selection record, worktree-local storage mechanism, effective-completion model, archive timing, and whether any policy values belong in a regenerated context report. These decisions are intentionally unresolved before activation.

## Intended direction

Each spec owns a `status.json` and is identified by name. Active specs live under `.specle/specs/`; completed specs eventually move to `.specle/archive/`. The generated skill index remains the skills catalogue. Worktree paths are local runtime facts, not committed project data.

## Verification

Validate migration of representative active, queued, committed, and completed specs; concurrent worktree isolation; merged-delivery completion without dirty source state; archive discovery; and stable-name reference resolution.
