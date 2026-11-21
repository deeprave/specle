# Summary: Versioned JSON contracts

## Outcome

Specle now publishes and validates versioned JSON Schema contracts for its shared agent-managed records. Runtime context, current issue selection, and the generated skill index use the initial `1.0` contracts; future spike findings and tracker links are created with their corresponding contract markers.

## What changed

- Added packaged Draft 2020-12 schemas for runtime context, current issue selection, findings, tracker links, the skill index, and shared definitions.
- Added a resource-safe schema registry, instance validation, and `specle schemas export <destination>` for portable schema resources.
- Added `$schema` markers to current runtime records and generated skill indexes.
- Updated source blueprints and active guidance to create versioned contract instances.
- Added strict runtime contract ownership checks, canonical tracker-link URL constraints, and offline export registry mapping.

## Evidence

Local verification passed with 63 tests, Ruff checks and formatting, Ty, `specle validate .`, and `git diff --check`. The packaged wheel was inspected to confirm schema resources are distributed. PR #7 was locally reviewed, triaged, updated for accepted feedback, passed its required checks, and merged.

## Key decisions and limits

The `1.0` contracts are the first supported baseline. Specle deliberately does not provide runtime compatibility for unversioned predecessor records because there is no released predecessor or update workflow to migrate. Concurrency, symlink, and interruption hardening for user-selected local export destinations remain out of scope.

## Recommendation and follow-up

Use the packaged registry or exported `registry.json` mapping when validating schemas outside the package. Define migration behaviour only when a released update workflow creates a real compatibility need.

## Copy-ready update

Added versioned JSON Schema contracts to Specle, including packaged validation resources, runtime and skill-index markers, portable export support, and updated agent guidance. The feature was verified locally and merged through PR #7.
