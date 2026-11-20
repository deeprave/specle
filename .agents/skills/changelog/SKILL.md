---
name: changelog
description: >-
  Publish a completed Specle change summary as a dedicated GitHub wiki changelog page.
usage: >-
  Use with a named completed archived change to publish its existing summary as a page beneath the GitHub wiki Changelog.
---

# Publish a changelog entry

This is a Specle-project workflow, not a distributable Specle skill. It publishes the human-facing record for one already completed work item.

## Select and validate the target

1. Require an explicit stable spec name. Resolve that exact name in `.specle/archive/`; do not use `.specle/current-spec` or choose an active item implicitly.
2. Stop unless the selected record has `status: "complete"`. State the recorded next workflow if it is not complete. Do not infer completion or advance lifecycle state.
3. Read the selected work item's artifacts and its existing `.specle/archive/<target>/summary.md`. Stop if the summary is absent; direct the user to explicitly invoke `summary <target>` and deliver that source-repository change before publishing.

Do not invoke `summary`, refresh an existing summary, or otherwise change the source repository. Summary generation and refresh are separate source-repository changes under the ordinary delivery policy.

## Update the wiki changelog

1. Derive the GitHub wiki repository from the configured `origin` URL. Support standard HTTPS and SSH GitHub remotes only; if the origin is not a GitHub repository, explain that this project-local workflow cannot locate its wiki and stop before changing external state.
2. Clone the wiki into a fresh temporary directory. Require `Changelog.md` and `_Sidebar.md` to exist; do not create or replace unrelated top-level wiki navigation in this workflow.
3. Derive the change slug by removing the datetime prefix from `<target>`: for example, `202611171130-add-skill-blueprints` becomes `add-skill-blueprints`. The summary's wiki page is `<slug>.md`.
4. Read the summary title, remove a leading `Summary:`, and inspect `<slug>.md`, `_Sidebar.md`, and `Changelog.md`. If the page already exists and both navigation files already link to it, report that the change is already published and stop without modifying the wiki checkout.
5. Copy the complete `summary.md` into `<slug>.md`, replacing only that page when it already exists. The page remains the human-readable record for that change. Ensure that both `_Sidebar.md` and `Changelog.md` link to the page. Add a nested sidebar item immediately beneath Changelog and a reverse-chronological landing-page entry under `## Changes` in this format:

   ```md
   - YYYY-MM-DD — [<summary title>](<slug>)
   ```

   Preserve all other sidebar and changelog entries.
6. Check the wiki change for whitespace errors, commit only `<slug>.md`, `Changelog.md`, and `_Sidebar.md` with `docs: add <target> changelog entry`, and push its default branch. Do not amend or force-push.

## Report

Report the published changelog entry and canonical wiki URL. If the workflow stopped, state which precondition failed and leave unrelated changes untouched.
