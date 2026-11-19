# Add `specle validate`

## Problem

Specle has human-readable lifecycle guidance but no structured transition declarations on the skills that implement it. A separate hand-maintained lifecycle contract would only validate itself, not the production skill workflow.

## Goal

Add `specle validate <target-directory>` to derive lifecycle validation from installed Specle skill declarations and verify target state with clear, actionable diagnostics.

## Behaviour

- Require lifecycle-owning skills to declare their possible transitions as structured frontmatter metadata.
- Require each lifecycle-owning skill to direct the agent to consult its own `lifecycle` frontmatter before applying a lifecycle transition.
- Build on the StrictYAML schema-backed parser established by `adopt-strictyaml-frontmatter`, rather than maintaining a restricted scalar parser or embedding JSON in YAML.
- Derive and audit the transition graph from installed Specle skills for reachable terminal outcomes, valid edges, and command availability.
- Validate target `.specle` JSON, current-issue alignment, spec paths, lifecycle status, and allowed next workflows.
- Return non-zero on validation failures without modifying the target.
- Keep schema-versioning work independent; validate the current established JSON shapes without adding a schema version or migration contract.

## Constraints

The target directory is required; validation must never infer the current working directory. Human Markdown remains explanatory, while declared skill metadata is the deterministic validation interface. The command is read-only and agent-client agnostic. This change depends on `adopt-strictyaml-frontmatter` for the parser and existing metadata schema; it alone adds lifecycle declarations to that schema.

## Verification

Test valid and invalid skill transition declarations, dead-end and unreachable-state detection, target layout and JSON errors, current-issue/context mismatches, invalid skill names, and read-only command behaviour.
