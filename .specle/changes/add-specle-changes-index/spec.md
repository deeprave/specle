# Add specle changes and index

## Problem

Durable Specle state is available only by inspecting change directories and `status.json` manually. There is no quick CLI view of incomplete work or completed archive history. Separately, the generated installed-skill index can only be rebuilt incidentally through installation, despite being a derived resource that must reflect installed skill metadata.

## Goal

Add a read-only `specle changes` command that presents concise active or archived change state, backed by explicit lifecycle timestamps rather than filesystem or delivery-text inference. Add `specle index <target-directory>` to rebuild only an existing deployment's generated installed-skill index.

## Direction

`specle changes` scans the current project's validated change records and, by default, reports incomplete active changes. `specle changes --archive` scans only archived changes. Each row presents the stable name, a short date, kind, status, dependencies, and the next action name. Active listings use `created_at`; archive listings use canonical `archived_at`.

`specle index <target-directory>` requires an explicit target directory, scans that deployment's installed managed skills, and atomically replaces only `.agents/skills/specle/index.json`. It does not install, update, remove, or otherwise change skills or policies.

The timestamp contract is supplied by `add-wrapup-skill`: active status updates use `updated_at`, and archived records use `archived_at`. Listing consumes those durable values and never derives dates from filesystem metadata at runtime.

Reuse the existing validated change-state reader and introduce one package-owned status-to-next-action mapping shared with the lifecycle contract. The command is observational only and does not replace the richer agent `status` workflow.

## Verification

Test active and archive output, dates, deterministic ordering, empty collections, invalid state diagnostics, action mapping, no mutation, index generation from installed metadata, explicit-target handling, and index-only replacement. Run the repository quality gates.
