---
name: analyse
specle_group: Discovery
description: >-
  Analyse codebases for guidance drift, technical debt, and risk.
usage: >-
  Use when a developer asks to understand a codebase, audit risks or technical debt, or refresh project guidance from implementation evidence.
---

# Analyse the codebase and update project guidance

Assess the codebase against its recorded project guidance and propose concrete updates.

## Workflow

1. Read `.specle/context.json` for current state and spec summary.
2. Analyse the code: its tech stack, structure, conventions and patterns in use.
3. Review `.agents/steering/*.md` and the relevant authoritative `.agents/project/*.md` files, and compare the project guidance against reality.
4. Identify risks, tech debt, and areas requiring improvement.

## Output

A clear analysis report, plus **specific proposed edits** to `.agents/project/*.md` where project facts or conventions drift from the code. Amend project documents only when the reusable workflow itself is wrong. Get confirmation before writing either kind of guidance change.

## Next

- `spec` — turn an improvement into a tracked spec.
- `review` — review a specific change in depth.
