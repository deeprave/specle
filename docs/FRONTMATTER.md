# Skill frontmatter

This reference describes the constrained frontmatter used by package-owned Specle skills in `src/specle/blueprints/skills/` and by their managed installed copies. It is parsed with StrictYAML; unsupported keys, scalar/list substitutions, and unsupported lifecycle vocabulary are invalid.

## Common fields

| Key | Required | Meaning |
| --- | --- | --- |
| `name` | Yes | Kebab-case skill name, matching its directory. |
| `specle_group` | Yes | Non-empty inventory group and the marker that identifies a managed Specle skill. |
| `description` | Yes | Concise, trigger-oriented summary. |
| `usage` | Yes | More detailed instruction on when to apply the skill. |
| `requires` | No | Directly required installed skills. Omit it when there are none. |
| `lifecycle` | Lifecycle owners | Structured lifecycle authority used by agents and `specle validate`. |

`requires` is a block sequence and describes direct availability only. It does not describe lifecycle progression.

```yaml
requires:
  - verify
```

## Lifecycle declarations

A lifecycle-owning skill declares only the authority it holds:

- `accepts`: statuses it may operate on.
- `creates`: statuses it may create without a preceding transition.
- `transitions`: state edges owned by the skill.
- `terminal`: statuses the skill can establish as terminal.

Use a compact status scalar for the ordinary case:

```yaml
lifecycle:
  accepts:
    - defined
  transitions:
    - from: defined
      to: estimated
      next: design
```

Use a nested selector only when a state needs a kind or scope constraint:

```yaml
lifecycle:
  transitions:
    - from:
        status: planned
        kind: bugfix
        scope: queued
      to: building
      next: verify
```

Both `from` and `to` accept either form. `next` is the next skill name or is omitted for a terminal outcome.

The supported statuses are `defined`, `estimated`, `designed`, `planned`, `spiking`, `building`, `verified`, `approved`, `committed`, `review-findings`, `triaged`, `complete`, and `cancelled`. Nested selectors may use the kinds `change`, `bugfix`, `refactor`, and `spike`, and the scopes `active`, `queued`, and `committed`.

The declaration is agent-visible production metadata. Before a skill records a lifecycle transition, its instructions require the agent to consult and obey its own declaration. The skill body remains the full operational procedure; this metadata is the constrained transition contract that `specle validate` audits.
