# Add specle changes and index

## Problem

Durable Specle state is available only by inspecting change directories and `status.json` manually. There is no quick CLI view of incomplete work or completed archive history. Separately, the generated installed-skill index can only be rebuilt incidentally through installation, despite being a derived resource that must reflect installed skill metadata.

## Goal

Add a read-only `specle changes` command that presents concise active or archived change state, backed by explicit lifecycle timestamps rather than filesystem or delivery-text inference. Add `specle index <target-directory>` to rebuild only an existing deployment's generated installed-skill index.

## Direction

`specle changes` scans the current project's discoverable change directories and, by default, reports incomplete active changes. `specle changes --archive` scans only archived changes. The human report has a header row and presents the stable name, a short date, kind, status, dependencies, and next action. A diagnostic column is included only when the report has a diagnostic row. A malformed or schema-invalid record, apart from an invalid optional archive date, or an unrenderable active timestamp remains visible with its directory name and diagnostic rather than being omitted or aborting the remaining collection. Active listings use `created_at`; complete archive listings use optional `archived_at`, and cancelled listings use optional `cancelled_at`. A missing or invalid optional terminal timestamp is shown as empty. With `--json`, it emits the same collection as a deterministic structured result containing collection identity and per-change durable fields; individual diagnostic records include a diagnostic field. With `--csv`, it emits those report fields as headered CSV; `--csv` and `--json` are alternative formats.

`specle index <target-directory>` requires an explicit target directory, scans that deployment's installed managed skills, and atomically replaces only `.agents/skills/specle/index.json`. It writes UTF-8 with normal readable permissions and reports an unsupported directory destination clearly. It does not install, update, remove, or otherwise change skills or policies.

Listing consumes durable timestamps and never derives dates from filesystem metadata at runtime. An invalid active timestamp records a row diagnostic; optional terminal timestamps are empty when missing or invalid.

Invalidly named directories are not changes and produce no synthetic change row. Report diagnostics contain only static causes; dependencies must have valid change names but need not refer to existing changes. Optional archive dates that are missing or invalid, and dates on nonterminal archive records, are empty. CSV uses CRLF record separators.

Selected normal work reports its next preparation step from the existing artifacts; S-sized normal work skips design and proceeds to tasks, with the relevant policy and skills aligned. A shared project preflight permits absent change, archive and agent directories but rejects those paths when they exist and are not directories; standalone schema export and blueprint validation are exempt. Invalid or unreadable selectors are reported without synthetic rows.

Index regeneration reports lifecycle diagnostics and refuses to write by default; `--force` permits regeneration while still reporting them and does not bypass the valid managed `specle` skill requirement. Index contents reflect the installed inventory, including valid local metadata edits.

Reuse the existing change-state discovery and introduce one package-owned record-and-selection-aware next-action resolver shared with the lifecycle contract, including `spiking` work and abbreviated workflows. The command is observational only: it exposes record diagnostics but deliberately does not replace the richer lifecycle validation or agent `status` workflow.

## Verification

Test headered text, JSON, and CSV active/archive output, optional terminal timestamps, malformed timestamps and schema records represented as diagnostics, deterministic ordering, empty collections, action mapping, no mutation, index generation from installed metadata, explicit-target handling, invalid or absent managed `specle` skill preservation, readable UTF-8 replacement, directory rejection, and index-only replacement. Run the repository quality gates.
