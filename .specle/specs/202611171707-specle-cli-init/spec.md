# Specle CLI initialisation

## Problem

The current individual-skill installation concept does not reflect Specle's intended use as a complete reusable skill suite that can be explicitly initialised for a target directory or a user.

## Goal

Provide a target-oriented `init` operation that installs the shared Specle distribution while preserving project-owned `.agents/project/` guidance and `.specle/` runtime state.

## Behaviour

- `specle init <target-directory>` installs the complete shared skill and steering inventory into that target's `.agents/` directory.
- The target directory is required; initialisation never assumes the current directory.
- Initialisation implicitly builds `skills/specle/index.json` through shared index-generation code, which lists installed marked skills with their groups, descriptions, usage guidance, and resource identifiers.
- Without `--force`, a complete destination preflight aborts before any existing distribution-managed content is replaced. With `--force`, replacements use temporary siblings, deletion of the previous destination, and rename into place.
- A user-level `~/.agents/` installation coexists with project-owned guidance and runtime state.

## Constraints

Update and standalone index commands, shell launcher behaviour, client integrations, symlinks, integrity checks, status reporting, and root `AGENTS.md` management are separate future changes. This change distributes skills and steering only.

## Verification

Test required target selection, protected project content, user-home installation, force preflight and replacement behaviour, and implicit index generation.
