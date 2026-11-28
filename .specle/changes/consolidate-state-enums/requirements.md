# Requirements: Consolidate state enums

## Why

Specle records each change's lifecycle status and kind as strings. The change-status JSON Schema currently accepts any non-empty status and any kebab-case kind, while skill-frontmatter parsing maintains separate tuples of supported lifecycle statuses and kinds and runtime lifecycle validation checks values against installed skill declarations. This divides value definitions and checking across layers: for example, a schema-valid arbitrary status can reach a change listing before lifecycle validation reports it.

Consolidate the definitions, validation, and conversion of change status and kind into string-valued enum classes. Make the versioned JSON contract agree with those supported values, while preserving the established wire representation and the ability to report invalid records clearly.

Specle also discovers its managed skills from packaged frontmatter and directory names, while installation and inventory code reference particular skill names and paths. A central enum of packaged Specle skill names will make those references coherent and make a future deliberate rename, such as adding a `specle-` prefix to avoid collisions, easier to coordinate.

## Scope and boundaries

- Covers the top-level change `status` and `kind` fields and the corresponding lifecycle and skill-frontmatter consumers.
- Covers an enum for all skills managed in the packaged Specle distribution and the relevant inventory, installation, update, and skill-name consumers. Packaged skill metadata, directory names, and references must remain consistent with it.
- Keep current skill names and installation paths unchanged. A prefix, a skill rename, and any associated migration are future possibilities, not requirements of this change. Preserve existing handling of unrelated skills and collisions.
- The current lifecycle status vocabulary is the set declared in the lifecycle policy. The documented initial kind vocabulary is `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`; lifecycle transitions may apply only to a subset of kinds.
- Tightening kind validation changes the currently documented behaviour that preserves unknown kebab-case kinds. Tightening status validation changes the current schema's acceptance of arbitrary non-empty statuses.
- Existing valid active and archived records retain their string values. Determine and document an appropriate schema compatibility and versioning approach before implementation; do not rewrite immutable archives merely to make the new implementation work.
- Delivery `event` values, their historical variants, and other JSON keys and nested status fields are out of scope.
- This change is independent of the in-flight changes-listing work. It must not impose a dependency on that change or assume it has been delivered.

## Requirements

### 1. Define authoritative string enums

**User story:** As a Specle maintainer, I want a single definition of each supported change status and kind so that all consumers validate and convert the same values.

1. THE implementation SHALL define a string-valued enum for change lifecycle statuses containing each currently supported lifecycle state.
2. THE implementation SHALL define a string-valued enum for change kinds containing the documented initial kinds: `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`.
3. EACH enum SHALL own the checking and conversion of its individual values, including rejecting unsupported values and converting supported strings to enum members and back to their durable string representation.
4. Lifecycle and skill-frontmatter consumers SHALL use these enum definitions instead of maintaining competing lists of supported status or kind strings.
5. Kind-specific lifecycle validity SHALL remain a separate semantic check from whether an individual status or kind is a recognised enum value.

### 2. Align durable contracts and validation

**User story:** As a user, I want invalid status and kind values detected consistently so that reports and validation do not treat arbitrary strings as valid change state.

1. THE change-status JSON Schema SHALL constrain top-level `status` and `kind` to the supported string enum values.
2. WHEN a change record contains an unsupported top-level `status` or `kind`, THE change-state validation path SHALL report an actionable invalid-contract diagnostic rather than treating the value as a supported state.
3. WHEN a record contains supported values, THE reader, lifecycle validation, reporting, and serialisation paths SHALL preserve their existing durable string values and applicable lifecycle semantics.
4. THE schema contract, Python enum values, and lifecycle metadata validation SHALL agree on the recognised individual values, without duplicating independent runtime value definitions.
5. THE change SHALL identify and address compatibility for current active and archived records and for exported versioned schemas; any necessary schema-version or migration decision SHALL be made explicitly in design.

### 3. Consolidate managed skill names

**User story:** As a Specle maintainer, I want the names of packaged managed skills represented centrally so that a future naming change can be coordinated across the distribution and its installation and update paths.

1. THE implementation SHALL define a string-valued enum containing every skill managed in the packaged Specle distribution, with values matching the current skill names.
2. THE implementation SHALL use that definition for packaged skill-name references in relevant runtime consumers, including inventory and installation and update operations, instead of maintaining competing hard-coded name definitions.
3. THE packaged inventory and enum SHALL agree on the managed skills and their names; an inconsistency SHALL be detectable with an actionable diagnostic.
4. THE design SHALL establish how the enum, packaged skill directories and frontmatter, skill dependencies and lifecycle references, and generated inventory or index data remain aligned as skills are added, removed, or deliberately renamed.
5. THE change SHALL retain existing skill names, installation paths, and behaviour for unrelated skills and name collisions; it SHALL NOT add a prefix or perform a naming migration.

### 4. Keep delivery and other JSON vocabulary unchanged

**User story:** As a maintainer, I want the JSON state portion of this refactor bounded to change status and kind so delivery-event semantics and specialised record formats remain independently manageable.

1. THE change SHALL NOT introduce an enum for delivery events or alter accepted or recorded delivery event values.
2. THE change SHALL NOT introduce enums for other JSON keys or specialised fields, including review and verification status fields.
3. THE change SHALL NOT activate or mutate another change as a side effect of validation or reporting.

## Verification direction

Exercise recognised and unrecognised status and kind values at the enum, schema, lifecycle, and CLI boundaries; verify the existing active and archived record corpus and the unchanged delivery-event behaviour. Verify packaged skill enum coverage and drift detection, and that inventory, installation, and update retain current names and preserve existing treatment of unrelated skills and collisions. Follow the project's documented quality gates.
