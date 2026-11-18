# Shared Agent Workflow

This is the portable entrypoint for the repository's spec-driven workflow. A repository-root `AGENTS.md` should direct agents here while retaining only genuinely local execution or tool instructions.

## Start here

1. Read `.agents/steering/*.md`. These are reusable policy: context state, lifecycle, and testing principles.
2. If `.agents/project/README.md` is absent, use the `onboard` skill before relying on project architecture, commands, security rules, API conventions, or tracker configuration.
3. If the project overlay exists, treat `.agents/project/*.md` as the authoritative project-specific facts. Read its README and only the documents relevant to the task.
4. Read the matching skill in `.agents/skills/` before performing a workflow stage.
5. For spec work, keep `.specle/current-issue.json` and `.specle/context.json` aligned with the lifecycle and context schema.

## Workflow

Use the local skills in the following order for feature work:

`spec` → optional `estimate` → `design` → `tasks` → `build` → `verify` → `review`.

Use `implement` when an existing spec should advance through its missing planning stages and build tasks in one request; it reuses completed artifacts and stops at unresolved decisions.

A clean verification result is `verified`, not `complete`; a subsequent passing review normally completes a spec. After review findings, use `triage` to record decisions, then `resolve` to route accepted decisions; it uses `revise` for corrections to the current spec's requirements, design, or plan. Resolve completes its selected target only when every finding is terminally no-action or has a completed dispatched follow-up. Use `context` after major progress or context compaction, and `status` to inspect recorded lifecycle state.

Alternative paths are `bugfix` for a bounded defect, `refactor` for behaviour-preserving work, and `spike` for an investigation that does not implement changes. Use `prepare` to create a non-active bugfix or refactor for named later implementation.

When each step ends, suggest the next step and any alternatives, if they exist. When the user explicitly says `next`, automatically invoke the previously suggested next step; do not require them to restate its command.

## Root bootstrap block

When adding this framework to a repository without a project overlay, add the following temporary block to the root `AGENTS.md` immediately after its pointer to this file. The `onboard` skill removes the marked block only after it has created and validated the overlay; the durable pointer to this file remains.

```md
<!-- agents-onboard:start -->
This repository has not yet established `.agents/project/` guidance. Use the `onboard` skill before feature work, then remove this marked bootstrap block.
<!-- agents-onboard:end -->
```
