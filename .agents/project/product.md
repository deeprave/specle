# Product guidance

Specle serves developers who need lightweight governance and workflow support while adding features and fixing bugs in their own projects.

Specle provides reusable AI-agent skills, human-readable steering documents, and a small Python management script for installing and updating those skills.

Specle must remain reusable across projects of all types. It must not prescribe a project's framework, hosting service, issue tracker, or other project-specific development choices.

## Inventory changes

Never add a skill to `.agents/skills/` or `src/specle/blueprints/skills/` unless the user explicitly requests that specific skill. Do not infer, propose through implementation, or silently install a skill for any reason.
