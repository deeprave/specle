# Estimate: add Specle manifest

## T-shirt size

L

## Breakdown

- New files: ~2–4 for the versioned manifest resource, its schema, and focused fixtures.
- Modified files: ~7–10 across shared inventory scanning, package metadata access, init staging, validation, CLI reporting, and tests.
- Estimated tasks: ~7 implementation and validation tasks.
- Key risks: defining a generation-history format that preserves released records while allowing the current development generation to be rebuilt deterministically; avoiding a checksum cycle; keeping manifest generation coupled to the shared inventory rather than a second filesystem traversal; and distinguishing installed manifest provenance from live managed-file drift.

## Confidence

High

## Recommendation

Continue through design. Keep the manifest package-owned and separate from the agent-facing skill index. Reuse the existing managed-inventory scan and transactional installation machinery, and specify clearly how a release-version record becomes immutable while the current development record is regenerated.

## Similar past work

- `specle-cli-init` established transactional installation of the managed skills and policies.
- `support-blueprint-validate` established shared blueprint and installed-inventory validation.
- `versioned-json-schemas` established packaged versioned JSON contracts and export-safe resource loading.
