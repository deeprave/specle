# Summary: Activate and track sidecars

## Summary

Specle can activate bugfixes and refactors through the same named activation entry point as other work, while tracking active sidecars locally and linking them to concurrent normal work.

## Outcome

Developers can prepare and build named sidecars without replacing the selected normal change, inspect locally active sidecars, and complete work together or separately.

## What changed

Activation and build now route according to change kind and lifecycle state. A worktree-local registry records active sidecars, and change listings report their activity and stale entries. Concurrent normal and sidecar work is linked automatically; completion preserves links for joint delivery and removes links to surviving work when delivery is separate. Lifecycle guidance and project initialisation reflect these behaviours.

## Key decisions and limits

Sidecar activity is local to a worktree. The workflow does not inspect which code a user includes in a delivery, and S-sized normal changes may proceed without a design.
