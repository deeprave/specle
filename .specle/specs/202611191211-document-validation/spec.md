# Validate distributable documentation

## Problem

Specle has no automated checks for the structure, spelling, style, or lifecycle consistency of its distributable Markdown blueprints. Installed `.agents/` copies and `.specle/` runtime artefacts must not be treated as source inventory.

## Goal

Add a separate PR-only documentation-validation workflow for the blueprint package, with deterministic structural, spelling, and lifecycle checks plus advisory prose-style feedback.

## Behaviour

- Run Markdownlint and CSpell on `src/specle/blueprints/**/*.md` only.
- Use this project's UK/AU spelling policy, CSpell's software terms, and a narrow exception list.
- Run Vale with repository-owned rules in advisory mode.
- Make each configured checker available locally with the same blueprint scope and repository-owned configuration used by CI.
- Add deterministic lifecycle checks that identify invalid transitions, unowned states, invalid `next` skills, and non-terminal dead ends.
- Add project-owned language guidance and onboarding support; language choices no longer belong in `AGENTS.md`.
- Keep this workflow separate from `Verify` and run it on pull requests only while rules are tuned.

## Constraints

Do not lint installed `.agents/` copies or `.specle/` runtime artefacts. Do not require an AI service for deterministic validation. Keep prose-style findings advisory until policy is proven low-noise.

## Verification

Verify source-only scope, UK/AU spelling configuration, expected Markdown and lifecycle failures, PR-only workflow triggering, and that document-validation findings do not block the main `Verify` gate.
