---
name: wrapup
specle_group: Integration
requires:
  - complete
  - triage
description: >-
  Merge a recorded archival completion PR and synchronise delivery.
usage: >-
  Use after complete has archived a change and recorded an open completion PR; merge that PR or synchronise an externally merged one without changing the archive.
lifecycle:
  accepts:
    - complete
---

# Wrap up archival delivery

Finish the externally delivered archival finalisation for one archived completed change. This workflow never changes the archived record.

## Workflow

1. Read `.specle/current-change` when present, `.agents/policies/{lifecycle,delivery}.md`, applicable project delivery guidance, and the named or selected archived change's `status.json`.
2. Resolve the target under `.specle/archive/`. Require `status: "complete"` and a `delivery.completion` object containing the completion PR reference, head branch, target branch, and event. Do not infer a completion PR.
3. Inspect the recorded completion PR. If it has unresolved external feedback, report `triage <change-name>` and stop. If it is open but cannot merge or lacks required checks, report that external state and stop. If it is already merged, do not attempt another merge.
4. Require the checkout to be on the recorded completion target branch before changing Git state. If it is not, stop and report the expected branch; do not switch branches implicitly.
5. Before an authorised merge or synchronisation, preserve tracked, untracked, and ignored work in a named recoverable stash. If stashing fails, stop.
6. With explicit delivery authority, merge the open completion PR when necessary, fast-forward the target branch from upstream without reset or force operations, then restore the stash. If restoration fails, retain the stash and report recovery steps.
7. After successful merge and synchronisation, remove `.specle/current-change` only when it names this archived change. Do not write `status.json`, summary files, archive contents, commits, or pull requests.

## Boundaries

- Do not generate summaries, move change directories, alter archived records, or create a completion PR.
- Do not merge unresolved or failing completion PRs.
- Do not discard a failed stash restoration.

## Next

No lifecycle step remains after successful wrapup.
