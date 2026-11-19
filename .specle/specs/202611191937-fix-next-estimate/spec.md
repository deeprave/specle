# Bugfix: preserve the activation boundary for queued planning

## Bug description

Queued normal changes created before the activation workflow retain `next: "estimate"`. In decision-gated mode, explicitly estimating one can therefore appear to authorise automatic planning before activation. The current lifecycle guidance also does not consistently distinguish explicit queued planning from active progression.

## Expected behaviour

`activate <spec-name>` is the only operation that makes a normal change current and starts automatic progression. It deterministically ensures an estimate, design, and task plan in that order, invoking the first missing stage; only a change with all three planning artifacts may proceed to build. Explicit `estimate`, `design`, and `tasks` calls may refine a queued normal change without activating it, but must stop after their requested planning operation. Tasks require a design.

## Actual behaviour

Queued records direct users to estimate, and continuation guidance can auto-chain a named queued estimate into subsequent planning despite the change not being activated.

## Root cause and fix approach

The activation boundary was added without migrating queued normal records or distinguishing explicit queued planning from active decision-gated continuation. Update lifecycle and skill guidance, migrate existing queued normal records to `next: "activate"`, and ensure activation fills the ordered estimate, design, and tasks preparation chain before build.

## Regression evidence

Inspect the migrated queued records and source/active skills to confirm that unactivated normal changes direct to `activate`, named planning stops after its requested stage, and only activation begins automatic progression.
