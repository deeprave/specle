# Specle CLI initialisation and updates

## Problem

The current individual-skill installation concept does not reflect Specle's intended use as a complete reusable skill suite that can be installed for a target directory or a user.

## Goal

Provide target-oriented `init` and update operations that install or refresh the shared Specle distribution while preserving project-owned `.agents/project/` guidance and `.specle/` runtime state.

## Behaviour

- `specle init <target-directory>` installs the complete shared skill and steering inventory into that target's `.agents/` directory.
- A generated Bash `specle` launcher invokes the packaged CLI through `uvx` and forwards `"$@"` unchanged.
- Update refreshes only distribution-managed target content.
- Initialisation and update atomically generate `skills/specle/index.json`, which lists installed marked skills with their groups, descriptions, usage guidance, and resource identifiers.
- `specle index <target-directory>` creates or refreshes that resource without changing skills or project-owned guidance.
- A user-level `~/.agents/` installation coexists with project-owned guidance and runtime state.

## Constraints

Client integrations, symlinks, integrity checks, status reporting, and root `AGENTS.md` management are separate future changes. Launcher placement and the exact non-skill distribution contents remain design decisions.

## Verification

Test target initialisation, protected project content, target updates, user-home installation, and launcher argument forwarding.
