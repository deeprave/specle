# Specle

Specle is a set of AI-agent skills for lightweight, spec-driven development. It provides a practical way to describe a focused change, work through it with an agent, and keep the resulting work clear and reviewable—without adding unnecessary process.

## What’s included

- Human-friendly Markdown files that document the workflow and its specifications.
- Agent skills for guiding the stages of spec-driven development.
- A small Python management script, designed to be run through `uvx`.

## Approach

Specle keeps specifications small and purposeful. A spec should give people and agents enough shared context to make a change safely, while remaining easy to read, discuss, and maintain.

The project is intended to support development workflows where documentation and agent instructions are first-class, rather than an afterthought.

See [LIFECYCLE.md](LIFECYCLE.md) for the lifecycle implemented today, including its workflow transitions and audit.

## Skill inventory

In this repository, `src/specle/skills/` is the canonical inventory of reusable skill blueprints. Each blueprint declares a human-facing `specle_group`, concise `description`, detailed `usage`, and its direct `requires` dependencies in frontmatter. Any skill with `specle_group` is considered to be part of the Specle skill inventory.
