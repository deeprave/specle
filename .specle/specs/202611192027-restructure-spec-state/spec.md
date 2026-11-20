# Restructure Specle spec state

## Problem

Shared runtime context duplicates current-selection and per-spec delivery data. It creates merge pressure across worktrees and is necessarily dirtied when external delivery completes after a PR merge.

## Goal

Make specs self-describing, make worktree selection local, and make completion derivable from delivery evidence rather than a mandatory post-merge tracked mutation.

## Decided direction

Each worktree uses an ignored one-line `.specle/current-spec` selector. Each spec owns a versioned `status.json`, identified by its directory name. Durable records contain spec-owned lifecycle and delivery facts only; optional agent handoff context is ignored and unschematized.

A merged delivery is effectively complete from its recorded reference and observed final evidence. Finalisation generates `summary.md`, moves the spec to `.specle/archive/`, and commits that durable completion state. Direct-main projects commit finalisation directly; branch-and-pull-request projects open a `<merged-branch>-completion` PR, after which unrelated work may continue on synchronised `main`.

## Intended direction

Each spec owns a versioned `status.json` and is identified by name. Active specs live under `.specle/specs/`; completed specs move to `.specle/archive/`. The generated skill index remains the skills catalogue. Worktree paths, current selection, and optional handoff cache are local runtime facts, not committed project data.

## Verification

Validate migration of representative active, queued, committed, and completed specs; concurrent worktree isolation; merged-delivery completion without dirty source state; archive discovery; and stable-name reference resolution.
