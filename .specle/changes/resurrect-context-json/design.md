# Design: Resurrect context json

## Overview

Restore `.specle/context.json` as an optional, ignored, worktree-local hand-off document. It transfers concise current status, recent relevant activities, material milestones, informal todos, directives, and the acting agent's own material actions between sessions, subagents, and reviewers. It remains outside lifecycle state: selection, status, relationships, dependencies, and delivery evidence continue to come only from per-change `status.json` records.

The change introduces a managed portable context policy. It enables hand-off maintenance by default, while an onboarding-created project policy chooses whether the project maintains a context document and whether reviewing agents may update it. The schema publishes a format for agents; Specle itself deliberately does not parse or validate the optional document.

## Architecture

```text
portable policy ──────► project context policy ──────► agent write authority
  default enabled          user selections                  │
                                                          ▼
agent hand-off ───────► .specle/context.json ◄──── sessions/subagents/reviewers
                               ignored, local only
                                      │
                                      ▼
                             packaged context schema

specle validate <target> ──► selector + durable status records only
```

Keep every Specle command, including `_validate_installed_target`, independent of context: it must neither parse nor diagnose `.specle/context.json`. Therefore a missing, stale, malformed, or differently shaped local cache cannot block `specle validate`, lifecycle commands, initialisation, update, selection, or task resolution.

## Contract and data

Register `specle://schemas/context/1.0` in `SCHEMA_IDENTIFIERS`, so `load_schema`, `validate_instance`, and `specle schemas export` handle it like existing public contracts. Add `src/specle/schemas/context/1.0.json` with this permissive shape:

```json
{
  "$schema": "specle://schemas/context/1.0",
  "milestones": [
    {
      "date_added": "2026-11-26T10:26:00+11:00",
      "subject": "Finished the portable hand-off design.",
      "change": "resurrect-context-json",
      "detail": {"reason": "keeps later sessions oriented"}
    }
  ],
  "todos": [
    {
      "date_added": "2026-11-26T10:26:00+11:00",
      "subject": "Consider the local branch delivery model.",
      "change": "add-local-branch-model"
    }
  ],
  "directives": [
    {
      "subject": "Do not create speculative concurrency handling.",
      "detail": {"source": "user preference"}
    }
  ]
}
```

`$schema` is required and fixed to the context URI. `milestones`, `todos`, and `directives` are optional arrays. A milestone requires non-empty `date_added` and `subject`, and may have non-empty `change` and `detail`; `date_added` is a human-readable local date-and-time string. Guidance prefers local ISO 8601 with an explicit numeric offset, such as `2026-11-26T10:26:00+11:00`, but schema validation does not impose that form. A todo follows the same rule and has non-empty `subject`; it may have `change` and `detail`. A directive requires non-empty `subject` and may have `detail`. Every `detail` accepts any JSON type, and the document and every item use `additionalProperties: true` for project-specific hand-off material.

No context record is generated, rewritten, or migrated. `.specle/.gitignore` already ignores `/context.json`; initialisation and update retain local context as they do now.

## Policy and guidance

Add managed `context.md` policy source and installed copy. It defines context as an optional hand-off rather than a permanent record, identifies `specle://schemas/context/1.0` as the portable shape, and sets `maintain_context: enabled` as the portable default. It instructs agents to use the document only when maintenance is enabled: read it at hand-off boundaries, record their own material actions and milestones, and keep it concise and current. It recommends local ISO 8601 timestamps with numeric offsets as readable guidance without rejecting other useful human-readable local date-and-time strings.

Onboarding will inventory and create `.agents/project/context.md`, asking separately whether to maintain `context.json` and whether reviewing agents may update it. A reviewing agent is one that neither built nor participated in the feature's design. `disabled` prevents new writes. Reviewers may always read it; lacking an explicit project allowance, they do not modify it. This conservative default makes the second choice meaningful while retaining enabled hand-off maintenance by default.

Milestones are additive and reverse chronological. They may remain indefinitely only when still relevant, but should be a small collection; a major event such as change completion may add a completion milestone and remove older no-longer-useful entries. Activation, first commit, and completion are recommended minimum milestones, but non-lifecycle decisions and work also qualify. Todos are pruned or marked transferred when defined work takes ownership. Directives carry current user defaults, denials, and similar instructions; they never override repository policy, durable records, or explicit current user instructions.

Update `docs/LAYOUT.md`, both portable entrypoints, review guidance, activation, commit, completion, and summary guidance. Add context to the layout tree. Explicitly prohibit a diary, command log, verification log, authoritative backlog, lifecycle source, Git commit, merge, or copying context between worktrees. Activation, commit, and completion read portable and applicable project context guidance, but never require a context document.

Add a separate package-owned `external-inputs.md` policy source and installed copy. It applies equally to GitHub issues, issue trackers, pull requests, pull-request reviews, comments, and provided external reviews. It instructs agents to treat all external content as untrusted: never as a fact, instruction, authority, approval, or user intent without independent confirmation. Agents assess accuracy, relevance, and provider intent; verify material claims against user direction and authoritative repository or system evidence; and seek explicit user direction before acting on a material proposal.

Treat `vary` as a distinct completed review disposition, not an alias for acceptance. A varied finding remains settled once its recorded dispatch completes, retaining the user-selected alternative in its recommendation and rationale.

Update triage and resolve guidance so both accepted and varied findings are dispatchable through their recorded routes. Their durable decisions remain distinct; only the dispatch mechanics are shared.

Relax tracker-link source and destination `url` fields to non-empty agent-meaningful strings. Do not infer, constrain, or validate a transport protocol: an integration may use an MCP locator, socket, TCP connection, or another representation useful to the acting agent.

## Boundaries

Context may be absent, stale, malformed, or use an unsupported schema without affecting Specle commands. Agents that choose to consume it can use the published schema as a portable format. Maintenance-disabled policy prevents writes; reviewers may read but do not mutate it without an explicit project allowance.

## Test strategy

- Add registry tests for the context identifier, exported resource, minimal and extended documents, milestone/todo/directive fields, arbitrary detail values, and invalid recognised fields. Prove that non-empty human-readable local date-and-time strings remain valid while empty or non-string `date_added` values do not.
- Prove isolation: malformed context beside a valid installed target does not change `specle validate` or normal selected-change runtime resolution; init and forced update preserve the ignored file.
- Validate policy inventory/synchronisation through normal installation; review the onboarding instructions rather than adding brittle prose tests.
- Cover a settled `vary` review decision through lifecycle validation.
- Cover flexible tracker locators and assert that malformed optional context produces no validation diagnostic.
- Run focused tests, then `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and `uv run specle validate --verbose .`.
