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

- [x] 8. Reconcile external-review corrections to shared inventory semantics.
  - [x] 8.1 Make the shared inventory result own package-completeness and top-level marker-owned policy analysis; remove standalone policy discovery.
  - [x] 8.2 Permit an empty installed managed inventory for comparison while retaining package completeness requirements and preserving user policy files during init.
  - [x] 8.3 Make both CLI validation modes report inspection failures consistently without tracebacks.
  - [x] 8.4 Add focused production-code coverage for the accepted behaviours, then run complete verification and review.

- [x] 9. Move package-completeness analysis into the inventory result.
  - [x] 9.1 Return completeness diagnostics from the shared scan and remove the standalone completeness helper.
  - [x] 9.2 Rewire init and blueprint validation to consume that result, with focused production-code coverage.
