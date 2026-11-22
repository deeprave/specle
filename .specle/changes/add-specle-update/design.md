# Design: add specle update

## Overview

Add `specle update <target-directory>` with `--dry-run` and `--force`. It will scan the installed deployment and packaged blueprint once each, read the package-owned historical manifest, determine the best-supported installed release generation, and create one explicit resource-level update plan. A normal update applies only additions, replacements, and removals that are safe against that detected generation. It preserves local modifications and all user-owned content. Force mode delegates to the same complete managed replacement policy as `init --force`.

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

Normal update requests confirmation only before overwriting content that differs from its detected generation or an unmarked same-named skill. A skill is atomic: its resources are never independently replaced or removed. A declined confirmation leaves that conflict unchanged and reports non-convergence, while accepted and conflict-free actions may still proceed. The generated index is built from the projected resulting installed managed inventory: it retains installed metadata for declined or unchanged skills and uses blueprint metadata only for accepted skill replacements. Strict installed-target validation is claimed only after no conflicts remain. `--force` deliberately bypasses all normal update confirmations and invokes the existing complete managed replacement behaviour used by `init --force`; dry-run output describes this as prospective behaviour.

Project overlay inspection is advisory only: the update never writes `.agents/project/` or `.agents/steering/`. A missing project directory or stable project README, and unexpected project-overlay layout that prevents normal onboarding assumptions, is reported with a suggestion to run `onboard`.

### Shared staged deployment transaction

Extract the staging, same-parent backup, replacement, rollback, and cleanup behaviour from `initialise_distribution` into a reusable transaction that accepts an explicit operation list. Operations are resource additions/replacements and removals; staged replacements use unique same-parent temporary paths. Existing destinations are moved to recoverable backups before a staged item is renamed into place. On any apply error, created destinations are removed and backups are restored in reverse order.

`init` keeps its current policy: stage all package-managed skill directories and policies, reject collisions unless forced, and then apply through this shared transaction. Normal `update` creates a selected resource operation list and uses the same transaction. After managed actions succeed, it generates the index from projected installed metadata while rollback recovery remains available; the index is not a staged input. Failure cleanup removes empty directories created solely by the failed operation.

## CLI and output

Add an `update` argparse subcommand:

```text
specle update TARGET_DIRECTORY [--dry-run] [--force]
```

`TARGET_DIRECTORY` must exist and is never inferred. Preflight validation uses the existing installed-target checks: readable managed files, valid metadata and dependencies, valid lifecycle declarations, and a valid generated index. A structurally invalid deployment fails before planning or mutation. Normal update asks for confirmation before any conflict replacement; preview never prompts. A declined confirmation produces a non-converged result rather than a false success.

Both preview and normal modes print the detected version, confidence/evidence, and one ordered immutable plan. Preview exits without writes. Normal mode applies that displayed plan rather than rebuilding it. The async command implementation extracts reusable update and validation operations, performs scan/read work asynchronously, and uses an asynchronous confirmation prompt. If confirmation is required, both stdin and stdout must be TTYs; otherwise the command fails clearly without applying the conflicted plan. Every update that applies managed actions runs installed-target validation afterwards and reports the result directly, without re-entering the CLI dispatcher. `--force` reports that it bypasses confirmation only when applying; dry-run says it would bypass it.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Missing target directory or `.agents` inventory | Clear command error; no changes |
| Invalid installed managed metadata, dependency, lifecycle, or index | Clear validation error; no changes |
| Invalid, unreadable, or conflicting package manifest | Clear command error; no changes |
| Indeterminate version detection | Report evidence; request confirmation only for content that diverges from available provenance or collides with scanned unmanaged content |
| Confirmation declined | Preserve that conflict, apply other safe or accepted actions, generate an index for the resulting installed inventory, and report non-convergence |
| Staging failure | Remove all temporary files and staging-created empty directories; no changes |
| Replacement/removal failure | Restore backups, report recovery paths if restoration is incomplete |
| `--force` | Explicitly report bypass; use established init force replacement semantics |

## Test strategy

Add production-behaviour tests for exact additive/subtractive and equivalent-generation detection; scanned unmanaged-policy conflicts; atomic skill update and removal; post-apply index generation; end-to-end TTY and non-TTY confirmation behaviour; update-specific staging failure cleanup; applying the displayed plan once; direct post-update validation; safe additions/upgrades/removals; partial-update reporting; force replacement including dry-run wording; advisory project guidance; and transaction recovery. Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty`, and both installed and `--blueprint` Specle validation modes.
