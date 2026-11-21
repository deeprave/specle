# Requirements: add online install

## Introduction

Specle can currently be installed through its Python CLI, but a new user needs to arrange `uvx` first. Provide small platform-native entrypoints that can be streamed to the appropriate shell and delegate the actual installation to `uvx specle init`.

## Glossary

- **Online installer:** a repository-distributed `install.sh` or `install.ps1` script executed through its platform-native shell from a remote stream or local checkout.
- **Target directory:** the explicit existing directory that receives the `.agents/` distribution through `specle init`.
- **Bootstrapped uvx:** an architecture-appropriate `uvx` executable downloaded temporarily from Astral when no usable `uvx` is on `PATH`.

## Requirements

### Requirement 1: Provide platform-native pipeable installers

**User Story:** As a developer without a local Specle checkout, I want to pipe the appropriate platform-native script to my shell so I can initialise Specle in a chosen directory.

#### Acceptance Criteria

1. The repository SHALL provide an executable `install.sh` Bash script for macOS and Linux.
2. The repository SHALL provide an `install.ps1` PowerShell script for native Windows.
3. The Bash script SHALL support standard-input execution, including `curl -fsSL <published-script-url> | bash -s -- <target-directory>`.
4. The PowerShell script SHALL support standard-input execution through PowerShell's documented remote-script invocation form, with an explicit target-directory argument.
5. Each script SHALL require exactly one explicit target-directory argument and SHALL fail with concise usage guidance when it is missing or invalid.
6. Neither script SHALL infer the current directory as the installation target.
7. Each script SHALL pass the supplied target directory unchanged to `uvx specle init`.

### Requirement 2: Use an existing uvx when available

**User Story:** As a developer with uv already installed, I want the installer to reuse my `uvx` command rather than download another copy.

#### Acceptance Criteria

1. IF a usable native `uvx` command is available on `PATH`, THEN the applicable script SHALL invoke that command to run `specle init`.
2. Each script SHALL report the command it is using without verbose logging.
3. Each script SHALL propagate the delegated command's non-zero exit status.

### Requirement 3: Bootstrap uvx only when necessary

**User Story:** As a developer without uvx, I want the platform-native installer to obtain the appropriate official executable temporarily and continue the installation.

#### Acceptance Criteria

1. IF `uvx` is unavailable, THEN the applicable script SHALL invoke Astral's official installer in a newly created temporary installation directory.
2. The Bash script SHALL use Astral's supported macOS/Linux installer path; the PowerShell script SHALL use Astral's supported Windows installer path.
3. Each script SHALL invoke the resulting temporary `uvx` executable and remove the temporary directory on success, failure, or interruption.
4. The bootstrap path SHALL not install uv globally, modify shell startup files, or permanently alter `PATH`.
5. Platform and architecture selection SHALL remain the responsibility of Astral's official installer rather than a Specle-maintained archive mapping.

### Requirement 4: Keep installation behaviour delegated to Specle

**User Story:** As a Specle maintainer, I want the shell script to stay small and let the versioned Python package own installation semantics.

#### Acceptance Criteria

1. The script SHALL invoke the published Specle package through `uvx specle init <target-directory>`.
2. The script SHALL not copy skills, construct an index, or duplicate CLI installation preflight, replacement, or policy logic.
3. The script SHALL preserve `specle init` output and actionable failures for the user.

## Non-Functional Requirements

- `install.sh` is Bash, not a portable-POSIX-shell compatibility layer; `install.ps1` is PowerShell for native Windows.
- Each installer must be safe for non-interactive use and must not prompt for input.
- It must use concise console output and no persistent logging.
- The implementation must use documented official Astral installer endpoints rather than an unverified third party or a Specle-maintained archive matrix.
- This change is independent of the queued CLI update and manifest changes. It must not rely on either feature.
