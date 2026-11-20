# Technical design: add skill blueprints

## Overview

Add a packaged skill inventory API and `specle` CLI subcommands for installing and updating Specle skills. Each source blueprint declares its Specle group and direct dependencies in frontmatter. The installer resolves the complete dependency closure before changing the active `.agents/skills/` inventory.

## Metadata contract

Every source `SKILL.md` retains its existing frontmatter and adds these top-level fields:

```yaml
specle_group: Planning
requires: []
```

`specle_group` is the non-empty marker that identifies a skill as part of the Specle inventory and provides its human-facing inventory group. `requires` is an optional inline list of skill names and defaults to an empty list when omitted. It represents only direct, required workflow dependencies; optional next steps do not appear in it.

The metadata reader does not implement general YAML parsing or add a YAML dependency. It extracts only `specle_group` and `requires` from the frontmatter, rejects duplicate or malformed instances of those fields, and ignores unrelated frontmatter fields such as multiline descriptions.

## Work classification

Extend the existing `.specle/context.json` records rather than creating per-spec manifests. `current_spec`, every `queued_specs` record, and every `recent_specs` record carry a `kind` string. New regular work records use `change`; the initial named kinds are `change`, `bugfix`, `docs`, and `release`.

The context reader treats a missing `kind` in existing records as `change`. It recognises `change`, `bugfix`, `refactor`, `docs`, and `release`, and accepts and preserves any other non-empty kebab-case value so future kinds do not require a schema migration. `kind` never replaces lifecycle `status`: the former identifies the work, while the latter records where that work is in its workflow.

The status skill adds a **Kind** column to its inventory and displays the stored kind, defaulting missing records to `change`.

Bugfixes and refactors use ordinary `YYYYMMDDHHMM-<slug>` directories. Each creates and updates its matching `queued_specs` record with its own `kind`, but does not replace `current_spec` or `.specle/current-issue.json`; this permits bounded side work to progress without displacing active feature work.

## Abbreviated-work verification

Abbreviated work contains `spec.md` and `tasks.md`, rather than the normal `requirements.md` and optional `design.md`. Its `spec.md` is the verification contract.

- A bugfix records the bug description, expected and actual behaviour, reproduction when inferable, root cause, fix approach, and regression-test evidence. Verification confirms the reported defect is resolved, the regression test demonstrates the expected behaviour, and the scope remains a bounded repair.
- A refactor records the current state, target state, behavioural invariants, baseline or characterisation evidence, and refactor approach. Verification confirms the documented invariants remain true, the baseline evidence and required gates pass, and no intentional behavioural feature was introduced.

`verify` defaults to the active normal spec. A user may name a queued abbreviated spec to verify it. On a pass, it changes only that queued record to `verified` with `next: "review"`; on a failure, it leaves that record `building` with `next` set to its owning abbreviated workflow. It never changes the active current issue when handling named queued work.

Both abbreviated workflows normally execute their tasks immediately. The `prepare` dispatcher invokes either one in its non-executing mode, writes the abbreviated `spec.md` and `tasks.md`, and sets only its queued record to `planned` with `next: "implement"`. `prepare` is reserved for this abbreviated-work mode; `plan` remains the normal-spec task-planning concept. The dispatcher reports the generated timestamped spec name, which must be explicitly named to `implement` or `verify` later.

## Implement routing

`implement` is an orchestrator and declares the direct skills it may invoke: `estimate`, `design`, `tasks`, `build`, `bugfix`, `refactor`, and `context`. `prepare` declares `bugfix` and `refactor` as its direct dependencies. The orchestrators resolve a named target against the active or queued records and branch on `kind`.

A normal target follows only missing normal stages. A named queued `bugfix` or `refactor` remains non-active: its owning workflow reuses the existing `spec.md` and `tasks.md`, completes any remaining abbreviated tasks, and leaves `verify` as the next step. Abbreviated work always requires an explicitly named queued target; it must not create a second directory or queued record, and `implement` must not apply estimate, design, tasks, or build to that abbreviated target.

## Status and review of concurrent work

`status` uses the matching context record's explicit `next` value when present; it falls back to the lifecycle table only when no next step is recorded. This keeps queued abbreviated work visible alongside the active normal spec without misreporting its route.

`review` requires `verify` and stops if its target is not verified. It defaults to the verified active normal spec. A queued abbreviated target must be explicitly named, must be `bugfix` or `refactor`, and must be verified. Review scopes its diff inspection to the target's recorded tasks and artefacts rather than unrelated working-tree changes. An approval moves only that sidecar's record to `recent_specs` as `complete`; findings leave only that record queued with `status: "review-findings"` and `next: "revise"`.

## Task planning against repository state

Before generating or reconciling a normal task plan, `tasks` inspects relevant staged and unstaged diffs plus recent commits. It plans remaining work against that evidence, but never infers task completion from a diff or existing code. `build` remains responsible for marking task completion, and `verify` independently confirms the implementation.

