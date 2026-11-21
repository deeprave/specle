# Summary: Restructure Specle spec state

## Outcome

Specle now keeps durable lifecycle and delivery evidence with each specification instead of a shared runtime context. Worktree selection is local, active specs are discoverable independently, and completed specs can be archived without unrelated state churn.

## What changed

- Added versioned per-spec `status.json` records and stable-name active/archive discovery.
- Retired durable shared context and current-issue records in favour of ignored local `current-spec` selection.
- Split Specle-owned package policy into `.agents/policies/`; `.agents/steering/` is now project-owned and installer-safe.
- Updated lifecycle skills for selection, spikes, summary generation, archive finalisation, and duplicate-name blocking.
- Added the independent `add-specle-reconcile` specification for later Git-aware duplicate-state recovery.

## Evidence

The implementation passed 65 tests, Ruff checks and formatting, Ty type checking, Specle validation, and local review before PR #8 merged.

## Key decisions and limits

Completion finalisation is deliberately delivered in a separate archive-only pull request after the implementation PR merges. Same-worktree concurrent workflow coordination and hostile local checkout hardening remain outside the current model.

## Recommendation and follow-up

Merge the completion pull request to archive this specification. Implement `add-specle-reconcile` later to provide explicit diagnosis and recovery when Git produces duplicate active/archive identities.

## Copy-ready update

Restructured Specle state so each specification owns durable lifecycle and delivery evidence, local worktree selection no longer creates tracked-state churn, and package policy is safely separated from project-owned steering.
