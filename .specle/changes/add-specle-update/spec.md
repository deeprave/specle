# Add specle update

## Problem

Specle can initialise a deployment but cannot safely refresh its package-managed skills and policies when the package blueprints change.

## Goal

Add `specle update <target-directory>` to bring one explicit, valid deployment into agreement with the packaged blueprint inventory.

## Direction

Update uses exact-first package manifest generation detection and compares managed plus scanned unmanaged inventory to produce one immutable add, upgrade, remove, and confirmation plan. `--dry-run` reports it without mutation; ordinary update displays and applies that exact plan once. A path occupied by unmanaged content, including an unmarked policy document, is a confirmation conflict rather than an absent resource. Confirmations require interactive stdin and stdout; otherwise the command fails clearly. Managed actions finish before the generated index is produced from the resulting installed inventory. Every applied update is validated afterwards and reports the result. `--force` bypasses confirmations using init-equivalent replacement semantics. The manifest remains package-only provenance and is never installed into `.agents/`.

## Verification

Test version detection and confidence reporting, dry-run non-mutation and plan output, each kind of managed drift, preservation of modified and user-owned content, force-mode replacement, managed removals, failed staging/replacement recovery, and post-update installed-target validation. Run the repository quality gates.
