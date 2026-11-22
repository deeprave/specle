# Design: Enhance define skill

## Overview

Refine managed guidance so `define` creates evidence-led, substantive but unselected normal changes and `build` provides the sole alignment boundary before implementation. The lifecycle frontmatter and output files remain the same; the workflow gains explicit investigation, material-uncertainty, definition summary, and build confirmation sequences.

## Architecture

```text
user request
    |
read relevant guidance, repository evidence, and active/archive changes
    |
material uncertainty? ── yes ──> focused elicitation with evidence-based default
    | no                               |
    +──────────────────────────────────+
    |
write requirements.md + spec.md + defined status.json
    |
present non-blocking definition summary → leave change unselected

activate → estimate → design → tasks
    |
build: present specification alignment summary → explicit confirmation → implementation
```

## Skill contract

- Keep the existing concise `description`, `usage`, `specle_group`, and lifecycle declaration.
- Direct agents to investigate applicable guidance, code, documentation, and active/archive changes before creating artifacts.
- Distinguish evidence-backed facts, requested outcomes, scope boundaries, material uncertainty, and minor recorded assumptions.
- Ask the user only when an answer would change scope, observable behaviour, compatibility, acceptance criteria, or change type. Do not ask questions answerable from evidence.
- Require substantive, testable requirements and a concise specification without mandating a proposal format or heading vocabulary.
- Stop without creating a change when existing work fully covers the request; use an explicit boundary for partial overlap.
- Create the durable defined change, then report a non-blocking definition summary without selecting or progressing it.
- Treat a duplicate proposed slug as blocking: report the conflicting change and let the user rename or investigate it.
- Preserve unique-name creation, `defined` status, and the prohibition on selecting or progressing the new change.
- Keep activation and task progression unchanged. Before a planned change's first implementation action, `build` presents a specification alignment summary and requires explicit confirmation, even with decision-gated progression.

## Data and synchronisation

The canonical managed guidance comprises `src/specle/blueprints/skills/{define,activate,tasks,build}/SKILL.md`, `src/specle/blueprints/policies/{lifecycle,automation}.md`, and the human lifecycle reference. Copy each managed file unchanged into its corresponding `.agents/` path, then regenerate `.agents/skills/specle/index.json` from the installed inventory. No schema, lifecycle-state, or new-skill change is needed.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Relevant evidence resolves a question | Record the evidence-led conclusion; do not ask the user. |
| Material uncertainty remains | Ask focused questions before creating change artifacts. |
| Existing work already covers the request | Report the evidence and stop without creating a duplicate change. |
| Proposed slug already exists | Report the conflicting change and stop before writing a durable record. |
| Related work is not a real prerequisite | Keep changes independent and state the boundary rather than adding a dependency. |
| User corrects the pre-build alignment summary | Revise the relevant artifacts and present the updated summary before implementation. |

## Test strategy

This is Markdown guidance, not production code. Review the blueprint and installed copies for identical content, validate the managed inventory and lifecycle, inspect the regenerated index entry, and run repository quality gates. Do not add tests for the skill documents themselves.
