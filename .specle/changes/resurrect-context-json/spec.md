# Resurrect context json

## Problem

Specle removed `context.json` as authoritative tracked state, correctly moving lifecycle and delivery facts into per-change records. However, the current workflow does not encourage agents to keep an optional handoff record, so useful recent context and not-yet-defined follow-ups are easily lost between sessions.

## Goal

Restore `.specle/context.json` as an optional, ignored, worktree-local handoff document with a small permissive schema. It should support concise milestones and todos while allowing agents to add useful context of their own.

## Direction

Define a schema with optional `milestones` and `todos`, allowing additional fields throughout. Milestones require a creation time and short summary, with an optional change reference; todos are concise, optionally linked to a change, and may be transferred when formalised. Update portable guidance to encourage useful refresh and regular pruning, while explicitly preventing diary-like accumulation or lifecycle authority.

## Verification

Test optional-file handling, recognised milestone and todo shapes, extensibility, invalid explicit context validation, and the guarantee that missing or invalid context does not affect lifecycle validation or command selection. Review guidance for handoff usefulness and durable-state boundaries.