## External work sources and destination

`track` treats external systems by role, rather than assuming every issue system is a project tracker. Project tracking guidance configures zero or more read sources and zero or one publish destination. A system may serve both roles, but each role has separate permissions and explicit operations.

`track` requires `spec` because an explicit import may establish a new normal spec when no suitable target exists. It imports one or more named source items into the chosen spec, checks recorded sources for changes without changing the spec until confirmation, and publishes only to the configured destination with explicit authorisation. It never writes to a source.

`track` defaults to the active normal spec. A queued bugfix or refactor may have sources and a destination link, but it must be explicitly named; `track` never selects a queued sidecar implicitly.

Each linked spec stores `.specle/specs/<spec>/tracker-links.json` with a `sources` array and a `destination` object or `null`. The JSON preserves each source or destination system, item kind, identifier, and canonical URL. This record is operational state; project policy remains human-maintained Markdown in `.agents/project/tracking.md`.

## Revision routing

`revise` changes only accepted feedback in place. For a normal active spec, it reconciles the affected requirements, design, and tasks, preserving still-valid completed tasks and returning the lifecycle to the earliest viable stage. For an explicitly named queued bugfix or refactor, it revises only the abbreviated `spec.md` contract and `tasks.md`, reopens or adds the affected task steps, and sets only that record to `planned` with `next: "implement"`. It never changes the active current issue or implements work itself.

## Active spike investigations

A spike is an active `kind: "spike"` work item, rather than an incomplete normal specification. It follows `defined` → `spiking` → `complete` through `.specle/current-issue.json` and `.specle/context.json`; beginning one obeys the same protection against displacing unfinished active work as `spec`.

Its spec directory contains `findings.json`, an agent-managed record with the investigation question, S/M/L/XL effort budget, scope, findings, recommendations, risks, and `outcome_spec` path or `null`. A spike performs only read-only investigation and no verification or review. When a resulting normal spec, bugfix, or refactor exists, its path is recorded as `outcome_spec`; otherwise it remains `null`.

## Project review guidance

`review.md` is a required project-overlay document. Onboarding inventories it and asks, one question at a time, for the review presentation mode, any override of the steering layouts, and policy for automatically accepting or addressing findings. The document records only user-confirmed or source-supported preferences; an unestablished preference remains explicitly unestablished. The reusable P1–P6 severity taxonomy and default presentation layouts are distributed in `.agents/steering/review.md` so projects share the same finding language.

## Completed-work summary

The former `demo` blueprint becomes `summary`. It is a completion-gated communication skill, not a lifecycle gate or an external publishing mechanism. It defaults to completed active work and requires an explicit name for any completed non-active item in `recent_specs`.

Before creating `.specle/specs/<target>/summary.md`, it confirms the selected record has `status: "complete"`; no inferred completion, verification, review, or context transition is permitted. The Markdown summary is deliberately human-facing and stands alongside, rather than replaces, operational JSON. For implementation work it derives only evidenced verification and review results. For a spike it derives the outcome from `findings.json`, foregrounding its recommendation and linking `outcome_spec` when present. Every summary includes a concise copy-ready update, but the skill neither posts it nor changes tracker state.

## Specle workflow guide

The source-only `about` blueprint is renamed `specle`. Its directory and frontmatter name match so the inventory validator can treat it as an ordinary managed skill. It remains source-only until it is separately vetted and installed, avoiding an unreviewed change to the active inventory.

Each Specle blueprint adds a human-readable `specle_group` frontmatter value. The `specle` guide reads `specle_group`, `name`, and `description` directly from installed skill frontmatter. It includes only marked skills, orders a stable set of known groups, sorts skills within each group, and reports an unfamiliar group instead of hiding the skill. The installer uses the same marker to identify eligible active skills while treating its value as presentation metadata rather than a dependency or installation constraint.

## Skill summary and usage metadata

Every blueprint declares a concise `description` and a separate `usage` field. The description carries compact trigger keywords suitable for clients that expose only a name and description during skill selection. Usage records when the skill applies, important preconditions or exclusions, and its expected result without making the selection description verbose.

The installed Specle inventory carries both fields. The `specle` guide decides whether to display concise descriptions, usage guidance, or both according to the user's request. The queued CLI work owns generating the inventory resource and the queued JSON-contract work owns its exact versioned shape; this change standardises the source metadata that those later features consume.

## Review triage

Each reviewed work item stores `.specle/specs/<spec>/review-findings.json`. The record contains source snapshots with stable source identifiers and revisions, plus consolidated findings. A finding retains its source IDs, evidence, P1–P6 severity, analysis, recommendation, duplicate relationship when applicable, decision, and route. Re-observing an unchanged source item does not create a new finding; a changed item is reconsidered with its prior history retained.

`review` records raw internal findings and sets the target to `review-findings` with next `triage`. `triage` can additionally collect explicitly named external sources, asks for a target when it cannot be established, consolidates findings, and presents them using project review guidance. It records accept, decline, skip, defer, or automatic decisions without implementation. When all current findings have decisions, it sets the target to `triaged` with next `resolve`; the later `resolve` skill dispatches one or more accepted routes.

