---
name: changelog
description: >-
  Publish a completed Specle change summary as a dedicated GitHub wiki changelog page.
usage: >-
  Use when a completed change needs its summary generated and published as a page beneath the GitHub wiki Changelog; name a completed change to override the current issue.
---

# Publish a changelog entry

This is a Specle-project workflow, not a distributable Specle skill. It publishes the human-facing record for one already completed work item.

## Select and validate the target

1. Read `.specle/current-issue.json` and `.specle/context.json`. Without an explicit name, select the current issue. With a name, select that exact record from `current_spec` or `recent_specs`; do not choose a queued item implicitly.
2. Stop unless the selected record has `status: "complete"`. State the recorded next workflow if it is not complete. Do not infer completion or advance lifecycle state.
3. Read the selected work item's artifacts and use the `summary` skill to create or refresh `.specle/specs/<target>/summary.md`. Retain only evidenced verification and review results.

The generated summary remains in the working tree under the repository's ordinary delivery policy. Do not stage, commit, push, or otherwise change the source repository.

## Update the wiki changelog

1. Derive the GitHub wiki repository from the configured `origin` URL. Support standard HTTPS and SSH GitHub remotes only; if the origin is not a GitHub repository, explain that this project-local workflow cannot locate its wiki and stop before changing external state.
2. Clone the wiki into a fresh temporary directory. Require `Changelog.md` and `_Sidebar.md` to exist; do not create or replace unrelated top-level wiki navigation in this workflow.
3. Derive the change slug by removing the datetime prefix from `<target>`: for example, `202611171130-add-skill-blueprints` becomes `add-skill-blueprints`. The summary's wiki page is `<slug>.md`.
4. Copy the complete `summary.md` into `<slug>.md`, replacing only that page when it already exists. The page remains the human-readable record for that change.
5. Read the summary title, remove a leading `Summary:`, and ensure that both `_Sidebar.md` and `Changelog.md` link to the page. Add a nested sidebar item immediately beneath Changelog and a reverse-chronological landing-page entry under `## Changes` in this format:

   ```md
   - YYYY-MM-DD — [<summary title>](<slug>)
   ```

   Preserve all other sidebar and changelog entries. If the page and both links already exist, report that the change is already published and make no wiki commit.
6. Check the wiki change for whitespace errors, commit only `<slug>.md`, `Changelog.md`, and `_Sidebar.md` with `docs: add <target> changelog entry`, and push its default branch. Do not amend or force-push.

## Report

Report the published changelog entry and canonical wiki URL. If the workflow stopped, state which precondition failed and leave unrelated changes untouched.
