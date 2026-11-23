# Specle project layout

Specle separates stable, human-maintained guidance from agent-managed runtime state.

```text
.agents/
  skills/                         # Core Markdown skill inventory
  policies/                       # Package-owned generic Markdown policy
  steering/                       # Project-owned generic Markdown guidance
  project/                        # Project-specific Markdown guidance

.specle/
  .gitignore                       # Ignores worktree-local runtime selection/cache
  current-change                     # Ignored one-line selected change name
  changes/
    <change-slug>/                   # Active or queued self-contained change
  archive/
    <change-slug>/                   # Completed self-contained change
```

The Specle distribution inventory lives in `src/specle/blueprints/skills/` and
`src/specle/blueprints/policies/`. Installation copies those inventories into the target project's
`.agents/` directory; it does not replace `.agents/steering/` or `.agents/project/`.

Each skill blueprint declares a human-facing `specle_group`, concise `description`, detailed `usage`, and optional direct `requires` dependencies in its frontmatter. A non-empty `specle_group` is the single marker that identifies a Specle skill and supplies its inventory group. Specle validates declared dependencies and manages only the distributed inventory; unrelated installed skills are left untouched. The `specle` guide uses the generated installed inventory's group, description, and usage metadata to present available skills. See [FRONTMATTER.md](FRONTMATTER.md) for the complete metadata contract.

## `.agents/`

Guidance in `.agents/` is Markdown and remains human-maintained. The generated `skills/specle/index.json` resource is the deliberate machine-readable exception.

- `.agents/skills/` is the core skill inventory distributed and updated by Specle.
- `.agents/policies/` contains package-owned generic policy distributed and updated by Specle.
- `.agents/steering/` contains project-owned generic steering. Specle does not install, update, or remove it.
- `.agents/project/` contains project-specific documents referenced by skills. The onboarding skill creates or updates this directory; users manage it thereafter. Specle distribution updates must leave it untouched.

## `.specle/`

`.specle/` is the agent-managed runtime workspace. It can use a distinct commit, permission, or ignore policy from `.agents/`.

Every change directory owns a versioned `status.json`. It records its `kind` separately from lifecycle status. The initial kinds are `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`; unknown non-empty kebab-case kinds are preserved. Directory name is the stable identity; active versus archived location is the durable classification.

`.specle/current-change` is an ignored, one-line worktree-local selector. It is absent in a fresh clone until `activate` selects a normal change or spike. It is never committed, copied, or synchronised between worktrees. `context.json` is an optional ignored agent cache only; it has no Specle contract or lifecycle authority.

## JSON contracts

Agent-managed records that cross skill or external-system boundaries identify their versioned contract through a top-level `$schema` URI. Specle packages Draft 2020-12 schemas for change status, spike findings, tracker links, and the generated skill index. Their stable identifiers follow `specle://schemas/<contract>/1.0`; the package registry loads and validates them locally without assuming a source checkout or network retrieval.

Use `specle schemas export <destination>` to create a portable copy of every schema resource. The command refuses to replace an existing destination unless `--force` is explicit, stages the complete export first, and preserves the existing destination if replacement fails.
The exported `registry.json` maps each stable schema URI to its relative resource path; offline consumers can register those resources under the listed URIs before validating schemas with internal `$ref` values.

Active changes live in `.specle/changes/`; durably completed changes live in `.specle/archive/`. Each change has a self-contained directory named with its unique kebab-case slug. The slug is its stable identity.

Artifacts belonging to a change stay in that change's directory rather than in a top-level artifacts directory.

## Specification documents

Choose a format based on the type of information, not solely on whether an agent reads it.

Keep narrative authority in Markdown:

- `spec.md` for the condensed problem, scope, and intended behaviour.
- `requirements.md` for readable requirements and acceptance criteria.
- `design.md` for architecture, rationale, diagrams, APIs, and trade-offs.
- `tasks.md` for a human-reviewable implementation checklist.
- `estimate.md` when the estimate includes explanatory risks and dependencies.
- `summary.md` for a human-facing account of completed work, including an optional copy-ready external update. It is written only after the work item's lifecycle state is `complete`.

Use JSON for operational state that agents must update, query, compare, or validate mechanically:

- `metrics.json` for measurements.
- `status.json` for a change's durable kind, lifecycle state, progress, verification, review, delivery evidence, stable-name dependencies, and relationships.
- `estimate.json` only when estimates feed automated scheduling or prioritisation.
- `findings.json` for a spike's time-boxed investigation question, effort budget, findings, risks, recommendations, and optional outcome change.
- `review-findings.json` for source-aware review findings, triage decisions, and routes.
- `tracker-links.json` for external work-source links and the optional delivery destination for that change.
- A sidecar may include `relationships` with its origin stable change name, relationship type, and delivery mode. This is required before executing it alongside a selected origin. For concurrent delivery, both records declare `delivery: "with-related-change"`: the parent names the sidecar with `type: "bugfix"` or `"refactor"`, and the sidecar names the parent with `type: "origin"`. The optional `delivery` property is a non-empty string in the `change-status/1.0` schema. Only this reciprocal pair permits the parent to deliver and archive the sidecar with it.

## External work links

Project policy in `.agents/project/tracking.md` declares zero or more read sources and zero or one publish destination. The per-change operational record is `.specle/changes/<change-slug>/tracker-links.json`:

```json
{
  "$schema": "specle://schemas/tracker-links/1.0",
  "sources": [
    {
      "system": "github",
      "kind": "issue",
      "id": "owner/repository#123",
      "url": "https://github.com/owner/repository/issues/123"
    }
  ],
  "destination": null
}
```

Sources may be imported or checked for updates. Only the configured destination may receive published work information, and only after explicit user authorisation.

## Spike findings

An active spike is a `kind: "spike"` work item that records a bounded investigation rather than an implementation plan. Its change directory contains `findings.json`:

```json
{
  "$schema": "specle://schemas/findings/1.0",
  "question": "Should the installer support user-level skill directories?",
  "hypothesis": "A user-level installation can coexist with project-owned state.",
  "effort": "M",
  "scope": "Investigate installation layouts and client compatibility without implementation.",
  "status": "complete",
  "findings": [],
  "recommendations": [],
  "risks": [],
  "outcome_change": null
}
```

`effort` is an S/M/L/XL research budget, not a delivery estimate or due date. `outcome_change` is the stable name of a resulting normal change, bugfix, or refactor when one exists.

## Completed-work summaries

`summary.md` is a Markdown artifact within the completed change directory. It is deliberately human-facing, unlike a spike's agent-managed `findings.json`. It describes the outcome, evidenced verification and review where applicable, key decisions and limits, follow-up recommendations, and a concise update that can be adapted for an external system. Creating it does not change lifecycle state or publish anything externally.

## Review findings

`review-findings.json` belongs to the reviewed change directory. It retains source identity and revision data so triage can avoid re-recording unchanged review items while preserving their history. It contains a `sources` array and consolidated `items`; each item carries source references, evidence, P1–P6 severity, analysis, recommendation, duplicate relationship when applicable, and the eventual decision, route, execution mode, and dispatch result.
