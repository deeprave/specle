# Specle

[![Tests](https://img.shields.io/github/actions/workflow/status/deeprave/specle/test.yml?branch=main&label=tests&logo=github)](https://github.com/deeprave/specle/actions/workflows/test.yml)
[![Maintenance](https://img.shields.io/badge/maintenance-active-brightgreen.svg)](https://github.com/deeprave/specle)
[![Python versions](https://img.shields.io/badge/python-3.13%20%7C%203.14%20%7C%203.15-blue?logo=python&logoColor=white)](https://github.com/deeprave/specle/actions/workflows/test.yml)

Specle is a set of AI-agent skills for lightweight, change-driven development. It provides a practical way to describe a focused change, work through it with an agent, and keep the resulting work clear and reviewable—without adding unnecessary process.

## What’s included

- Human-friendly Markdown files that document the workflow and its changes.
- Agent skills for guiding the stages of change-driven development.
- A small Python management script, designed to be run through `uvx`.

## Approach

Specle keeps changes small and purposeful. A change should give people and agents enough shared context to make a change safely, while remaining easy to read, discuss, and maintain.

The project is intended to support development workflows where documentation and agent instructions are first-class, rather than an afterthought.

See [the lifecycle reference](docs/LIFECYCLE.md) for the lifecycle implemented today, including its workflow transitions and audit.

## Initialise an installation

Initialise the reusable Specle distribution at an explicit, existing target directory:

```console
uvx specle init /path/to/project
```

This installs the packaged skills and policy documents into `/path/to/project/.agents/` and generates `skills/specle/index.json`. It never assumes the current directory, and it does not create or modify `.agents/project/`, `.specle/`, a root `AGENTS.md`, or a shell launcher. If a managed skill, policy document, or index already exists, the command stops before writing; rerun with `--force` to replace only those managed destinations.

## Update an installation

Preview a managed distribution update before writing it:

```console
uvx specle update /path/to/project --dry-run
```

An ordinary update applies conflict-free changes. If it would replace locally modified managed content or an unmanaged path at a package-managed destination, it reports every conflict, makes no changes, and exits non-zero. Rerun with `--yes` to approve every reported selective replacement, or use `--force` for the broader init-equivalent managed replacement.

Standalone launcher, client-integration, and project-bootstrap commands are deliberately deferred to later changes.

## JSON schemas

Specle distributes versioned JSON Schema contracts for its shared agent-managed records. Export a portable schema tree for external tools or integrations with:

```console
uvx specle schemas export /path/to/schemas
```

Use `--force` only when intentionally replacing an existing export. See [the layout and contract reference](docs/LAYOUT.md#json-contracts).

## Skill inventory

In this repository, `src/specle/blueprints/` is the canonical source inventory of the portable `AGENTS.md`, reusable skill blueprints, and steering documents. Each skill blueprint declares a human-facing `specle_group`, concise `description`, detailed `usage`, and its direct `requires` dependencies in frontmatter. Any skill with `specle_group` is considered to be part of the Specle skill inventory.

## Status

Run `specle status` to see the selected change, local sidecars, Git worktree summary, and concise optional context. The command is read-only and does not list changed paths. Use `specle status --markdown` to output Markdown source.
