# Tasks: add Specle manifest

- [x] 1. Define text-manifest lines and package-version ownership.
  - [x] 1.1 Add focused failing production tests for `version:skill/<skill>/<path>:<checksum>` and `version:policies/<document>:<checksum>` output, stable ordering, and the package `__version__` source.
  - [x] 1.2 Add the package version export plus text-manifest line parsing and construction from one supplied `ManagedInventory`.

- [x] 2. Implement append-only release generation.
  - [x] 2.1 Add failing production tests for initial output creation, append of missing lines to a valid existing manifest, repeated-entry no-op behaviour, conflicting-checksum and duplicate-identity rejection, malformed-line rejection, and preservation of prior lines.
  - [x] 2.2 Implement manifest load, line validation, immutable `(version, path)` checks, and atomic append to an explicit output path without scanning the blueprint tree a second time.

- [x] 3. Expose the source-only manifest CLI command.
  - [x] 3.1 Add failing production tests for `specle manifest <output>`, required output selection, concise result rendering, and package-version retrieval through `importlib`.
  - [x] 3.2 Add the argparse command and AnyIO dispatch, wiring it to one packaged-inventory scan and the append-only text generator without touching `.agents/`.

- [x] 4. Add initial provenance and release documentation.
  - [x] 4.1 Generate the initial manifest under `src/specle/blueprints/` for the current package version and confirm it contains every managed skill and policy resource.
  - [x] 4.2 Add `docs/` guidance for release preparation, entry forms, append-only history, first appearance, retirement, and checksum-change queries.

- [x] 5. Verify the release-only boundary and complete checks.
  - [x] 5.1 Add production tests that init and installed-target validation do not copy, require, or consume a manifest.
  - [x] 5.2 Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, blueprint validation, installed-target validation, and pre-commit.
  - [x] 5.3 Correct the generated-index exclusion assertion so it rejects a manifest entry for `skills/specle/index.json`, then rerun the affected checks.
