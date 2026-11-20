# Design: add `specle validate`

## Overview

Add a read-only `specle validate <target-directory>` command. It validates the target's installed Specle skill lifecycle contract and its current runtime state. The lifecycle graph comes from constrained `lifecycle` frontmatter on the skills that own transitions; Markdown steering remains human-facing policy and is not parsed as program input.

The implementation extends the StrictYAML metadata parser delivered by `adopt-strictyaml-frontmatter`. It does not introduce JSON-schema version fields, migrations, or compatibility assumptions.

## Architecture

```text
target directory
  ├─ .agents/skills/*/SKILL.md
  │    └─ StrictYAML metadata + lifecycle declarations
  │          └─ lifecycle graph validator
  └─ .specle/{current-issue.json,context.json}
       └─ runtime-record validator ───────┘
                                      │
                              diagnostics / exit status
```

`main.py` retains synchronous argparse parsing and dispatches the read-only validation work through the existing AnyIO entrypoint. A validation module owns graph construction and runtime checks; `inventory.py` owns frontmatter parsing and direct dependency validation.

## Lifecycle declaration contract

Lifecycle-owning skills gain an optional-but-required-for-owners `lifecycle` mapping. Its constrained schema has:

- `accepts`: a block sequence of status/kind/scope entries the skill may operate on.
- `creates`: a block sequence of statuses the skill can create without a prior transition.
- `transitions`: a block sequence of explicit `from`, `to`, and the next owning command or terminal outcome. A state defaults to a compact status scalar; use a nested status/kind/scope mapping only when a transition needs that constraint.
- `terminal`: a block sequence of statuses the skill can establish as terminal.

Only a fixed vocabulary of current statuses, kinds, and scopes is accepted. `requires` remains separate and continues to mean direct installed-skill availability. The parser represents declarations as typed metadata alongside the existing fields.

Each lifecycle-owning skill’s body will explicitly direct the agent to read and obey its own `lifecycle` declaration before it records a transition. The body remains the operational procedure; the declaration is the concise machine-readable authority that the validator audits against it.

## Reference documents

Durable repository references move under `docs/`: `LAYOUT.md` describes the project areas and artefact placement, `LIFECYCLE.md` describes the currently implemented workflow, and `FRONTMATTER.md` describes the package-owned skill metadata contract. The latter documents compact status selectors and nested status/kind/scope selectors. It remains explanatory; the StrictYAML schema in `inventory.py` is the executable constraint.

## Validation flow

1. Require an explicit existing target directory; never infer the current directory.
2. Discover only installed skills carrying the Specle marker, parse their metadata, validate direct dependencies, and collect lifecycle declarations.
3. Build the directed graph from the declarations. Diagnose unknown statuses, missing owner skills, contradictory declarations, unreachable statuses, outgoing-edge gaps, and non-terminal states that cannot reach a declared terminal state.
4. Parse the target's current issue and context JSON. Confirm active-path/name alignment, referenced directories, declared statuses, valid `next` commands, supported kinds, and state evidence that current lifecycle semantics require (for example verification, review, or delivery evidence where applicable).
5. Aggregate path-specific diagnostics and return non-zero if any check fails. Do not mutate the target.

The validator accepts unknown future JSON fields. It validates only the established fields required for the current workflow, leaving versioned schema evolution to its independent change.

## Error handling and output

Expected errors—missing target paths, invalid frontmatter, graph failures, malformed JSON, and inconsistent records—become concise diagnostics naming the relevant file and recovery command when available. `argparse` continues to own argument errors. No validation path writes files, contacts a network service, or installs inventory.

On success, normal output remains one concise completion line. `--verbose` adds stable, human-readable audit lines for the managed-skill inventory, lifecycle graph, generated index resource, and runtime records. It reports counts and paths only; it does not dump parsed records or diagnostics internals.

## Test strategy

- Parser tests for valid and invalid lifecycle declaration shapes, while preserving direct `requires` behaviour.
- Graph tests for valid normal, abbreviated, spike, delivery, and review-resolution paths; then unreachable, ownerless, contradictory, and dead-end variants.
- Runtime tests for missing and malformed inputs, active-path mismatches, missing skills, illegal next commands, invalid statuses, and required evidence.
- CLI tests for a required explicit target, read-only success/failure exit behaviour, and actionable diagnostics.
- Migration/parity tests for source blueprints, active local skills, and the regenerated installed index.
- Link checks for the relocated repository references.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check`.
