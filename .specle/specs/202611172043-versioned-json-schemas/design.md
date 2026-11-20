# Design: versioned JSON contracts

## Overview

Specle will make every shared agent-managed JSON record self-identifying and validate it against package-owned JSON Schema resources. The first supported version is a baseline: existing repository records are updated atomically, while unversioned runtime input is rejected rather than interpreted heuristically.

The change covers runtime context, current issue selection, spike findings, tracker links, and the installed skill index. It also adds a portable export command for consumers that cannot import the Python package.

## Architecture

```text
contract instance ── $schema URI ──> packaged JSON Schema resource
        │                                  │
        ├── Specle reader/writer ───────────┤
        ├── public registry/loader ─────────┤── internal $ref registry
        └── `specle schemas export` ────────┘── portable schema tree
```

### Packaged resources and identifiers

Add a package resource tree under `src/specle/schemas/`, containing one schema per contract and shared fragments. Resources use JSON Schema Draft 2020-12. Every published schema has a stable, package-controlled `$id`:

```text
https://github.com/deeprave/specle/schemas/<contract>/1.0
```

Shared fragments have the same identifier pattern and are referenced by those absolute IDs. The package resource layout mirrors the identifier hierarchy so export produces a self-contained directory tree whose `$ref` relationships remain resolvable.

Each contract instance gets a top-level `$schema` string containing its exact versioned contract URI. The governing schema requires that value with `const`; readers select the schema through the URI, reject an absent value, and report an unsupported URI without attempting legacy compatibility.

### Registry and public API

Add a dedicated schema module that uses `importlib.resources` rather than source-tree paths. It will:

- expose the known contract identifiers and load a schema by identifier;
- construct an in-memory Draft 2020-12 registry so internal `$ref` values resolve from packaged resources;
- validate an object against its declared `$schema` URI; and
- expose an export operation that copies the complete resource tree to a caller-provided destination.

Unknown identifiers, missing resources, invalid JSON, and validation failures raise concise package-specific errors. The implementation may use the maintained `jsonschema` validator and its reference registry; JSON Schema resources themselves remain data files.

### CLI export

Add a nested command:

```shell
specle schemas export <destination> [--force]
```

The command exports all schemas, not a selected subset. It refuses an existing destination unless `--force` is explicitly supplied. Export stages a sibling temporary directory, replaces the destination only after a complete copy succeeds, and reports errors without a traceback. It makes no changes to an installed `.agents` inventory or project runtime state.

### Contract consumers and writers

Update the five producer/consumer paths atomically:

| Contract | Primary producer/consumer |
| --- | --- |
| runtime context | lifecycle/context workflows and `specle validate` |
| current issue | activation/context workflows and runtime validation |
| spike findings | spike/summary workflows |
| tracker links | track workflow |
| skill index | installation/index generation and `specle validate` |

Runtime validation will load and validate context/current-issue records through the registry before applying lifecycle-specific rules. Index generation adds the index contract URI; comparison validates the generated resource under the same contract. Blueprint instructions that create or update the remaining contract instances will name the appropriate URI and required fields. Sync those blueprint changes to the active `.agents` inventory.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Missing `$schema` | Reject as an unsupported unversioned contract with the record path. |
| Unknown schema URI | Reject with the URI and supported contract identifiers. |
| Invalid instance | Report the contract URI, JSON path, and schema-validation reason. |
| Missing packaged resource/internal `$ref` | Raise a registry error naming the unavailable identifier. |
| Export collision | Abort before replacement unless `--force` is present. |
| Export staging or replacement failure | Retain the original destination and remove only temporary staged output when safe. |

## Documentation and output

Extend the documentation layout reference with the contract inventory, URI convention, versioning rules, and registry/export interfaces. Keep human explanation in Markdown; schemas and instances remain JSON. The export command prints the destination after successful installation.

## Test strategy

- Unit-test each packaged schema against a minimal valid record and representative invalid `$schema`/required-field cases.
- Test that registry loading works through `importlib.resources` and resolves an internal shared-schema `$ref`.
- Test every current JSON producer produces a versioned valid instance, including generated indexes.
- Test runtime validation reports missing and unsupported contracts clearly before lifecycle validation.
- Test CLI export into a new directory, collision refusal, `--force` replacement, and failure-safe staging behaviour.
- Run `pytest`, `ruff check`, `ruff format --check`, `ty`, `specle validate .`, and `git diff --check`.

## Dependencies

None. This work is independent of queued state restructuring and document validation.
