# Requirements: versioned JSON contracts

## Introduction

Specle uses JSON for agent-managed state and for information crossing skill and external-system boundaries. These records currently have documented shapes but no explicit contract identity or version. Formal JSON contracts will make hand-offs between skills, migrations, validation, and external integrations safer.

## Glossary

- **JSON contract**: a named, versioned definition of a JSON record's purpose, fields, and compatibility rules.
- **Contract instance**: a JSON file governed by a JSON contract.
- **Schema version**: the version identifier embedded in or otherwise unambiguously associated with a contract instance.
- **External boundary**: data exchanged with a source or destination system outside Specle.

## Requirements

### Requirement 1: Identify agent-managed JSON contracts

**User Story:** As a developer, I want every operational JSON record identified by a stable contract, so that skills can safely exchange and evolve data.

#### Acceptance Criteria

1. THE project SHALL define named contracts for every agent-managed JSON file that is read or written by more than one skill or crosses an external boundary.
2. THE initial contract inventory SHALL include current-issue state, runtime context, spike findings, tracker links, and the generated Specle skill index.
3. THE project SHALL document each contract's purpose, owning skills, storage location, and canonical field shape.

### Requirement 2: Version contract instances

**User Story:** As a developer, I want JSON records to declare their contract version, so that readers can distinguish compatible records from legacy or unsupported forms.

#### Acceptance Criteria

1. THE project SHALL define a consistent mechanism for a contract instance to identify its contract name and schema version.
2. NEW contract instances SHALL use that mechanism.
3. Readers SHALL recognise the supported versions for every contract they consume and provide an actionable error for an unsupported version.

### Requirement 3: Evolve published contracts deliberately

**User Story:** As a developer, I want future contract changes to be deliberate and safe after Specle publishes stable JSON contracts.

#### Acceptance Criteria

1. THE first implementation SHALL establish the baseline supported version for each contract and SHALL not provide runtime compatibility for pre-contract unversioned records.
2. THE project SHALL define how a published contract evolves compatibly and when an explicit migration is required.
3. A migration for a published contract SHALL preserve fields outside its declared transformation unless the governing contract explicitly permits their removal.

### Requirement 4: Make external links safe and portable

**User Story:** As a developer, I want external source and destination references to be interpreted consistently across skills and connectors.

#### Acceptance Criteria

1. THE tracker-links contract SHALL model multiple source links and an optional single destination link.
2. THE contract SHALL preserve external system, item kind, identifier, and canonical URL without inventing replacement identifiers.
3. Contract documentation SHALL distinguish Specle-owned fields from data owned by an external system.

### Requirement 5: Distribute a schema registry

**User Story:** As a package consumer, I want Specle's published schemas available through a package-owned registry, so that validation can load them consistently from a source checkout, an installed wheel, or `uvx`.

#### Acceptance Criteria

1. THE project SHALL package its machine-readable JSON Schema resources with the `specle` distribution.
2. EACH published schema SHALL have a stable package-controlled identifier, and shared schema fragments SHALL resolve through documented internal `$ref` values.
3. THE package SHALL expose a public resource-safe schema loader and registry interface without assuming a source-tree filesystem path.
4. THE interface SHALL provide actionable errors for an unknown schema or an unavailable schema resource.
5. Tests SHALL load packaged schemas and resolve at least one internal shared-schema reference.

## Non-Functional Requirements

- Contract documentation remains readable in Markdown, while contract instances remain JSON.
- The design must remain independent of a particular agent client or tracker.
- Contract checks and migrations must not modify unrelated project-owned Markdown guidance.
- The implementation may update this repository's existing experimental JSON records atomically, but it need not support them as a runtime input format.

## Deferred decisions

- The exact identifier syntax and version representation.
- CLI commands for validation or migration.
