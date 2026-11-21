# Summary: Delivery policy and completion workflow

## Outcome

Specle now distinguishes local approval from delivered work. Projects can select a portable delivery model and record their own delivery conventions, while the workflow represents locally approved, submitted, and fully delivered work separately.

## What changed

- Added portable delivery steering and project-owned delivery guidance, with onboarding questions for the applicable policy.
- Added the `approved` and `committed` lifecycle states, plus `commit` and `complete` skills for policy-led delivery.
- Made branch-and-pull-request completion safe: it requires the submitted branch, preserves local work in a recoverable stash when needed, merges or confirms the pull request, synchronises the delivery branch, and then records completion.
- Allowed submitted changes to receive named triage, resolution, verification, review, and redelivery without displacing unrelated active work.
- Added explicit relationships for bugfix and refactor sidecars delivered with their active change; unrelated abbreviated work is prepared for a separate worktree.
- Updated lifecycle and schema guidance to reflect the implemented delivery flow.

## Evidence

The recorded verification run passed `pytest`, `ruff check`, `ruff format --check`, `ty check`, and `git diff --check` on 18 November 2026. Local review passed with no remaining findings. Pull request [#2](https://github.com/deeprave/specle/pull/2) was merged to `main` on 18 November 2026 after its review findings were triaged and resolved or declined.

## Key decisions and limits

Delivery policy stays human-readable and project-owned. Specle supplies portable models rather than prescribing a Git host, tracker, branch convention, or agent authority. External writes remain subject to explicit user authorisation and the selected project policy.

## Recommendation and follow-up

Use the new delivery guidance when onboarding a project, then use `commit` after local approval and `complete` only once the project’s final delivery event is evidenced. The separate queued work on versioned JSON schemas remains independent from this delivery workflow.

## Copy-ready update

Added delivery-policy support to Specle: local review approval is now distinct from external delivery, with project-owned delivery guidance, `commit` and `complete` workflows, safe pull-request finalisation, and explicit handling for related sidecar bugfixes and refactors. The work was verified locally, reviewed, and merged through PR #2.
