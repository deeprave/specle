# Design: Add Specle status

## Overview

Add a read-only `specle status` command that combines the existing durable change snapshot and lifecycle resolver with a compact Git worktree summary. The command does not modify selectors, records, the registry, or Git state.

## Architecture

The CLI parser dispatches status for the current directory. A status reporting component reads the existing change snapshot and worktree-local sidecar registry, resolves the selected active or archived record without guessing, reads optional hand-off context, and independently invokes Git to obtain branch and porcelain status. The renderer presents available sections and static diagnostics. Existing state readers and next-action logic remain authoritative.

## Data and reporting

Display the selected change name, kind, status, derived next action and available durable lifecycle dates on one labelled date-only line; show the same date line for active sidecars. Report an absent selection as no change in progress without selector validity checks or diagnostic-text inspection. Report registry-listed active sidecars once each with labelled kind, status and derived next action, regardless of delivery links. This is status display, not a separate validation pass. Never infer relationships from files or task progress.

Pass `--no-optional-locks` to Git. Display branch name or detached HEAD and compact counts of modified, added, deleted, renamed, untracked, conflicted and type-changed entries; omit individual paths. Use NUL-delimited Git porcelain output so unusual paths and rename entries are parsed reliably, counting an entry once in each applicable category. A clean worktree is reported explicitly.

## Context summaries

Read optional `.specle/context.json` as display data and parse recognisable date values and display their calendar date only, preserving unrecognised values. Display milestones first, todos next and other object lists after them. Group consecutive entries by date and change or subject, without repeating those values until they change. Show each milestone subject under its optional change and omit milestone details; indent other list details below their subject and truncate plain-text lines only as needed to remain shorter than 80 characters; Markdown labels may exceed the limit. Tolerate missing optional fields and missing context without blocking other output. Do not add a validation workflow.

## Errors

Read-only state and Git failures are reported as static, non-data-bearing diagnostics where applicable. Each Git inspection failure leaves other status details available. Do not validate or repair the selector or infer a replacement; unreadable change collections fail fast. Preserve existing CLI preflight conventions.

## Status skill parity

Update the installed and packaged status skills to report the same change, sidecar, Git and optional context categories and apply the same calendar-date and line-length rules as the CLI. Both interfaces remain read-only and display-oriented.

## Test strategy

Exercise missing, valid, archived and malformed selections; registered sidecars and their next actions; optional context lists, calendar-date rendering and line length; available timestamps and next actions; clean, dirty and detached worktrees; unusual paths and renames; and independent Git command failures. Run the project quality gates through `uv`.

## Markdown output

`specle status --markdown` emits the same information as Markdown source using headings and grouped bullets. Plain-text output remains the default.
