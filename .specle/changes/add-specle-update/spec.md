# Add specle update

## Problem

Specle can initialise a deployment but cannot safely refresh its package-managed skills and policies when the package blueprints change.

## Goal

Add `specle update <target-directory>` to bring one explicit, valid deployment into agreement with the packaged blueprint inventory.

## Direction

Update depends on `add-specle-manifest`. It will inspect package and installed manifest generations together with the packaged blueprint and installed `.agents/` inventories. It will require a structurally valid deployment, compare live inventories for managed drift, and make no change when already current. When drift exists, it will reuse init's staged replacement, backup, recovery, obsolete-managed-content removal, index generation, and manifest distribution machinery. User-owned configuration remains untouched.

## Verification

Test invalid and current targets, each kind of managed drift, update preservation of user content, managed removals, failed staging/replacement recovery, and post-update installed-target validation. Run the repository quality gates.
