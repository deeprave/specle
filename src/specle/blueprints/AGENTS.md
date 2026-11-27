# Shared Agent Workflow

This is the portable entrypoint for the repository's change-driven workflow. A repository-root `AGENTS.md` should direct agents here while retaining only genuinely local execution or tool instructions.

Specle initialisation distributes reusable `skills/` and `policies/` only. It does not install this entrypoint, `.agents/steering/`, `.agents/project/`, `.specle/`, a root `AGENTS.md`, or a launcher; those remain project or future-client concerns. This portable entrypoint and both distributed inventories are the source blueprints under `src/specle/blueprints/`.

## Start here

1. Read `.agents/policies/*.md`. These are reusable Specle policy: lifecycle, delivery, review, testing, external-input handling, and optional hand-off-context principles.
2. Read `.agents/steering/*.md` next. These are project-owned generic overrides.
3. If `.agents/project/README.md` is absent, use the `onboard` skill before relying on project architecture, commands, security rules, API conventions, or tracker configuration.
4. If the project overlay exists, treat `.agents/project/*.md` as the authoritative project-specific facts. Read its README and only the documents relevant to the task.
5. Read the matching skill in `.agents/skills/` before performing a workflow stage.
6. For change work, read the selected change from `.specle/current-change` when it exists and use the target's `status.json` as the durable lifecycle record. A missing selector means no work is selected in this checkout.
7. Treat `.specle/context.json` as optional policy-controlled hand-off context. Ordinary maintenance is enabled unless project policy disables it; a reviewing agent that neither built nor participated in design may update it only with explicit project permission. It is never a prerequisite for a skill or a source of lifecycle facts.

## Workflow

Use the local skills in the following order for feature work:

`define` → `activate` → `estimate` → `design` → `tasks` → `build` → `verify` → `review` → `commit` → `complete`.

Before activation, an explicitly named normal change may be estimated, designed, or given tasks without becoming current or continuing automatically. Tasks require a design. `activate` is the only operation that makes normal work current and begins the required estimate → design → tasks preparation chain before build.

A clean verification result is `verified`, not `complete`; a subsequent passing review makes the work `approved`. `commit` records the delivery event and moves the work to `committed`; `complete` archive-finalises every delivery model. After review findings, use `triage` to record decisions, then `resolve` to route accepted decisions; it uses `revise` for corrections to the selected change's requirements, design, or plan. Use `status` to orient current work and `changes` to inspect pending lifecycle state.

`cancel <change-name>` is an explicit alternative for ending any active non-terminal change without delivery. It never infers the selected target, and it requires user-directed handling of dependencies and in-flight work before archiving the record as `cancelled`.

Alternative paths are `bugfix` for a bounded defect, `refactor` for behaviour-preserving work, and `spike` for an investigation that does not implement changes. Use `prepare` to create an unselected bugfix or refactor for named later implementation.

When each step ends, suggest the next step and any alternatives, if they exist. When the user explicitly says `next`, automatically invoke the previously suggested next step; do not require them to restate its command.

## Shell execution

In zsh shell snippets, do not use `path` as a variable name: it is the special array that backs `PATH`.

## Root bootstrap block

When adding this framework to a repository without a project overlay, add the following temporary block to the root `AGENTS.md` immediately after its pointer to this file. The `onboard` skill removes the marked block only after it has created and validated the overlay; the durable pointer to this file remains.

```md
<!-- agents-onboard:start -->
This repository has not yet established `.agents/project/` guidance. Use the `onboard` skill before feature work, then remove this marked bootstrap block.
<!-- agents-onboard:end -->
```
