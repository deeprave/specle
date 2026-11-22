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
4. Read `[project].version` from `pyproject.toml` and compare it with the proposed version using PEP 440 semantics. If the proposed version is invalid, equal to, or lower, report both values and stop.
5. Confirm that `chore/release_<version>` does not already exist locally or remotely. If it exists, report it and stop; do not overwrite or reuse it implicitly.

## Prepare the release

1. Create and switch to `chore/release_<version>` from the configured delivery branch.
2. Update `[project].version` in `pyproject.toml` to the accepted version.
3. Run `uv run specle manifest src/specle/blueprints/manifest`.
4. Confirm that the command reports the proposed version. If it differs or fails, stop without committing.
5. Show the complete proposed commit contents, including all staged, unstaged, and untracked non-ignored files. Do not classify any change as unrelated or exclude it for that reason.
6. Request explicit user authorisation to commit. If declined, leave the branch and prepared changes untouched.
7. On authorisation, stage all tracked changes and all untracked non-ignored files with `git add -A`, then create one commit titled `chore: release <version>`.
