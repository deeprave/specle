# Requirements: add `specle validate`

## Introduction

Specle skills describe lifecycle transitions in human-readable Markdown, while `.specle` stores the current and queued operational state as JSON. The current CLI has no deterministic way to check that those records are coherent or that the skills implementing the lifecycle provide a recovery path from every non-terminal state. A validator must derive its graph from declarations on those skills, rather than maintaining an independent lifecycle model or trying to infer formal semantics from prose.

## Glossary

- **Transition declaration**: structured frontmatter metadata on a lifecycle-owning Specle skill that describes a created, source, target, conditional, or terminal lifecycle state.
- **Target directory**: an explicit project root containing the `.agents/` and `.specle/` areas to validate.
- **Runtime record**: a current, queued, or recent record in `.specle/context.json`.
- **Dead end**: a reachable non-terminal status with no valid outgoing transition or no path to a terminal status.

## Requirements

### Requirement 1: Add an explicit validate command

**User Story:** As a maintainer, I want a read-only validation command for a selected project, so that I can identify corrupt or inconsistent Specle state before relying on it.

#### Acceptance Criteria

1. THE CLI SHALL provide `specle validate <target-directory>` with a required target-directory argument.
2. THE command SHALL not infer a target from the current working directory.
3. THE command SHALL perform no write, installation, replacement, staging, commit, or external operation.
4. THE command SHALL exit successfully only when all applicable checks pass, and SHALL exit non-zero with actionable diagnostics otherwise.

### Requirement 2: Declare lifecycle transitions in skills

**User Story:** As a maintainer, I want lifecycle-owning skills to declare their transitions in structured metadata, so that validation audits the workflow skills that agents actually use.

#### Acceptance Criteria

1. EACH lifecycle-owning Specle skill SHALL declare structured transition metadata in its frontmatter, including the statuses it creates, accepts, can produce, and marks terminal where applicable.
2. THE implementation SHALL extend the StrictYAML schema-backed parser from `adopt-strictyaml-frontmatter` with lifecycle declarations as a documented, constrained mapping and list format while preserving the existing frontmatter fields.
3. THE declarations SHALL support the current normal, abbreviated, and spike lifecycle flows, including delivery states and review-resolution exits.
4. THE validator SHALL derive its lifecycle graph from installed Specle skill declarations and confirm every non-terminal status has at least one valid outgoing transition and can reach a terminal status.
5. THE validator SHALL detect unreachable statuses, transitions to undeclared statuses, missing command owners, contradictory declarations, and non-terminal dead ends.
6. THE human-readable lifecycle steering SHALL remain explanatory policy; the validator SHALL not parse prose or Mermaid diagrams to construct its graph.
7. EACH lifecycle-owning skill SHALL explicitly instruct the agent to consult that skill's `lifecycle` frontmatter before applying or recording a lifecycle transition. The body instructions and declaration SHALL agree; neither may silently override the other.

### Requirement 3: Validate installed skill availability

**User Story:** As a maintainer, I want transition declarations checked against the installed skill inventory, so that recorded or declared next workflows cannot name unavailable skills.

#### Acceptance Criteria

1. THE command SHALL read the target's installed Specle skill inventory and identify skills by their declared frontmatter marker and name.
2. THE validator SHALL confirm every transition-declaring command and every recorded `next` workflow is available in that inventory, except explicitly declared terminal outcomes.
3. THE validator SHALL report missing, malformed, duplicate, or contradictory Specle skill metadata with the relevant file or record location.
4. THE validator SHALL ignore unrelated installed skills that do not carry the Specle marker.

### Requirement 4: Preserve direct skill dependencies

**User Story:** As a maintainer, I want lifecycle declarations kept distinct from direct skill dependencies, so that installation safety and workflow behaviour remain independently understandable.

#### Acceptance Criteria

1. THE existing `requires` frontmatter key SHALL remain the declaration of direct skill availability dependencies.
2. THE implementation SHALL not replace, infer, or rewrite `requires` from lifecycle transition metadata.
3. THE validator SHALL validate direct dependencies and lifecycle declarations separately and report failures in their respective terms.

### Requirement 5: Validate target runtime state

**User Story:** As an agent or maintainer, I want operational state checked against the skill-derived lifecycle graph, so that a target cannot remain silently inconsistent or unrecoverable.

#### Acceptance Criteria

1. THE command SHALL require and parse `.specle/current-issue.json` and `.specle/context.json` when validating active runtime state.
2. THE validator SHALL confirm that the active current-issue path and `current_spec` name and path align, and that referenced spec directories exist.
3. THE validator SHALL check current and queued records for a status declared by installed skills, compatible `kind`, permitted `next` command, and any required lifecycle evidence applicable to their state.
4. THE validator SHALL report malformed JSON and missing required runtime inputs without a traceback.
5. THE validator SHALL preserve unknown future record fields and shall not reject them merely because a future independent change may add them.

### Requirement 6: Preserve independent schema evolution

**User Story:** As a maintainer, I want validation now without prematurely committing to a versioned schema design, so that schema evolution remains an independently planned change.

#### Acceptance Criteria

1. THE change SHALL validate the current established context and current-issue shapes without adding schema-version fields, migration logic, or a compatibility layer.
2. THE change SHALL not depend on `versioned-json-schemas` or impose its anticipated record format.
3. A later schema-versioning change MAY extend the validator with version and migration checks without changing the command's read-only target semantics or the skill-derived transition graph.

## Non-Functional Requirements

- Validation must be deterministic, fast, and testable without an AI service or network access.
- Diagnostics must name the failing file, record, status, or command and suggest the recovery workflow when known.
- Skill transition metadata is a production interface for agents and validation; it must be concise, explicit, and visible alongside the human workflow instructions.
- A lifecycle declaration is not merely validator input: the owning skill must make its availability and authority explicit to the agent in its body instructions.
- The implementation SHALL use the StrictYAML parser and schema established by `adopt-strictyaml-frontmatter`; it SHALL not use PyYAML, `yaml.load`, or an unsafe loader for any frontmatter input.
- The CLI remains synchronous at the argument-parsing boundary with an asynchronous `main` entrypoint using AnyIO.
- This change depends only on `adopt-strictyaml-frontmatter`; it remains independent of document validation, auto-merge, JSON schema versioning, and all other queued work.
