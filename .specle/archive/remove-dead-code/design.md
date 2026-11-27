# Design: Remove dead code

## Overview

This is a subtraction-first cleanup. The command-line application already composes directly from `scan_managed_inventory`, `compare_managed_inventories`, `read_runtime_snapshot`, `validate_runtime_records`, `build_skill_index`, and the schema operations. The Vulture-reported helpers sit outside that composition.

The implementation will remove each reported function unless inspection finds a current, concrete supported use beyond its direct unit test. A supporting test that only imports and invokes the helper will be removed or replaced with coverage of the real consumer. No public Python API is introduced.

## Architecture

```text
specle CLI
  -> inventory scanning / comparison / installation
  -> runtime snapshot and runtime-record validation
  -> schema validation

Vulture (pre-commit, complete tree scan)
  -> src + tests + optional explicit whitelist
  -> fail on unapproved unused code
```

The cleanup affects the unused wrappers and isolated helper implementations in `change_state.py`, `inventory.py`, `lifecycle.py`, `schema_registry.py`, and `sidecars.py`. The command paths remain unchanged; their existing integration tests provide the retained behavioural boundary.

## Retention and whitelist decision

For every reported symbol, inspect all source, test, documentation, packaging, and command-line references. Retain it only if there is a present, specific supported use that static analysis cannot observe.

If such an exception exists, add `vulture_whitelist.py` at the repository root (or another clearly documented repository-level location), reference it in the Vulture hook command, and place an explanatory comment beside each explicit symbol reference. The whitelist is not a future-use registry and must not suppress a name because it is unit-tested. If no exception exists, do not create the file.

## Pre-commit integration

Keep Vulture as a pinned remote pre-commit hook and keep `pass_filenames: false` so it scans the full trees. Change its confidence threshold from the initial 100% setting to the threshold that emits the reported 60% unused-function findings. The hook invocation includes the whitelist only when it exists. Vulture remains absent from `pyproject.toml`, the lockfile, and CI.

## Error handling

No new runtime error path is added. Existing command-line errors and validation diagnostics remain the authoritative behaviour. If the Vulture configuration or whitelist is invalid, the pre-commit hook fails locally with its normal diagnostic.

## API and data

No new runtime API, schema, record, or command option is added. Removing unsupported module-level functions intentionally narrows the uncommitted, undocumented internal surface.

## Test strategy

1. Start by identifying direct helper-only tests, then preserve or add behavioural coverage at the corresponding CLI or actual internal consumer boundary before deletion.
2. Verify the removal by running Vulture at the configured confidence threshold over `src` and `tests`; it must report no unapproved production functions.
3. When a whitelist exists, verify that it is loaded and that its comments state each concrete retention rationale.
4. Run the full pre-commit suite on a feature branch, plus `uv run --frozen pytest`, `uv run --frozen ruff check .`, `uv run --frozen ruff format --check .`, `uv run --frozen ty check`, and `uv run --frozen specle validate --verbose .`.
