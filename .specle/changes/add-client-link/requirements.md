# Requirements: add client link

## Introduction

Specle installs and manages skills in `.agents/skills`, but AI clients do not consistently discover that location. Users need an explicit command that links the managed inventory into one or more supported client skill locations without overwriting client-owned configuration.

## Glossary

- **Client:** a named AI development client with a researched, documented local skills location.
- **Client specification:** one client name supplied as an argument or as one entry in a comma-delimited argument.
- **Managed skill:** a skill recognised by the Specle inventory scan.
- **Correct link:** a symlink at a client skill path that resolves to the corresponding local `.agents/skills/<name>` path.

## Requirements

### Requirement 1: Provide an explicit link command

**User Story:** As a Specle user, I want to expose installed managed skills to selected AI clients, so each client can discover the same local inventory.

#### Acceptance Criteria

1. `specle link [--dir <directory>] CLIENT [CLIENT ...]` SHALL require at least one client specification.
2. A client specification MAY contain comma-delimited client names; the command SHALL normalise and deduplicate all requested names.
3. `--dir` SHALL select the project directory containing `.agents`; when omitted, the command SHALL use the current directory as the explicit local-project default.
4. The command SHALL scan the target deployment's managed inventory and only link managed skills.
5. The command SHALL reject unknown client names with a clear list of supported clients.

### Requirement 2: Maintain researched client specifications

**User Story:** As a user, I want client names to resolve to reliable locations, so links are created only where each supported client expects skills.

#### Acceptance Criteria

1. The package SHALL define a researched client specification for each supported client, including Claude Code/Desktop, Codex, Pi, Antigravity, Cursor, Cursor Agent, and any other clients confirmed during implementation research.
2. Each specification SHALL document its skills directory, supported operating systems, and whether a direct `.agents/skills` directory link is recognised.
3. Unsupported platforms or clients that do not support filesystem links SHALL produce a clear warning and make no replacement or copy by default.

### Requirement 3: Create safe individual skill links

**User Story:** As a user, I want links created without replacing existing client content, so Specle does not damage my configuration.

#### Acceptance Criteria

1. For each applicable client, the command SHALL create a relative symlink from the client skills directory for every managed skill to the corresponding `.agents/skills/<name>` directory.
2. If a destination skill path already exists as a correct link, the command SHALL skip it silently unless `--verbose` is supplied.
3. If a destination skill path already exists as an incorrect link, file, directory, or client-owned skill, the command SHALL warn and skip it without replacement.
4. The command SHALL never force, overwrite, delete, or copy a client skill path.
5. On platforms without supported symlink creation, the command SHALL warn and skip affected links; it SHALL not silently copy managed skills.

### Requirement 4: Detect whole-directory links

**User Story:** As a user, I do not want redundant client links when the client already resolves skills through `.agents/skills`.

#### Acceptance Criteria

1. Before creating individual links, the command SHALL detect whether the client skills directory itself resolves to the target `.agents/skills` directory.
2. If so, it SHALL skip that client because individual links would have no effect.
3. The command SHALL also detect an equivalent client directory symlink arrangement that resolves through `.agents/skills` and skip it.

### Requirement 5: Provide useful reporting

**User Story:** As a user, I want concise feedback about linking outcomes, so I can understand what changed and what needs attention.

#### Acceptance Criteria

1. Warnings SHALL identify the client, skill path, and reason the link was skipped.
2. With `--verbose`, each created link and each already-correct skipped link SHALL report what was linked or skipped and its destination.
3. Normal output SHALL remain concise and SHALL not report already-correct links.

## Non-Functional Requirements

- Client-location research must use current vendor documentation before a client is supported.
- The command must remain agent-client agnostic in its core inventory handling.
- This change does not add a launcher, copy-based fallback, or overwrite mode.
