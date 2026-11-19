# Requirements: adopt StrictYAML frontmatter

## Introduction

Specle's package-owned skills use YAML frontmatter as their machine-readable interface. The existing custom parser is deliberately limited but duplicates YAML parsing logic, accepts only selected representations, and cannot apply a schema. StrictYAML provides a safe restricted YAML subset and application-defined schema validation suited to this inventory.

## Glossary

- **Package-owned skill**: a skill supplied by Specle under `src/specle/blueprints/skills/` or its installed `.agents/skills/` copy.
- **Frontmatter schema**: the StrictYAML mapping definition for the current package-owned metadata fields.
- **Active inventory**: this repository's installed local `.agents/skills/` copy, kept synchronised with the blueprints.

## Requirements

### Requirement 1: Use StrictYAML for package-owned frontmatter

**User Story:** As a maintainer, I want one safe parser and schema for skill metadata, so that malformed or ambiguous frontmatter is diagnosed consistently.

#### Acceptance Criteria

1. THE project SHALL depend on StrictYAML for package-owned skill-frontmatter parsing.
2. THE implementation SHALL replace the custom frontmatter value parser with a StrictYAML parser and an explicit schema.
3. THE parser SHALL accept only the current fields `name`, `specle_group`, `description`, `usage`, and `requires`.
4. THE schema SHALL require non-empty scalar values for `name`, `specle_group`, `description`, and `usage`, and accept an optional sequence of skill-name scalars for `requires`; its absence means no dependencies.
5. THE implementation SHALL report malformed frontmatter, schema violations, and invalid skill names as actionable `SkillMetadataError` messages without a traceback.
6. THE parser SHALL not use PyYAML, `yaml.load`, or an unsafe loader.

### Requirement 2: Migrate the managed inventories

**User Story:** As a skill author, I want package-owned metadata to use a consistent readable representation, so that its structure is easy to review and safely parse.

#### Acceptance Criteria

1. EACH blueprint skill SHALL conform to the StrictYAML frontmatter schema.
2. EACH active local `.agents/skills/` Specle skill SHALL match its blueprint metadata and conform to the same schema.
3. A skill with dependencies SHALL express `requires` as a block sequence. A skill with no dependencies SHALL omit `requires`; the parser SHALL treat it as an empty dependency set.
4. THE migration SHALL preserve every current skill name, group, description, usage, and direct dependency.
5. THE migration SHALL not change the body instructions, lifecycle policy, or non-Specle skills.

### Requirement 3: Preserve inventory behaviour

**User Story:** As an installer and user of the `specle` skill, I want parser hardening without changing the existing inventory contract.

#### Acceptance Criteria

1. THE installer SHALL continue to validate direct `requires` dependencies and generate the same index content from valid metadata.
2. THE installer SHALL continue to reject a package-owned skill whose declared name differs from its directory name.
3. THE Specle marker and grouping behaviour used to discover package-owned skills SHALL remain unchanged.
4. THE implementation SHALL not add lifecycle transition declarations or a `validate` CLI command.

## Non-Functional Requirements

- The schema and parser must be deterministic, local-only, and compatible with Python 3.13 through 3.15.
- Error messages must identify the affected `SKILL.md` file.
- This change is independent of document validation, auto-merge, and JSON schema versioning.
- `add-specle-validate` has an explicit dependency on this change because it will introduce lifecycle metadata and consume this schema-backed parser.
