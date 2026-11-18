# Requirements: Specle CLI initialisation and updates

## Introduction

Specle is a suite of reusable skills that may be installed locally for a project, for a user, or eventually through other client mechanisms. The current CLI direction must support installing the complete Specle distribution into a chosen target without taking ownership of project-specific guidance or runtime state.

## Glossary

- **Target directory**: the positional directory supplied to the CLI command.
- **Distribution-managed content**: the reusable Specle skill and steering inventory.
- **Project-owned content**: `.agents/project/` and `.specle/` in an individual project.
- **Skill index**: the generated machine-readable inventory of installed Specle skills.

## Requirements

### Requirement 1: Initialise a target installation

**User Story:** As a developer, I want to initialise Specle for a chosen target directory, so that its shared skills are available without manually copying blueprints.

#### Acceptance Criteria

1. THE CLI SHALL provide `specle init <target-directory>`.
2. THE command SHALL install the complete distribution-managed skill and steering inventory into the target's `.agents/` directory.
3. IF the target directory is the user's home directory, THEN the command SHALL install the shared inventory at `~/.agents/`.
4. THE command SHALL preserve any existing project-owned `.agents/project/` content and `.specle/` runtime workspace.

### Requirement 2: Provide a shell launcher

**User Story:** As a developer, I want a simple local `specle` command, so that I can invoke the packaged CLI through `uvx`.

#### Acceptance Criteria

1. THE initialisation workflow SHALL create a Bash launcher named `specle`.
2. THE launcher SHALL invoke Specle through `uvx`.
3. THE launcher SHALL forward every received argument unchanged using `"$@"`.

### Requirement 3: Update a target installation

**User Story:** As a developer, I want to refresh a target's shared skills without disturbing its project-owned guidance.

#### Acceptance Criteria

1. THE CLI SHALL provide an update operation that accepts a target directory.
2. THE update operation SHALL refresh only distribution-managed content in that target's `.agents/` directory.
3. THE update operation SHALL preserve `.agents/project/` and `.specle/`.

### Requirement 4: Preserve local and project ownership boundaries

**User Story:** As a developer, I want a user-level installation to coexist with each project's own guidance and runtime state.

#### Acceptance Criteria

1. A user-level installation at `~/.agents/` SHALL contain only shared distribution-managed content.
2. Each project SHALL continue to own its own `.agents/project/` and `.specle/` directories.
3. THE CLI SHALL not infer that a user-level installation owns or replaces project-owned content.

### Requirement 5: Generate an installed skill index

**User Story:** As a developer, I want each Specle installation to provide a current structured inventory, so that the `specle` skill and future clients can discover installed skills without filesystem scanning.

#### Acceptance Criteria

1. AFTER a successful initialisation or update, THE CLI SHALL atomically generate `<skills-location>/specle/index.json`.
2. THE CLI SHALL provide `specle index <target-directory>` to create or refresh that target's installed skill index without changing installed skills or project-owned guidance.
3. THE index SHALL contain only installed skills carrying `specle_group`, organised in an ordered group list.
4. EACH indexed skill SHALL include its name, group, concise description, detailed usage guidance, and resource location or identifier.
5. A failed initialisation, update, or index operation SHALL leave the previous index unchanged.
6. THE index SHALL be a generated packaged skill resource, not project-owned guidance.

## Non-Functional Requirements

- The CLI must remain lightweight and Python-based, using `uv`/`uvx` for management and execution.
- The initialisation and update operations must work without a project-specific framework, tracker, or hosting service.
- Target selection and file writes must be explicit and must not modify unrelated directories.

## Deferred work

This change does not define client-specific agent directories, linking or symlinking project skills to `~/.agents/`, integrity checks, status/change reporting, or root `AGENTS.md` management. Those capabilities require separate discussion and specifications.

## Open design questions

- Where the generated launcher should be placed and how that location becomes available on `PATH`.
- The exact distribution contents installed alongside skills, including whether the portable `.agents/AGENTS.md` entry point is included.
- How future clients consume user-level skills or project-local skills.
