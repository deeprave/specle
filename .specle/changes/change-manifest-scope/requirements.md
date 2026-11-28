# Requirements: Change manifest scope

## Problem

`specle manifest` is release-maintenance tooling for the Specle project itself, but it is currently registered in the ordinary CLI parser. This exposes a command that is irrelevant and potentially misleading in installed or consuming projects.

## Intended outcome

The manifest command is available only when Specle is being developed from a directory whose `pyproject.toml` declares `[project] name = "specle"`. Everywhere else, it is indistinguishable from an unknown `specle` subcommand.

## Scope

- Determine developer context from `pyproject.toml` in the process current directory only.
- Treat the context as eligible only when its parsed `[project].name` is exactly `"specle"`.
- Register and execute `manifest` only in that eligible context.
- Preserve the manifest command’s existing arguments and behaviour when eligible.
- Make ineligible `specle manifest` parsing fail through the same invalid-command path, with the same exit behaviour and output shape as another unknown subcommand.

## Boundaries

- Do not advertise `manifest` in general CLI help, usage, documentation, or generated command inventories.
- Do not add an environment variable, configuration switch, parent-directory search, package-installation heuristic, or alternate invocation to enable it outside the eligible current directory.
- A missing, unreadable, malformed, or non-matching current-directory `pyproject.toml` is ineligible.
- This change does not alter manifest file format, generation, append-only semantics, or release workflow when the command is eligible.

## User stories

### 1. Use manifest tooling while developing Specle

As a Specle maintainer working from the project root, I want the manifest command to remain available so I can perform release-preparation work.

#### Acceptance criteria

1. WHEN the current directory contains a parseable `pyproject.toml` with `[project] name = "specle"` THEN `specle manifest <output>` SHALL be accepted and retain its existing manifest-generation behaviour.
2. WHEN that developer context is eligible THEN help and usage output SHALL include the manifest command and its existing argument contract.

### 2. Hide developer-only tooling elsewhere

As a user of an installed Specle command, I do not want release-maintenance tooling exposed in normal command discovery or invocation.

#### Acceptance criteria

1. WHEN the current directory has no eligible `pyproject.toml` THEN general `specle` help and usage output SHALL NOT mention `manifest`.
2. WHEN the current directory has no eligible `pyproject.toml` THEN `specle manifest` SHALL fail with the same exit status, output stream, and invalid-command message form as another unknown subcommand.
3. WHEN `pyproject.toml` is missing, unreadable, malformed, lacks `[project].name`, or declares a name other than exactly `"specle"` THEN the command SHALL treat the directory as ineligible.

### 3. Keep the boundary local and predictable

As a maintainer, I want eligibility to be explicit and local so incidental repository layout or environment state cannot expose developer tooling.

#### Acceptance criteria

1. WHEN an eligible `pyproject.toml` exists only in a parent or child directory THEN `specle manifest` SHALL remain unavailable unless the current directory itself is eligible.
2. WHEN an environment variable, installed package metadata, or another configuration source suggests Specle development without an eligible current-directory `pyproject.toml` THEN `specle manifest` SHALL remain unavailable.
