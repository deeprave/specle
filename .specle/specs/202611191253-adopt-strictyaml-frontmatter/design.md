# Design: adopt StrictYAML frontmatter

## Overview

Replace the bespoke key/value frontmatter parser in `specle.inventory` with StrictYAML and one explicit schema for Specle-owned skill metadata. The schema remains deliberately limited to the five current metadata fields. This hardens input validation without adding lifecycle declarations or changing installation and index semantics.

Independent skills omit `requires`; dependent skills use an ordinary YAML block sequence. The parsed result normalises an omitted key to the existing empty dependency tuple.

## Architecture

```text
SKILL.md
  │
  ├─ extract delimited frontmatter text
  │
  ├─ StrictYAML load(schema)
  │    └─ mapping: name, specle_group, description, usage, optional requires
  │
  ├─ convert validated values to SkillMetadata
  │    └─ absent requires → ()
  │
  └─ existing discovery, dependency validation, installation, and index generation
```

The schema and conversion helper stay in `inventory.py` because only that module consumes the package-owned metadata. StrictYAML parsing exceptions and value-validation failures are caught at this boundary and re-raised as `SkillMetadataError` containing the source `SKILL.md` path and a concise reason.

Marker detection for stale installed directories is intentionally separate. It reads only the delimited frontmatter lines and recognises a top-level `specle_group:` line; it does not parse or validate the rest of that legacy file. This preserves forced-upgrade pruning without weakening the StrictYAML schema used for package-owned metadata.

## Metadata schema

The schema accepts only these keys:

- `name`, `specle_group`, `description`, and `usage`: required non-empty strings.
- `requires`: optional sequence of skill-name strings. Its absence represents no direct dependencies.

After schema loading, the existing skill-name regular expression validates `name` and every `requires` member. This retains the current public constraint while StrictYAML rejects duplicate keys, unsupported YAML features, malformed structures, and unknown metadata keys.

## Inventory migration

Update every source `src/specle/blueprints/skills/*/SKILL.md` frontmatter block, then copy the matching metadata to the managed local `.agents/skills/` inventory. Preserve each skill's body verbatim.

For dependent skills:

```yaml
requires:
  - verify
```

For independent skills, omit `requires` entirely. The active and source inventories must remain metadata-equivalent. Rebuild the installed Specle index after the migration.

## Error handling

- No opening or closing frontmatter delimiter: raise the existing path-specific `SkillMetadataError`.
- StrictYAML parse or schema failure: translate to path-specific `SkillMetadataError` without leaking a traceback through the CLI.
- Invalid skill name or invalid declared dependency name: raise the existing clear metadata error form.
- Dependency references remain checked by the existing distribution-level dependency validator.

## Test strategy

- Update valid metadata fixtures to use block-list dependencies and test that omitted `requires` becomes an empty tuple.
- Cover malformed YAML, an unknown key, a wrong value shape, and an invalid dependency name, asserting path-bearing `SkillMetadataError` output.
- Retain directory-name and direct-dependency validation coverage.
- Compare the complete source and marked-active inventories, including directory and declared names, while ignoring unmarked project-local skills.
- Cover marker detection for legacy flow-style frontmatter and forced obsolete-skill pruning.
- Keep `SCHEMA.md` aligned with the block-list and omitted-key convention.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check`.
