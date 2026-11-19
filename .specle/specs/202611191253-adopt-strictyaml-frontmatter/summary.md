# Summary: Adopt StrictYAML frontmatter

## Outcome

Specle now parses package-owned skill frontmatter with StrictYAML and an explicit metadata schema. The managed blueprint and active inventories use the same supported dependency representation, and forced upgrades can still remove obsolete skills carrying legacy metadata.

## What changed

- Added StrictYAML as a runtime dependency and replaced the bespoke frontmatter value parser.
- Defined the allowed metadata fields: `name`, `specle_group`, `description`, `usage`, and optional `requires`.
- Migrated package-owned skills to block-list dependencies and omitted `requires` when no dependency exists.
- Added parity coverage for the complete marked active inventory, including declared names, while leaving unmarked project-local skills alone.
- Kept obsolete-skill marker detection deliberately lexical within frontmatter so a forced installation can remove old managed directories even when their other metadata is no longer valid StrictYAML.
- Updated `SCHEMA.md` to document the supported dependency syntax.

## Evidence

- Project verification passed: pytest, Ruff check, Ruff format check, ty, and diff whitespace checks.
- The GitHub test matrix passed for Python 3.13, 3.14, and 3.15; GitGuardian and Sourcery also completed successfully.
- Local review approved the implementation. Three Sourcery findings were resolved in the follow-up commit; one test-fixture expansion was intentionally deferred.
- PR #5 merged to `main` as `fe898648f7e9e854113e997c061d0e11859c81ca`.

## Key decisions and limits

- StrictYAML validates current package-owned metadata only. The obsolete-directory marker check is not a metadata parser and therefore does not relax the package schema.
- Independent skills omit `requires`; empty flow-style lists are not supported.
- The deferred review suggestion would add extra fixture detail for directory removal; existing coverage already tests the relevant marker-recognition and pruning behaviour.

## Recommendation and follow-up

Use this schema-backed parser as the foundation for the separately planned lifecycle metadata and `specle validate` work. Do not add lifecycle declarations to this change.

## Copy-ready update

Specle now uses StrictYAML to validate package-owned skill frontmatter, with a documented block-list dependency format and parity checks between the blueprint and installed inventories. The installer also retains safe forced-upgrade cleanup for obsolete skills with legacy metadata. PR #5 has merged to main.
