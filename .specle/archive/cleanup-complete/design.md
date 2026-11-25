# Design: Cleanup complete

## Overview

Branch delivery has an original-PR phase and, only after premature original-PR merge, a recovery-PR phase. Both use `complete` and retain one active delivery phase at a time.

```text
approved → commit → committed / original PR open
                         │
                         ├─ external feedback → triage → resolve → corrective loop → same PR
                         │
                         └─ complete → archive + immutable PR identity → push → auto-merge
                                                                        │
                  original PR already merged before archive delivery ──┘
                                   │
                                   └─ sync main → <branch>-complete → recovery PR → auto-merge
```

`delivery` retains the implementation event. For branch delivery, `delivery.completion` identifies the PR carrying archival finalisation with `reference`, `head_branch`, and `target_branch`. It excludes a commit hash: the archive commit is discoverable in Git history, and embedding its own SHA requires a self-reference or later archive mutation.

## Delivery phases and resumption

An active committed target uses its recorded delivery branch. After archival mutation, explicit `complete <name>` discovers the first incomplete phase: archive commit, branch push, PR creation/update, auto-merge request, merge confirmation, or target synchronisation.

If the original PR is already merged before archive delivery, completion synchronises the recorded target branch, creates or reuses `<delivery-branch>-complete`, archives the delivery set there, and opens an auto-merge PR carrying the missed archive commit. If tracked work prevents the branch switch, it stops and lets the user decide how to preserve it; untracked files do not require preservation. Recovery does not add identity to, or otherwise rewrite, the immutable archive. Normal completion never creates this branch.

The checkout must equal the phase branch: original delivery branch until recovery begins, then the recorded recovery branch. A mismatch is an actionable stop, not a trigger for automatic stash or branch switching.

After archive finalisation, the archive is immutable. `triage` and `resolve` reject it; later defects are independent work. A resumed `complete` only finishes an eligible PR merge, synchronises the target branch, and removes the matching selector.

## Direct delivery

Local-only and direct shared-upstream delivery use the implementation commit and branch already recorded by `commit`. Their `complete` operation archive-finalises without `delivery.completion`. No PR reference, event, or fabricated completion commit is valid.

## Schema and archive migration

Remove `commit` from `delivery.completion` in current `1.0` schema. Update every historical archived status record carrying it in the same change. This is an intentional unreleased-format break with no compatibility version.

## CI fast lane

Keep the PR workflow triggered for every update. A repository-local validation-lane action fails closed unless it can establish successful full validation for the preceding revision against the unchanged PR base. Full jobs run for mixed, uncertain, or non-PR changes; a metadata job runs `uv run --frozen specle validate .` only for eligible updates. An always-running `Verify` aggregation job checks the applicable path, preserving the required check name. Pushes to `main` always take the full suite. Validate the action with `act` and observed PR runs rather than recurring workflow tests.

## Failure handling

- External feedback, CI, or merge eligibility blocks auto-merge but leaves the current phase resumable.
- A missing push, PR, identity, or auto-merge step is retried only by explicit completion resumption.
- Premature original-PR merge selects recovery; archival work is never silently pushed to an already merged branch.
- Merge conflicts, wrong branch, or rejected push stop with durable record and selector retained.

## Test strategy

- Cover lifecycle metadata for direct, original-PR, and recovery delivery phases; archives never enter feedback workflows.
- Cover direct delivery without PR completion evidence and schema rejection of completion commit fields.
- Validate migration of every historical completion commit field.
- Exercise fail-closed CI classification with `act`, then confirm the implementation and archive-only PR updates choose their expected lanes; retain unconditional full main coverage.
- Run complete project quality gates and installed/blueprint validation.
