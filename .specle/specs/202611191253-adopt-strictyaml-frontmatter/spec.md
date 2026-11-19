# Adopt StrictYAML frontmatter

## Problem

Specle currently extracts skill frontmatter with a custom line parser. It supports only a narrow set of scalar forms, cannot validate a coherent metadata shape, and would become brittle once skills carry structured lifecycle declarations.

## Goal

Replace the custom parser with StrictYAML and a schema for the existing package-owned skill frontmatter, then migrate both the blueprint and active local skill inventories to the schema's clear block-style representation.

## Behaviour

- Parse package-owned skill frontmatter only through StrictYAML and a safe, constrained schema.
- Define the current fields (`name`, `specle_group`, `description`, `usage`, and `requires`) with their expected types and requiredness.
- Migrate all blueprint skills and their active `.agents/skills/` counterparts to the schema-compatible block style, including block-list `requires` values.
- Preserve existing inventory, dependency validation, and generated index behaviour.
- Produce actionable metadata errors without tracebacks.

## Boundaries

This change does not introduce lifecycle transition declarations, `specle validate`, JSON schema versions, or validation of third-party skills. `add-specle-validate` will explicitly build lifecycle metadata and the validator on this parser foundation.

## Verification

Test valid and invalid frontmatter, required and optional fields, malformed YAML, dependency validation, index generation, and blueprint/active-inventory parity.
