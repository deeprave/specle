# Tasks: support blueprint validate

- [x] 1. Add failing CLI mode and blueprint-validation tests.
  - [x] 1.1 Cover `validate --blueprint`, installed-target mode, and rejected missing or combined mode arguments in `tests/test_main.py`.
  - [x] 1.2 Cover blueprint metadata, generated-index, and lifecycle validation without an installed target.

- [x] 2. Add failing shared-inventory and drift tests.
  - [x] 2.1 Cover equivalent package and installed inventory records, including parsed metadata and nested-resource checksums.
  - [x] 2.2 Cover missing, modified, marker-stripped, and unexpected managed skills or resources; confirm unmarked user skills remain outside comparison.

- [x] 3. Build one shared inventory scanner and drift comparison.
  - [x] 3.1 Scan either skills root into stable managed-skill records containing parsed metadata and resource checksums, excluding the generated installed index.
  - [x] 3.2 Compare installed and blueprint record collections and emit actionable missing, unexpected, or checksum-drift diagnostics without modifying either root.

- [x] 4. Rewire both CLI modes through the shared scanner.
  - [x] 4.1 Keep mutual-exclusive invocation while using scanner records for blueprint metadata, dependency, index, lifecycle, and verbose reporting.
  - [x] 4.2 Use scanner records for installed metadata, dependency, index, lifecycle, comparison, runtime checks, and verbose reporting.

- [x] 5. Move source validation into the Test workflow.
  - [x] 5.1 Add a blueprint-validation job to `test.yml` and make Verify require its successful outcome.
  - [x] 5.2 Remove the installed-target lifecycle invocation from `document-validation.yml` without changing its prose checks. Inspect workflow configuration directly; do not add workflow tests.

- [x] 6. Run focused and complete validation.
  - [x] 6.1 Run the changed tests and `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and both `specle validate --blueprint --verbose` and installed-target validation.

- [x] 7. Consolidate inventory inspection.
  - [x] 7.1 Make one inventory operation own traversal, metadata parsing, dependency validation, resource checksums, and lifecycle analysis.
  - [x] 7.2 Rewire init, validation, index generation, and compatibility helpers to consume its result rather than rediscovering skills.
  - [x] 7.3 Preserve a reusable lifecycle graph in the inventory result for later rendering or planning commands, then re-run complete verification and review.
