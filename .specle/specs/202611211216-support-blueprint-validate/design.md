# Design: support blueprint validate

## Overview

Split validation into two explicit modes:

- `specle validate <target-directory>` remains the read-only installed-target validator and gains package-content drift detection.
- `specle validate --blueprint` validates the packaged `src/specle/blueprints/` inventory and lifecycle contract directly, without requiring or comparing an installed target.

Both modes call one inventory operation. It receives the distribution root: the package blueprint root or an installed target's `.agents/` root. It performs the sole managed-skill traversal for that root, returning stable managed-skill records with parsed metadata and checksums for every enclosed resource, together with dependency and lifecycle analysis.

## Architecture

```text
blueprint path ──────┐
                    ├─ inspect managed inventory ── validated inventory
installed .agents ──┘                                  │
                                                       ├─ skills and resource checksums
                                                       ├─ lifecycle graph and diagnostics
                                                       ├─ index model
                                                       └─ installed mode: compare with blueprint inventory

installed target
  ├─ generated index
  └─ runtime state
```

`inventory.py` owns the reusable inventory operation and lifecycle analysis. It discovers managed skills, parses each `SKILL.md` once, validates direct dependencies, recursively checksums every regular resource under that skill directory, derives the lifecycle graph and diagnostics, and represents all results as immutable inventory data. The installed `specle/index.json` resource is excluded because it is generated and remains validated by comparison with `build_skill_index`.

Blueprint mode resolves `packaged_distribution_root()` and passes it to the inventory operation. Installed mode passes `.agents/` to the same operation. Both mode paths consume its skills, lifecycle diagnostics, and generated index model. Installed mode additionally compares the two record collections by skill name and resource-relative path: an added or missing record/resource, or unequal checksum, is drift. An unmarked installed skill produces no inventory record and remains user-owned. A marker-stripped expected skill is reported as missing when the two record collections are compared.

The inventory result is intentionally reusable: the index is built from its skills; init/update/reconcile use its managed names and checksums to determine additions, replacements, and removals; and a later lifecycle rendering command can use its graph directly without a second parse or traversal. Compatibility helpers, where retained, delegate to this operation rather than discovering skills independently.

## API and output

`validate` accepts exactly one mode:

```text
specle validate <target-directory> [--verbose]
specle validate --blueprint [--verbose]
```

The parser accepts an optional target positional only to support blueprint mode, then rejects zero-mode and combined-mode invocation through the normal argparse error path. It never chooses the current directory implicitly.

Blueprint verbose output identifies blueprint mode and reports managed skills, resource checksum coverage, the generated-index model, and lifecycle summaries. Installed verbose output reports the same inventory summary for the installed root, followed by successful comparison with the blueprint inventory and its runtime summary.

## Error handling

- Invalid CLI mode combinations use argparse diagnostics and non-zero exit status.
- Missing, modified, or unexpected managed inventory records emit concise diagnostics naming the affected skill or resource; unequal checksums identify unsynchronised managed content and direct the user to update or validate with the matching package version.
- Unmarked user skills are ignored without parsing their full frontmatter.
- Blueprint mode never opens an installed target or reads runtime state.
- Both modes remain read-only.

## CI integration

Add a dedicated blueprint-validation job to `test.yml` that installs the existing environment and runs `uv run --frozen specle validate --blueprint --verbose`. Add that job to Verify's `needs` list and outcome guard.

Remove the lifecycle job from `document-validation.yml`; Markdownlint, CSpell, and Vale remain unchanged. Workflow configuration is inspected directly rather than covered by workflow-specific tests.

## Test strategy

- Extend CLI tests for each valid mode and rejected zero/combined mode.
- Add scanner tests proving package and installed roots produce the same record shape, including metadata and nested-resource checksums.
- Add comparison fixtures for identical, missing, modified, marker-stripped, and unexpected managed skills or resources; confirm unmarked skills are ignored.
- Add blueprint-mode tests for package metadata, generated-index model, and lifecycle failures without a target directory.
- Preserve existing generated-index and runtime validation tests.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and direct workflow inspection. Do not add tests for declarative workflow configuration.
