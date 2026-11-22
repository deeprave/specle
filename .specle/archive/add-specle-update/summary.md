# Summary: Add Specle update

## Summary

Specle can now safely update an installed managed distribution from its packaged blueprints while preserving user-owned project guidance and making every replacement decision explicit.

## Outcome

`specle update <target>` identifies the installed package generation, reports the planned changes, and updates managed skills and policies. `--dry-run` previews the plan, `--yes` accepts every reported selective replacement, and `--force` performs the broader managed replacement used by initialisation.

## What changed

- Added manifest-based version detection and an update plan for managed skills and policies.
- Added safe staged replacement, rollback, generated-index rebuilding, and post-update validation.
- Added clear conflict handling: ordinary updates make no changes when a replacement needs approval.
- Added the `--yes` approval flag and documentation for update behaviour.

## Key decisions and limits

Updates do not prompt interactively. A conflicted selective plan is reported in full and requires an explicit rerun with `--yes`; `--force` remains the deliberate full managed replacement path.