`resolve` requires `triage`, `revise`, `prepare`, `bugfix`, `refactor`, and `spec`. It accepts only a triaged target with decided findings, processes accepted routes in P1–P6 order, and records the selected workflow, execution mode, resulting spec path, and dispatch state in `review-findings.json`. New bugfix and refactor work defaults to `prepare`; direct execution is allowed only when the recorded decision or automatic policy explicitly authorises it. Downstream skills own lifecycle changes when accepted work is dispatched, so dispatching alone never completes the originating reviewed work item.

On every invocation, Resolve reconciles existing dispatches before dispatching anything new. It inspects each resulting work item through its recorded spec path: incomplete or failed follow-up work keeps the selected target `triaged`; completed follow-up work is recorded as completed and is not dispatched again. When every current finding is terminally no-action (`decline`, `skip`, `defer`, or `duplicate`) or has a completed follow-up, Resolve records the review as `resolved` and completes the selected target: the active normal target becomes `complete`, while a named queued abbreviated target moves to `recent_specs` as `complete` without changing the active current issue. This is an explicit reconciliation outcome, not completion merely because work was dispatched.

An accepted `spec` route from an active normal target is a terminal hand-off, not a child follow-up. Resolve defers it while any other current finding has incomplete accepted work. Once every other finding is terminally no-action or has a completed follow-up, Resolve records the hand-off, completes the active current spec, and only then invokes `spec` to initialise the independent normal spec as current work. This ensures the former spec never becomes an unresumable queued normal record, does not wait for work that belongs to a separate flow, and does not bypass another accepted action.

When Resolve finds incomplete recorded follow-up work, it reports that work item's own next step and names `resolve <target>` as the reconciliation step after completion. The lifecycle reference renders the three flows as separate top-to-bottom Mermaid diagrams so each remains readable in a narrow page.

## Lifecycle reference

The root `LIFECYCLE.md` is a human-facing reference derived from the current lifecycle steering and installed workflow behaviour. It maps status-owning skills to their transitions, audits every state for a valid outgoing transition or explicit terminal outcome, and uses an inline Mermaid diagram to show normal, queued abbreviated, and spike paths. It documents Resolve reconciliation of terminal no-action dispositions and completed dispatched work, plus the active-normal independent-spec terminal hand-off once all other findings are settled, but excludes the queued delivery-policy change and its proposed statuses and commands.

## Architecture

```text
specle CLI
    |
    +-- argparse command dispatch
            |
            +-- inventory service
                    |
                    +-- packaged source: importlib.resources / specle/skills
                    +-- metadata reader: Specle group + direct requirements
                    +-- dependency resolver: ordered, cycle-checked closure
                    +-- installer: preflight and copy to <cwd>/.agents/skills
```

Add an inventory module responsible for locating packaged resources, reading metadata, resolving dependencies, and planning copies. Keep CLI parsing synchronous in `build_parser()`, then call the inventory service from the existing AnyIO-backed async entry point. Filesystem operations run through `anyio.to_thread.run_sync` so the public runtime remains asynchronous.

## Installation and update behaviour

`specle install <skill>` resolves the requested source blueprint and every required dependency in dependency-first order. `specle update [<skill>]` refreshes one named Specle skill or every active skill whose local frontmatter declares `specle_group`.

Before copying, the service validates every source blueprint in the planned closure: the directory name and frontmatter name must agree, `specle_group` must be non-empty, each requirement must name another marked source blueprint, and the dependency graph must contain no cycle.

The service then preflights every destination. A missing destination is installable. An existing destination marked with `specle_group` is updateable. An existing destination without that marker is protected and causes the command to fail before any planned copy occurs. The installer writes only `SKILL.md` files in the planned skill directories and does not alter `.agents/project/`, steering, or unrelated skills.

## Errors

Report clear CLI errors for an unknown skill, malformed or missing `specle_group` metadata, an unknown dependency, a dependency cycle, and a protected external active skill. Each error names the relevant skill and path. A failed preflight makes no copy.

## API and data

Use immutable records for source metadata and the resolved installation plan. Keep the source-root and target-root parameters injectable so tests can use temporary directories. The default source root comes from packaged `specle/skills` resources; the default target root is `.agents/skills` beneath the current working directory.

## Test strategy

Add focused tests for metadata extraction, dependency ordering, missing dependencies, cycles, protected external skills, managed-skill replacement, and no writes after a failed preflight. Add context/status tests for known kinds, unknown kebab-case kinds, and missing-kind records defaulting to `change`. Add CLI tests for `install` and `update` success and actionable failures. Run `pytest`, `ruff check`, `ruff format`, and `ty` through `uv` before verification.

## Non-goals

This change does not install or update project guidance or arbitrary external skills. It does not add a YAML parser or any external API integration.
