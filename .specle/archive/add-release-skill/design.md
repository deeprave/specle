# Design: Add release skill

## Overview

Add one project-owned `.agents/skills/release/SKILL.md`. It describes a guarded, interactive release-preparation workflow; it is not copied to `src/specle/blueprints/` and is therefore absent from managed installations and manifests.

## Architecture

```text
user version (or elicitation)
        |
read-only preflight ──> selected change / open PR? ──> report and stop
        |
canonical version and manifest-format validation
        |
fetch and synchronise delivery branch
        |
create chore/release_<canonical-version> branch
        |
update pyproject.toml ──> uv run specle manifest src/specle/blueprints/manifest
        |                         |
        |                         +── reported version differs? ──> stop
        v
show git diff / full commit candidate
        |
explicit user approval ──> git add -A && release commit
```

## API / data

- Read the existing project version from `[project].version` in `pyproject.toml`.
- Use `packaging.version.Version` semantics for parsing and ordering the supplied version. Convert the accepted value to its canonical string form before any later operation.
- Validate that canonical form against the manifest version grammar before branch creation; reject values the manifest cannot represent.
- The release manifest remains `src/specle/blueprints/manifest`; invoke `uv run specle manifest src/specle/blueprints/manifest` after the metadata update.
- Require the command's reported version to equal the canonical release version. This confirms that `specle.__version__`, sourced through `importlib.metadata`, sees the updated distribution metadata before the manifest is committed.
- Query GitHub for open pull requests. Treat any returned open PR, including drafts, as a blocker.
- Fetch and fast-forward the configured delivery branch from upstream before creating the release branch. Stop if it cannot be synchronised cleanly.

## Error handling

| Condition | Behaviour |
| --- | --- |
| `.specle/current-change` selects work | Report its name and stop before edits or branch creation. |
| An open GitHub PR exists | Report the PR and stop before edits or branch creation. |
| Missing, invalid, equal, or lower version | Explain the comparison and stop without changes. |
| Canonical version is unsupported by the manifest | Report the unsupported value and stop before branch creation. |
| Delivery branch cannot synchronise with upstream | Stop before release-branch creation and report the Git recovery needed. |
| Manifest command reports another version or fails | Stop without a commit; retain the release branch and ordinary working-tree changes for user inspection. |
| Branch already exists | Stop and ask the user whether to resume or choose another release version; do not overwrite it. |
| User declines the displayed commit | Leave the release branch and prepared files unchanged; do not stage or commit. |

## Output

The skill reports each preflight result, the accepted version transition, manifest command outcome, branch name, and the complete candidate commit contents. It does not claim publication or delivery.

## Test strategy

This change adds Markdown workflow guidance only. Review the skill against its acceptance criteria and project delivery policy, ensure it remains absent from blueprint and managed-inventory paths, then run the established quality gates that apply to the repository.
