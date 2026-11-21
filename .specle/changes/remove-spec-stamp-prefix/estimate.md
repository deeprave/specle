# Estimate: remove spec stamp prefix

## T-shirt size

XL

## Breakdown

- New files: approximately 1–2 schema/test support files, depending on whether the renamed change-state schema is introduced as a new resource or replaces the current resource in place.
- Modified files: approximately 45–65 across runtime code, schema registry, blueprints, installed mirror, generated index, documentation, tests, active changes, and archived history.
- Renamed files and directories: 6 active change directories, 17 archived change directories, the active collection directory, the creation skill, and the change-state schema resource.
- Estimated tasks: 8–10, including a deliberate repository-wide reference inventory and final validation.
- Key risks: stale structured references inside archived review evidence; incorrectly deriving historical activation timestamps; missing a generated or installed-mirror reference; an incomplete rename leaving a mixed `spec`/`change` runtime contract.

## Confidence

Medium. The destination state is clear, but the repository-wide rename must distinguish work-item terminology from the retained product name `Specle` and literal `spec.md` document references.

## Recommendation

Keep this as one repository-wide, atomic source-layout change. Introduce the new `change` terminology and contracts directly with no compatibility aliases or external migration path. Perform a structured inventory first, then use automated validation and targeted assertions to prove that only intended `spec.md` and `Specle` references remain.

## Similar past work

- `202611192027-restructure-spec-state` moved lifecycle authority from shared state into per-change records and established ignored local selection.
- `202611172043-versioned-json-schemas` established packaged, validated JSON Schema resources.
- `202611211216-support-blueprint-validate` consolidated the blueprint and installed inventory validation paths.
