# Estimate: adopt StrictYAML frontmatter

## T-shirt size

M

## Breakdown

- New files: approximately 0–2, depending on whether the schema is kept with `inventory.py` or extracted for clarity.
- Modified files: approximately 50: package dependency/lock state, metadata parser and tests, plus every source and active Specle `SKILL.md` frontmatter block.
- Estimated tasks: 4–5 implementation slices.
- Key risks: mapping StrictYAML's error types into concise `SkillMetadataError` messages; preserving folded description/usage text; and keeping source/active frontmatter exactly aligned after migration.

## Confidence

High. The current parser is isolated in `src/specle/inventory.py`, existing metadata tests provide a clear baseline, and the schema intentionally covers only the five existing fields.

## Recommendation

Use `design`. Although the parser substitution is locally contained, the schema boundary, error contract, packaging, and inventory-wide migration need a short technical design before implementation.

## Similar past work

`specle-cli-init` established the inventory parser and installer behaviour. `add-decision-gated-progression` demonstrated the source-blueprint to active-inventory synchronisation pattern, including regenerated installed resources.
