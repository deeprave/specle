# Estimate: versioned JSON contracts

## T-shirt size

L

## Breakdown

- New files: approximately 7 — packaged schemas, shared fragments, registry/loader module, and focused tests.
- Modified files: approximately 12 — runtime JSON records, JSON readers and writers, package configuration, relevant skills, and documentation.
- Estimated tasks: 9.
- Key risks: choosing stable schema identifiers and instance markers; packaging resources safely for both a source checkout and installed distribution; preserving `$ref` resolution without filesystem assumptions; updating every current consumer atomically; and keeping the export layout portable.

## Confidence

Medium. The existing `specle validate` work provides an inventory of live JSON consumers and an established package layout, but the contract marker, schema registry API, and export shape need detailed design before implementation.

## Recommendation

Continue through design. Establish baseline versions only: do not add compatibility parsing for the repository's present unversioned records. Include `specle schemas export <destination>` as the portable non-Python interface, with safe destination replacement semantics. This change has no dependency on queued work; in particular, it must not wait for state restructuring or document validation.

## Similar past work

- `add-specle-validate` introduced package-owned lifecycle validation and inventories the current JSON runtime and installed-skill resources.
- `adopt-strictyaml-frontmatter` introduced schema-validated package metadata and resource-safe parsing patterns.
