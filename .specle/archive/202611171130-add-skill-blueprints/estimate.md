# Complexity estimate: add skill blueprints

## T-shirt size

**M**

## Breakdown

- **New files:** approximately 2–4 for focused CLI tests and any metadata or installation helpers.
- **Modified files:** approximately 20–25, including the management CLI, package resources, every skill blueprint's frontmatter, and affected inventory guidance.
- **Estimated tasks:** 6–8 test-first tasks covering ownership metadata, dependency inspection, protected installation, idempotent updates, and user-facing CLI output.

## Key risks

- Direct dependencies must be distinguished from optional next steps without inventing a brittle dependency model from prose alone.
- Ownership metadata must protect externally installed skills while allowing Specle-managed skills to be installed and updated predictably.
- Installation must copy only the requested skill and leave unrelated active skills and `.agents/project/` guidance untouched.
- The packaged wheel must continue to include every Markdown resource needed for installation and update operations.

## Confidence

**Medium.** The source inventory and active destination are established, but the management script has only an initial CLI scaffold and does not yet define metadata, dependency, or copy interfaces.

## Recommendation

Run `design` before creating implementation tasks. The design should define ownership and dependency representations, source-to-destination installation rules, update behaviour, and how the CLI reports missing dependencies or protected external skills.

## Similar past work

No prior Specle implementation specs exist.
