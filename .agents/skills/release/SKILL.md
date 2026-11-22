---
name: release
description: >-
  Prepare a repository release commit after confirming no active change or open pull request remains.
usage: >-
  Use with an optional proposed version to prepare a release branch, version update, manifest, and authorised release commit.
---

# Prepare a release

Prepare one authorised release commit.

It does not push, open or update a pull request, tag, publish, or create a release.

## Preflight

Perform every preflight check before changing files or creating a branch.

1. Check for an active selected change. If one exists, report it and stop. Unselected queued changes do not block a release.
2. Query GitHub for open pull requests, including drafts. If any exists, report its number and URL and stop.
3. Take an optional version from the user. If absent, request one through client elicitation when available, otherwise ask plainly.
4. Read `[project].version` from `pyproject.toml`. Validate and normalise the proposed version with PEP 440 semantics, then reject it if the canonical form is invalid for the manifest. If it is equal to or lower than the current version, report both values and stop.
5. Confirm that `chore/release_<canonical-version>` does not already exist locally or remotely. If it exists, report it and stop; do not overwrite or reuse it implicitly.

## Prepare the release

1. Fetch, switch to, and fast-forward the configured delivery branch from its upstream. If it cannot synchronise cleanly, stop.
2. Create and switch to `chore/release_<canonical-version>`.
3. Update `[project].version` in `pyproject.toml` to the canonical version.
4. Run `uv run specle manifest src/specle/blueprints/manifest`.
5. Confirm that the command reports the canonical version. If it differs or fails, stop without committing.
6. Show the complete proposed commit contents, including all staged, unstaged, and untracked non-ignored files. Do not classify any change as unrelated or exclude it for that reason.
7. Request explicit user authorisation to commit. If declined, leave the branch and prepared changes untouched.
8. On authorisation, stage all tracked changes and all untracked non-ignored files with `git add -A`, then create one commit titled `chore: release <canonical-version>`.
