# Bugfix: prevent assumed dependencies between changes

## Bug

Planning and implementation skills can treat a queued, future, or conceptually related change as a prerequisite without an explicit user decision or unavoidable implemented technical dependency.

## Expected behaviour

Changes remain independent by default. A dependency is recorded only when the user specifies it or an already-implemented technical interface makes it unavoidable. Future requirements, constraints, records, or functionality do not affect another change until that future change is implemented.

## Actual behaviour

The delivery-policy work was made dependent on the queued versioned-schema change even though the user had not made it a prerequisite. This added hidden constraints, blocked delivery, and muddied review and implementation.

## Reproduction

Create a future queued change describing a possible persistence format, then plan a separate delivery or workflow change. Existing skill guidance permits the latter to be blocked on the former based on anticipated design rather than an explicit dependency.

## Root cause and fix approach

The planning and implementation skills lack an explicit independence-default rule. Add it to `spec`, `estimate`, `design`, `tasks`, `revise`, and `implement`; add regression coverage that forbids inferred dependencies and premature future-change constraints.

## Relationship

This bugfix was raised because the active `202611180808-add-delivery-policy` change was procedurally blocked by the assumed future-schema dependency. It unblocks that change and is delivered with it, rather than as an independent delivery.

## Regression evidence

The focused blueprint-contract tests will assert the independence-default rule and reject language that makes ordering or anticipated future work a dependency.
