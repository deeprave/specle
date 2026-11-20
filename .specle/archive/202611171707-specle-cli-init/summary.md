# Summary: Initialise the complete Specle skill distribution

## Outcome

Specle now provides an explicit `specle init <target-directory> [--force]` command for installing its complete shared skill and steering distribution into a chosen target's `.agents/` directory. The command never infers the current directory and leaves project-owned `.agents/project/` and `.specle/` content untouched.

## What changed

- Replaced the earlier individual-skill workflow with target-oriented distribution initialisation.
- Added discovery and validation for the complete packaged skill and steering inventories.
- Generated `skills/specle/index.json` during successful initialisation, grouping installed Specle skills with their descriptions, usage guidance, and resource locations.
- Added preflight collision detection and a `--force` path that replaces only managed destinations.
- Made forced replacement transactional: existing managed content is backed up, restored after a failed replacement, and retained with a recovery path if restoration itself fails.
- Moved the distributable source assets under `src/specle/blueprints/`, containing the portable workflow entrypoint, skills, and steering documents together.

## Evidence

The recorded CLI-initialisation verification passed the project's pytest, Ruff check, Ruff format, Ty, and wheel-resource gates. Local review identified the replacement-failure safety gap; it was addressed by the completed `handle-forced-replacement-errors` bugfix, whose verification and review both passed.

## Key decisions and limits

Initialisation distributes only Specle-managed skills and steering documents. It does not install project guidance, runtime state, a root `AGENTS.md`, a shell launcher, client integrations, or symlinks. Standalone `index` and `update` commands remain separate future work.

## Recommendation and follow-up

Use `specle init <target-directory>` to establish a new shared skill inventory, adding `--force` only when deliberately replacing existing managed destinations. Address the separately queued schema-versioning and delivery-policy changes before adding further CLI commands.

## Copy-ready update

Specle now has an explicit, safe `init` command that installs the complete skills and steering distribution into a chosen target, generates its skill index, preserves project-owned state, and handles forced replacement failures transactionally. Update and standalone index commands remain planned follow-up work.
