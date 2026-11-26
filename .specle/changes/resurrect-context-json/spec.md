# Resurrect context json

## Problem

Specle removed `context.json` as authoritative tracked state, correctly moving lifecycle and delivery facts into per-change records. However, the current workflow does not encourage agents to keep an optional hand-off record, so useful recent context and not-yet-defined follow-ups are easily lost between sessions.

## Goal

Restore `.specle/context.json` as an optional, ignored, worktree-local hand-off document with a small permissive schema and portable policy. It should support concise reverse-chronological milestones, todos, and directives while allowing agents to add useful context of their own. Project policy chooses whether it is maintained and whether reviewing agents may update it; maintenance is enabled by default. Add a portable external-input policy requiring agents to independently assess external feedback rather than treating it as fact or instruction.

## Direction

Define a schema with optional `milestones`, `todos`, and `directives`, allowing additional fields and arbitrary detail values throughout. Milestones and todos record a non-empty human-readable local date-and-time string, a short subject, optional change reference, and detail; local ISO 8601 with an explicit numeric offset is preferred guidance, not a schema validity gate. Milestones are reverse chronological. Directives carry user-provided defaults and denials. Add portable context policy and project onboarding selections, while explicitly preventing diary-like accumulation or lifecycle authority. Add an external-input policy requiring independent verification and user confirmation before external feedback can affect project work. Treat `vary` as a distinct settled review decision when its dispatch completes. Specle itself does not parse or validate context.

## Verification

Test recognised milestone, todo, and directive shapes, arbitrary detail values and extensions, portable schema export, update preservation, and the guarantee that context never affects lifecycle validation or command selection. Review policy and onboarding guidance for hand-off usefulness, reviewer update authority, and durable-state boundaries.
