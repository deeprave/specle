# Design: Add Specle changes and index

## Overview

Add `specle changes` as a read-only presentation over the existing validated change-state reader, and add `specle index <target-directory>` as an index-only mutation over the existing installed inventory and index builder.

## Architecture

```text
specle changes [--archive] [--json | --csv]
  -> discover change directories and retain per-record diagnostics
  -> report record-aware lifecycle context
  -> deterministic headered text, CSV, or structured JSON report

specle index TARGET
  -> scan_managed_inventory(TARGET/.agents)
  -> build_skill_index(installed skills)
  -> staged atomic index replacement only
```

The CLI owns argument parsing and output. Existing state, schema, lifecycle, inventory, and atomic replacement primitives remain authoritative.

## Data and errors

Active rows use `created_at`; complete archive rows use optional `archived_at`; and cancelled archive rows use optional `cancelled_at`. Text and CSV present a renderable durable timestamp as a deterministic `YYYY-MM-DD` date and use their empty value otherwise; JSON preserves a finite numeric timestamp or `null`. A malformed or unrenderable record becomes a diagnostic row before format rendering, so it remains visible without suppressing the remaining collection. A package-owned lifecycle resolver accepts a record and selected name to supply each displayed action, including `spiking` and abbreviated work. The command intentionally leaves lifecycle-invalid records inspectable. Index generation requires a valid managed `specle` skill, otherwise treats discovered managed skills as the installed inventory, and atomically writes UTF-8 with readable permissions after rejecting a directory destination.

## Test strategy

Test headered text, JSON, and CSV active/archive listings, complete filtering, ordering, dependency rendering, empty collections, optional terminal timestamps, malformed/schema-invalid diagnostic rows, selection-aware actions, and absence of writes. Test index-only creation and replacement, rejection and preservation when the managed `specle` skill is missing or invalid, readable UTF-8 output, directory rejection, and preservation of skills and policies. Run all project quality gates.
