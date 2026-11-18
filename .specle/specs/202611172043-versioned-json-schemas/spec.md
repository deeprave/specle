# Versioned JSON contracts

## Problem

Specle relies on several JSON records for runtime state and external-work links, but their shapes are only implicit in skill instructions and prose schema guidance. This makes cross-skill hand-offs, external integrations, and future migrations fragile.

## Goal

Define named, versioned contracts for agent-managed JSON so every reader can identify what it consumes, evolve published versions deliberately, and reject unsupported forms safely.

## Scope

Start with current-issue state, runtime context, spike findings, tracker links, and the generated Specle skill index. Document ownership, location, canonical fields, compatibility, and external-data boundaries. Make new instances identify their contract and version through one consistent mechanism.

## Constraints

Keep human explanation in Markdown and operational records in JSON. Do not tie the contracts to a specific agent client, external tracker, or JSON-schema library. This change establishes the first supported versions; it updates the repository's existing experimental records atomically rather than supporting unversioned records at runtime.

## Verification

Validate supported records, reject missing or unsupported contract identities with clear errors, and confirm tracker links retain multiple sources plus an optional destination.
