# Add triage elicitation

## Problem

Free-form triage prompts do not take advantage of clients that can present structured choices, and their wording does not clearly name the alternative path for a varied or discussed decision.

## Goal

Define a portable, client-capability-aware triage prompt: native elicitation when supported and a consistent textual fallback everywhere else.

## Direction

Keep triage's one-at-a-time decision flow and durable finding records unchanged. Standard choices are accept, decline, defer, and other; other collects a user-directed variation or discussion before anything is recorded. Document client elicitation as conditional capability use rather than a required protocol.

## Verification

Check the blueprint and installed triage guidance for the same structured-choice and fallback contract, validate lifecycle metadata, and run the repository quality gates.
