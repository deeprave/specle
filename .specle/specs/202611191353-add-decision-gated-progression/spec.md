# Add decision-gated progression

## Problem

Specle treats every lifecycle skill as a separate user interaction even when its next step is routine and successful. `implement` partially compensates by chaining planning and build, but stops before verification and review. This creates unnecessary hand-offs while still failing to make genuine human decisions explicit.

## Goal

Add an opt-in, project-owned decision-gated progression policy. In that mode, an agent continues successful local lifecycle stages until it reaches a genuine decision, failure, triage-decision summary, or delivery authorisation boundary.

## Behaviour

- Define portable `manual` and `decision-gated` progression modes in steering; missing policy remains manual.
- Add project `automation.md`, selected through onboarding and mapped in the project README.
- In decision-gated mode, automatically progress through successful estimate, design, tasks, build, verify, and review stages without skipping their instructions or state updates.
- Stop for material ambiguity, verification failure, review/triage decisions, external delivery authorisation, or another established human decision boundary.
- Start triage automatically after review findings, but after every item has a decision, persist and present the complete decision-and-route list, set `triaged`, and wait for explicit `resolve`.
- Remove the redundant `implement` skill and route planned abbreviated work directly to its owning `bugfix` or `refactor` skill.

## Boundaries

This policy controls continuation after a skill completes; it does not weaken verification, review, triage, delivery safeguards, or a skill's direct-invocation preconditions. It does not automatically commit, push, open a pull request, merge, or perform any other external write.

## Verification

Test both progression modes, each stop condition, review-to-triage behaviour, final triage-summary behaviour, abbreviated-work routing without `implement`, onboarding output, and installed-inventory/index removal of `implement`.
