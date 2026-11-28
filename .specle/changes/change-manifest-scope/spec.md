# Change manifest scope

## Motivation

The manifest command exists solely to prepare release provenance for Specle itself. Its current unconditional parser registration exposes developer tooling to ordinary installed-command users.

## Intended outcome

Expose `specle manifest` only from a current directory whose parsed `pyproject.toml` declares the exact project name `specle`. Outside that context, omit it from help and handle it exactly as an invalid command.

## Scope and impact

The parser must decide eligibility before registering the manifest subcommand. The implementation should use standard TOML parsing of only the current directory’s configuration, fail closed for every read or parse problem, and preserve manifest execution unchanged when eligible.

## Boundaries

The change intentionally does not provide an override, discover a project root, inspect installed metadata, or document the command for ordinary users. It is a command-exposure change, not a manifest-format or release-process change.

## Verification direction

Behavioural CLI tests should compare eligible manifest invocation with existing behaviour, verify its presence in eligible help, and compare ineligible manifest invocation byte-for-byte or equivalently with an unknown-command failure. Cover missing, malformed, non-matching, and parent-only `pyproject.toml` cases.
