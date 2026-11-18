# Requirements: Specle CLI initialisation

## Introduction

Specle is a suite of reusable skills that may be installed locally for a project, for a user, or eventually through other client mechanisms. This first target-oriented CLI operation must initialise the complete shared distribution at an explicit target without taking ownership of project-specific guidance or runtime state.

## Glossary

- **Target directory**: the positional directory supplied to the CLI command.
- **Distribution-managed content**: the reusable Specle skill and steering inventory.
- **Project-owned content**: `.agents/project/` and `.specle/` in an individual project.
- **Skill index**: the generated machine-readable inventory of installed Specle skills.
- **Force**: explicit authorisation to replace existing distribution-managed destinations.

## Requirements

### Requirement 1: Initialise a target installation

**User Story:** As a developer, I want to initialise Specle for a chosen target directory, so that its shared skills are available without manually copying blueprints.

#### Acceptance Criteria

1. THE CLI SHALL provide `specle init <target-directory>`.
2. THE command SHALL install the complete distribution-managed skill and steering inventory into the target's `.agents/` directory.
3. IF the target directory is the user's home directory, THEN the command SHALL install the shared inventory at `~/.agents/`.
4. THE command SHALL preserve any existing project-owned `.agents/project/` content and `.specle/` runtime workspace.
5. THE target directory SHALL be a required positional parameter; the CLI SHALL not infer the current directory as a target.

### Requirement 2: Preserve local and project ownership boundaries

**User Story:** As a developer, I want a user-level installation to coexist with each project's own guidance and runtime state.

#### Acceptance Criteria

1. A user-level installation at `~/.agents/` SHALL contain only shared distribution-managed content.
2. Each project SHALL continue to own its own `.agents/project/` and `.specle/` directories.
3. THE CLI SHALL not infer that a user-level installation owns or replaces project-owned content.

### Requirement 3: Generate an installed skill index during initialisation

**User Story:** As a developer, I want each Specle installation to provide a current structured inventory, so that the `specle` skill and future clients can discover installed skills without filesystem scanning.

#### Acceptance Criteria

1. AFTER a successful initialisation, THE CLI SHALL generate `<skills-location>/specle/index.json` using reusable index-building code.
2. THE index SHALL contain only installed skills carrying `specle_group`, organised in an ordered group list.
3. EACH indexed skill SHALL include its name, group, concise description, detailed usage guidance, and resource location or identifier.
4. A failed initialisation SHALL leave the previous index unchanged.
5. THE index SHALL be a generated packaged skill resource, not project-owned guidance.

### Requirement 4: Protect existing distribution-managed content

**User Story:** As a developer, I want initialisation to stop before overwriting an existing installation unless I explicitly authorise it, so that a target is never changed accidentally.

#### Acceptance Criteria

1. THE `init` command SHALL accept `--force`.
2. WITHOUT `--force`, THE CLI SHALL preflight every distribution-managed destination, including skills, steering, and index, and abort before making any change if any destination already exists.
3. WITH `--force`, THE CLI SHALL replace only distribution-managed content and SHALL preserve `.agents/project/` and `.specle/`.
4. FOR each replacement, THE CLI SHALL create a temporary sibling, remove the existing destination only after temporary creation succeeds, then rename the temporary item into place.
5. IF a forced replacement fails before initialisation completes, THEN the CLI SHALL remove every managed destination created by that attempt before restoring prior managed destinations.

## Non-Functional Requirements

- The CLI must remain lightweight and Python-based, using `uv`/`uvx` for management and execution.
- The initialisation operation must work without a project-specific framework, tracker, or hosting service.
- Target selection and file writes must be explicit and must not modify unrelated directories.

## Deferred work

This change does not provide `update` or `index` subcommands. A later update change will refresh an installation, and a later index change will expose the shared index-building code without installing first. It does not create a shell launcher; launcher behaviour requires separate design. It also does not define client-specific agent directories, linking or symlinking project skills to `~/.agents/`, integrity checks, status/change reporting, or root `AGENTS.md` management.

## Open design questions

- How future clients consume user-level skills or project-local skills.
