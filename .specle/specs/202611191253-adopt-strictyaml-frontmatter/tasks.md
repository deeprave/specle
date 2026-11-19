# Tasks: adopt StrictYAML frontmatter

- [x] 1. Add the StrictYAML runtime dependency and define parser behaviour tests in `tests/test_inventory_metadata.py`.
  - [x] 1.1 Cover block-list dependencies, omitted `requires`, malformed YAML, unknown fields, invalid shapes, and invalid skill names with path-specific `SkillMetadataError` expectations.
  - [x] 1.2 Add StrictYAML through `uv` and update the lockfile.
- [x] 2. Replace the bespoke frontmatter value parser in `src/specle/inventory.py` with the explicit StrictYAML schema.
  - [x] 2.1 Retain delimiter handling and normalise absent `requires` to an empty tuple.
  - [x] 2.2 Translate StrictYAML parse and schema errors into concise, path-bearing `SkillMetadataError` messages while retaining dependency and directory-name validation.
- [x] 3. Migrate the managed skill inventories and prove their metadata remains aligned.
  - [x] 3.1 Add or update metadata-parity coverage for every package-owned blueprint and its active Specle counterpart.
  - [x] 3.2 Convert dependent `requires` values to block sequences, omit the key for independent skills, copy the matching frontmatter into `.agents/skills/`, and regenerate the installed Specle index.
- [x] 4. Address accepted PR #5 compatibility, parity, and documentation feedback.
  - [x] 4.1 Add focused regression coverage for marker detection with legacy flow-style metadata and for complete marked-inventory parity, without expanding the deferred directory-removal fixture.
  - [x] 4.2 Detect obsolete managed-skill markers by frontmatter line, update `SCHEMA.md` to document supported `requires` syntax, and strengthen the parity check.
