# Specle project layout

Specle separates stable, human-maintained guidance from agent-managed runtime state.

```text
.agents/
  skills/                         # Core Markdown skill inventory
  steering/                       # Generic Markdown guidance for every project
  project/                        # Project-specific Markdown guidance

.specle/
  .gitignore                       # Ignores worktree-local runtime selection/cache
  current-spec                     # Ignored one-line selected spec name
  specs/
    YYYYMMDDHHMM-<spec-slug>/      # Active or queued self-contained specification
  archive/
    YYYYMMDDHHMM-<spec-slug>/      # Completed self-contained specification
```

The Specle distribution inventory lives in `src/specle/blueprints/skills/` and
`src/specle/blueprints/steering/`. Installation copies those inventories into the target project's
`.agents/` directory; it does not replace `.agents/project/`.

Each skill blueprint declares a human-facing `specle_group`, concise `description`, detailed `usage`, and optional direct `requires` dependencies in its frontmatter. A non-empty `specle_group` is the single marker that identifies a Specle skill and supplies its inventory group. Specle validates declared dependencies and manages only the distributed inventory; unrelated installed skills are left untouched. The `specle` guide uses the generated installed inventory's group, description, and usage metadata to present available skills. See [FRONTMATTER.md](FRONTMATTER.md) for the complete metadata contract.

## `.agents/`

Guidance in `.agents/` is Markdown and remains human-maintained. The generated `skills/specle/index.json` resource is the deliberate machine-readable exception.

- `.agents/skills/` is the core skill inventory distributed and updated by Specle.
- `.agents/steering/` contains generic steering documents distributed and updated by Specle.
- `.agents/project/` contains project-specific documents referenced by skills. The onboarding skill creates or updates this directory; users manage it thereafter. Specle distribution updates must leave it untouched.

## `.specle/`

`.specle/` is the agent-managed runtime workspace. It can use a distinct commit, permission, or ignore policy from `.agents/`.

Every spec directory owns a versioned `status.json`. It records its `kind` separately from lifecycle status. The initial kinds are `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`; unknown non-empty kebab-case kinds are preserved. Directory name is the stable identity; active versus archived location is the durable classification.

`.specle/current-spec` is an ignored, one-line worktree-local selector. It is absent in a fresh clone until `activate` selects a normal spec. It is never committed, copied, or synchronised between worktrees. `context.json` is an optional ignored agent cache only; it has no Specle contract or lifecycle authority.

## JSON contracts

Agent-managed records that cross skill or external-system boundaries identify their versioned contract through a top-level `$schema` URI. Specle packages Draft 2020-12 schemas for spec status, spike findings, tracker links, and the generated skill index. Their stable identifiers follow `https://github.com/deeprave/specle/schemas/<contract>/1.0`; the package registry loads and validates them without assuming a source checkout.

Use `specle schemas export <destination>` to create a portable copy of every schema resource. The command refuses to replace an existing destination unless `--force` is explicit, stages the complete export first, and preserves the existing destination if replacement fails.
The exported `registry.json` maps each stable schema URI to its relative resource path; offline consumers can register those resources under the listed URIs before validating schemas with internal `$ref` values.

Active specifications live in `.specle/specs/`; durably completed specifications live in `.specle/archive/`. Each specification has a self-contained directory named `YYYYMMDDHHMM-<spec-slug>`. The complete directory name is its stable identity and the date-time prefix provides ordering.

Artifacts belonging to a specification stay in that specification's directory rather than in a top-level artefacts directory.

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
- `status.json` for a specification's durable kind, lifecycle state, progress, verification, review, delivery evidence, stable-name dependencies, and relationships.
- `estimate.json` only when estimates feed automated scheduling or prioritisation.
- `findings.json` for a spike's time-boxed investigation question, effort budget, findings, risks, recommendations, and optional outcome spec.
- `review-findings.json` for source-aware review findings, triage decisions, and routes.
- `tracker-links.json` for external work-source links and the optional delivery destination for that specification.
- A sidecar may include `relationships` with its origin stable spec name, relationship type, and delivery mode. This is required before executing it alongside a selected origin.

## External work links

Project policy in `.agents/project/tracking.md` declares zero or more read sources and zero or one publish destination. The per-spec operational record is `.specle/specs/YYYYMMDDHHMM-<spec-slug>/tracker-links.json`:

```json
{
  "$schema": "https://github.com/deeprave/specle/schemas/tracker-links/1.0",
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

An active spike is a `kind: "spike"` work item that records a bounded investigation rather than an implementation plan. Its spec directory contains `findings.json`:

```json
{
  "$schema": "https://github.com/deeprave/specle/schemas/findings/1.0",
  "question": "Should the installer support user-level skill directories?",
  "hypothesis": "A user-level installation can coexist with project-owned state.",
  "effort": "M",
  "scope": "Investigate installation layouts and client compatibility without implementation.",
  "status": "complete",
  "findings": [],
  "recommendations": [],
  "risks": [],
  "outcome_spec": null
}
```

`effort` is an S/M/L/XL research budget, not a delivery estimate or due date. `outcome_spec` is the path of a resulting normal spec, bugfix, or refactor when one exists.

## Completed-work summaries

`summary.md` is a Markdown artefact within the completed spec directory. It is deliberately human-facing, unlike a spike's agent-managed `findings.json`. It describes the outcome, evidenced verification and review where applicable, key decisions and limits, follow-up recommendations, and a concise update that can be adapted for an external system. Creating it does not change lifecycle state or publish anything externally.

## Review findings

`review-findings.json` belongs to the reviewed spec directory. It retains source identity and revision data so triage can avoid re-recording unchanged review items while preserving their history. It contains a `sources` array and consolidated `items`; each item carries source references, evidence, P1–P6 severity, analysis, recommendation, duplicate relationship when applicable, and the eventual decision, route, execution mode, and dispatch result.
