---
name: context
specle_group: Coordination
description: >-
  Reconcile compact Specle context with recorded work state.
usage: >-
  Use after material progress, context compaction, or suspected state drift; reconcile evidence without inventing lifecycle transitions.
---

# Refresh context.json

Regenerate `.specle/context.json` so it reflects the current spec and progress. It is the structured
context other agents read first.

## Workflow

1. Read `.specle/current-issue.json` to get the current spec folder.
2. If `current_spec.kind` is `spike`, read `findings.json`. Otherwise, read that folder's `requirements.md`, `spec.md`, `tasks.md`, and `design.md`.
3. Read `.agents/steering/*.md`, especially `context.md` and `lifecycle.md`. Read project guidance only when it is needed to refresh recorded project facts. Treat `.agents/project/` documents as authoritative when they apply.
4. Regenerate `.specle/context.json`, keeping the existing structure. Include at least:
   - `current_spec` — name, path, kind, status, progress (`tasks_completed`/`tasks_total`), and the spike outcome path when applicable.
   - `verification` and `review` — last known evidence in the schema defined by `context.md`.
   - `queued_specs` — every unfinished queued spec, retaining its name, path, kind, status, next step, and any recorded dependencies.
   - `python_checks`, `commit_policy` — carry forward unless they changed.
   - `current_diagnosis` / `requirements_summary` — condensed `spec.md` content, not the full requirements document.
5. Write valid JSON that follows `context.md` and identifies the current baseline contract with `"$schema": "https://github.com/deeprave/specle/schemas/context/1.0"`. Keep it concise and actionable; do not paste whole specs. Default a missing legacy kind to `change`, preserve unknown non-empty kebab-case kinds, and do not infer a verification or review transition from task checkboxes.

Run this after context compaction or major changes so the next agent starts with accurate context.

## Next

- `build` — continue implementing.
- `verify` — check the implementation against the spec.
