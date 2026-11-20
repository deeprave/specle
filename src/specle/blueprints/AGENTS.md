# Shared Agent Workflow

This is the portable entrypoint for the repository's spec-driven workflow. A repository-root `AGENTS.md` should direct agents here while retaining only genuinely local execution or tool instructions.

Specle initialisation distributes reusable `skills/` and `steering/` only. It does not install this entrypoint, `.agents/project/`, `.specle/`, a root `AGENTS.md`, or a launcher; those remain project or future-client concerns. This portable entrypoint and both distributed inventories are the source blueprints under `src/specle/blueprints/`.

## Start here

1. Read `.agents/steering/*.md`. These are reusable policy: context state, lifecycle, and testing principles.
2. If `.agents/project/README.md` is absent, use the `onboard` skill before relying on project architecture, commands, security rules, API conventions, or tracker configuration.
3. If the project overlay exists, treat `.agents/project/*.md` as the authoritative project-specific facts. Read its README and only the documents relevant to the task.
4. Read the matching skill in `.agents/skills/` before performing a workflow stage.
5. For spec work, read the selected spec from `.specle/current-spec` when it exists and use the target's `status.json` as the durable lifecycle record. A missing selector means no work is selected in this checkout.

## Workflow

Use the local skills in the following order for feature work:

`spec` → `activate` → `estimate` → `design` → `tasks` → `build` → `verify` → `review` → `commit`; use `complete` only for branch-and-pull-request delivery.

Before activation, an explicitly named normal spec may be estimated, designed, or given tasks without becoming current or continuing automatically. Tasks require a design. `activate` is the only operation that makes normal work current and begins the required estimate → design → tasks preparation chain before build.

A clean verification result is `verified`, not `complete`; a subsequent passing review makes the work `approved`. The selected delivery model determines whether `commit` completes that work or creates a `committed` branch-and-pull-request delivery for `complete` to finish. After review findings, use `triage` to record decisions, then `resolve` to route accepted decisions; it uses `revise` for corrections to the selected spec's requirements, design, or plan. Use `status` to inspect durable lifecycle state.

Alternative paths are `bugfix` for a bounded defect, `refactor` for behaviour-preserving work, and `spike` for an investigation that does not implement changes. Use `prepare` to create an unselected bugfix or refactor for named later implementation.

When each step ends, suggest the next step and any alternatives, if they exist. When the user explicitly says `next`, automatically invoke the previously suggested next step; do not require them to restate its command.

## Root bootstrap block

When adding this framework to a repository without a project overlay, add the following temporary block to the root `AGENTS.md` immediately after its pointer to this file. The `onboard` skill removes the marked block only after it has created and validated the overlay; the durable pointer to this file remains.

```md
<!-- agents-onboard:start -->
This repository has not yet established `.agents/project/` guidance. Use the `onboard` skill before feature work, then remove this marked bootstrap block.
<!-- agents-onboard:end -->
```
