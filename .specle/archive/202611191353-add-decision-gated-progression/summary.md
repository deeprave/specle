# Summary: Decision-gated workflow progression

## Outcome

Specle can now continue successful local workflow stages automatically when a project selects decision-gated progression, while retaining explicit stops for material decisions, failed verification, triage decisions, and delivery authority.

## What changed

- Added reusable automation steering and project-level `automation.md` policy, with onboarding support.
- Removed the `implement` shortcut in favour of lifecycle-owned continuation.
- Added `activate <spec-name>` so `spec` remains planning-only and normal work starts only through an explicit action.
- Preserved named targets through automatic handoffs, including non-active work.
- Added decision-gated continuation for abbreviated work and revisions.
- Made `specle init --force` prune only obsolete skill directories marked with `specle_group`, while retaining unrelated installed skills and recovery backups.

## Evidence

The completed implementation passed 31 pytest tests, `ruff check`, `ruff format --check`, `ty check`, and `git diff --check`. Local review approved the resolved change. PR #3 merged into `main` as `1945170b1d538b8ac731d3d81d7451c76ec666d2`.

## Key decisions and limits

Creating a normal spec no longer activates it. Activation always begins its next planning stage, while normal automatic progression remains governed by the project policy. Forced installation manages only skill directories declaring `specle_group`; it does not remove unrelated local skills.

## Recommendation and follow-up

Use `spec` to queue ideas during planning and `activate <spec-name>` when work should commence. Projects that prefer step-by-step operation can retain manual progression in their project automation guidance.

## Copy-ready update

Specle now supports decision-gated progression: routine local stages continue automatically, while decisions, failed verification, triage, and delivery still pause for developer input. Normal specs are explicitly activated, and forced installs safely remove only retired Specle-managed skills.
