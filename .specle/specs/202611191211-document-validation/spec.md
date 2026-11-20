# Validate distributable documentation

## Problem

Specle has no local agent capability to check the structure, spelling, style, or lifecycle consistency of its distributable Markdown blueprints and repository documentation. Installed `.agents/` copies and `.specle/` runtime artefacts must not be treated as source inventory.

## Goal

Add a local document-validation skill and a separate pull-request workflow for the distributable blueprint package and repository documentation. Both use deterministic structural, spelling, and lifecycle checks plus advisory prose-style feedback.

## Behaviour

- Run Markdownlint and CSpell on the blueprint package plus repository documentation (`README.md` and `docs/**/*.md`).
- Develop repository-owned Markdownlint, CSpell, and Vale configurations that fit the Markdown conventions used by Specle skills and documentation, including YAML frontmatter, examples, intentionally unwrapped prose, UK/AU spelling, and established software terminology. Use shared configuration by default, with documented scope-specific configuration only where the content genuinely needs different rules.
- Use this project's UK/AU spelling policy, CSpell's software terms, and a narrow exception list.
- Run Vale with narrow repository-owned rules in advisory mode.
- Run the installed checkers locally with source-documentation scope and repository-owned configuration.
- Add deterministic lifecycle checks that identify invalid transitions, unowned states, invalid `next` skills, and non-terminal dead ends.
- Add project-owned language guidance and onboarding support; language choices no longer belong in `AGENTS.md`.
- Add a pull-request-only document-validation workflow that uses the same source scope and repository-owned configuration as the local skill.
- Add changed-file pre-commit hooks for Markdownlint, CSpell, and advisory Vale, plus an inventory-wide `specle validate` hook.
- Keep document validation separate from the main `Verify` aggregate and non-required by repository rules.

## Constraints

Do not lint installed `.agents/` copies or `.specle/` runtime artefacts. Validate `README.md` and `docs/**/*.md` alongside the blueprint package. Use the already installed local tools for the skill and workflow-provided tools for CI; do not add project dependencies. All validation runs must be read-only: they report findings without changing documents. Configure tools for intentional repository conventions rather than disabling broad classes of checks or rewriting valid content to suit generic defaults. Do not require an AI service for deterministic validation. Keep prose-style findings advisory and non-required by repository rules.

## Verification

Verify source-only scope, UK/AU spelling configuration, expected Markdown and lifecycle failures, advisory Vale output, changed-file pre-commit behaviour, PR-only workflow triggering, read-only execution, and independence from the main `Verify` gate.
