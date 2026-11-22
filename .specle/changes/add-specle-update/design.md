# Design: add specle update

## Overview

Add `specle update <target-directory>` with `--dry-run`, `--yes`, and `--force`. It will scan the installed deployment and packaged blueprint once each, read the package-owned historical manifest, determine the best-supported installed release generation, and create one explicit resource-level update plan. A normal update applies only additions, replacements, and removals that are safe against that detected generation. If that plan contains conflicts, it reports all of them and exits non-zero without mutation; `--yes` explicitly applies that complete selective plan. It preserves local modifications and all user-owned content unless `--yes` selects their reported replacement. Force mode delegates to the same complete managed replacement policy as `init --force`.

The manifest remains a package resource only. It is never copied into `.agents`.

## Architecture

```text
package blueprints ──scan──> DistributionInventory ─┐
                                                  ├─> update planner ─> report / transaction
package manifest ──parse──> manifest generations ─┘                         │
                                                                            ├─ dry run: print only
target/.agents ──scan──> DistributionInventory ──────────────────────────────└─ update: staged apply
```

### Shared inventory and manifest model

Rename the existing scan result to `DistributionInventory`, because it represents both managed content and discovered unmanaged conflicts. Each entry is keyed by its stable path below `.agents`, such as `skills/verify/SKILL.md` or `policies/lifecycle.md`. Unmanaged policy documents are recorded so a later package policy cannot be mistaken for an absent path. Generated `skills/specle/index.json` remains excluded from blueprint resources and is generated after a successful apply.

Move update-specific models and planning into a dedicated module, leaving scanning in `inventory.py`. Shared release-generation and update-plan records live in a leaf module so manifest parsing and update planning do not rely on a concealed import relationship. Action and confidence values use explicit closed types. Manifest parsing continues to reject malformed or conflicting text lines with explicit exceptions, never assertions, and exposes all complete release generations without reparsing the source inventory.

The planner receives exactly three already-scanned inputs: the package blueprint inventory, the target installed inventory, and parsed manifest generations. It does not walk either inventory again. It produces:

- detected version and confidence evidence;
- additions, upgrades, removals, and conflicts requiring confirmation;
- missing or unexpected project-overlay guidance; and
- whether there is any managed drift to apply.

Version detection checks exact inventory equality before partial comparison. If consecutive release generations have equivalent exact inventories, the latest matching version represents the equivalence class and remains `exact`. Partial comparison accounts for matches, missing expected resources, unexpected installed resources, and mismatches. The report exposes its evidence rather than claiming certainty from incomplete data: an exact full match is `exact`; a unique best-supported partial match is `likely`; ties, no matching evidence, or incompatible evidence are `indeterminate`.

### Update planning rules

For each managed resource path, compare the detected historical checksum, installed checksum, and current blueprint checksum:

| Situation | Normal update action |
| --- | --- |
| Present only in current blueprint and absent from unmanaged inventory | Add |
| Incoming path occupied by unmanaged scanned resource | Request confirmation before replacement |
| Every resource of an installed skill matches its detected generation and the skill differs from current blueprint | Replace the entire skill |
| Any resource of an installed skill differs from its detected generation | Confirm replacement or removal of the entire skill |
| Present in detected generation but absent from current blueprint, with unchanged installed checksum | Remove policy resource |
| Installed differs from detected generation | Request confirmation before replacement/removal |
| Unmarked skill has the name of an incoming managed skill | Request confirmation before replacement |
| Same installed and current checksum | No action |

Normal update flags overwrites of content that differs from its detected generation or an unmarked same-named skill as confirmation-required. A skill is atomic: its resources are never independently replaced or removed. Without `--yes`, any confirmation-required action causes the complete plan to be reported and the command to exit non-zero without applying even otherwise-safe actions. `--yes` approves every reported confirmation-required action and applies the displayed selective plan exactly once. The generated index is built from the projected resulting installed managed inventory. Strict installed-target validation follows every applied update. `--force` deliberately bypasses selective planning and invokes the existing complete managed replacement behaviour used by `init --force`; dry-run output describes this as prospective behaviour.

Project overlay inspection is advisory only: the update never writes `.agents/project/` or `.agents/steering/`. A missing project directory or stable project README, and unexpected project-overlay layout that prevents normal onboarding assumptions, is reported with a suggestion to run `onboard`.

### Shared staged deployment transaction

Extract the staging, same-parent backup, replacement, rollback, and cleanup behaviour from `initialise_distribution` into a reusable transaction that accepts an explicit operation list. Operations are resource additions/replacements and removals; staged replacements use unique same-parent temporary paths. Existing destinations are moved to recoverable backups before a staged item is renamed into place. On any apply error, created destinations are removed and backups are restored in reverse order.

`init` keeps its current policy: stage all package-managed skill directories and policies, reject collisions unless forced, and then apply through this shared transaction. Normal `update` creates a selected resource operation list and uses the same transaction. After managed actions succeed, it generates the index from projected installed metadata while rollback recovery remains available; the index is not a staged input. Each temporary path is registered for cleanup before its copy begins, so failure cleanup removes partial temporary paths and empty directories created solely by the failed operation.

## CLI and output

Add an `update` argparse subcommand:

```text
specle update TARGET_DIRECTORY [--dry-run] [--yes] [--force]
```

`TARGET_DIRECTORY` must exist and is never inferred. Preflight validation uses the existing installed-target checks: readable managed files, valid metadata and dependencies, valid lifecycle declarations, and a valid generated index. A structurally invalid deployment fails before planning or mutation. Normal update never prompts: it reports every conflict in the plan, makes no changes, and exits non-zero. `--yes` approves every reported conflict for that invocation; preview never mutates.

Both preview and normal modes print the detected version, confidence/evidence, and one ordered immutable plan. Preview exits without writes. A normal conflict plan exits non-zero before writing; `--yes` applies that displayed plan rather than rebuilding it. The command implementation uses AnyIO-compatible scan/read work and reusable validation operations directly, without re-entering the CLI dispatcher or reading interactive terminal input. Every update that applies managed actions runs installed-target validation afterwards and reports the result directly. `--force` reports that it bypasses selective confirmation only when applying; dry-run says it would do so.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Missing target directory or `.agents` inventory | Clear command error; no changes |
| Invalid installed managed metadata, dependency, lifecycle, or index | Clear validation error; no changes |
| Invalid, unreadable, or conflicting package manifest | Clear command error; no changes |
| Indeterminate version detection | Report evidence; mark only content that diverges from available provenance or collides with scanned unmanaged content as requiring `--yes` |
| Confirmation-required plan without `--yes` | Report every conflict; make no changes; exit non-zero |
| Staging failure | Remove every temporary file, including a partial path created by a failed copy, and staging-created empty directories; no changes |
| Replacement/removal failure | Restore backups, report recovery paths if restoration is incomplete |
| `--force` | Explicitly report bypass; use established init force replacement semantics |

## Test strategy

Add production-behaviour tests for exact additive/subtractive and equivalent-generation detection; scanned unmanaged-policy conflicts; atomic skill update and removal; post-apply index generation; complete conflict reporting without mutation; `--yes` selective approval; update-specific staging failure cleanup including partial copy paths; applying the displayed plan once; direct post-update validation; safe additions/upgrades/removals; force replacement including dry-run wording; advisory project guidance; and transaction recovery. Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty`, and both installed and `--blueprint` Specle validation modes.
