---
name: summary
specle_group: Reporting
requires: []
description: >-
  Summarise completed Specle work for people.
usage: >-
  Use only after work is complete to create a human-facing report and copy-ready update; it does not publish externally.
---

# Summarise completed work

Produce `summary.md` as a useful human account of completed work. It is a communication artefact, not an AI verification record and not an external publication.

## Workflow

1. Read `.specle/context.json`, `.specle/current-issue.json`, relevant steering, and applicable project guidance. Select the active work item by default. A non-active completed item in `recent_specs`, of any kind, must be explicitly named.
2. Apply the state guard before writing anything. The selected record must have `status: "complete"`. Otherwise, stop and identify the owning next workflow. Do not imply completion, run verification or review, or change lifecycle state.
3. Read the target's evidence in full:
   - For normal work, read its requirements, design, task plan, verification evidence, review outcome, and the relevant implementation.
   - For a bugfix or refactor, read its abbreviated `spec.md`, task plan, verification evidence, review outcome, and the relevant implementation.
   - For a spike, read `findings.json`, including recommendations, risks, and `outcome_spec`.
4. Write `.specle/specs/<target>/summary.md`. Make it stand on its own for people who have not followed the workflow. Use this structure, omitting sections that do not apply:

   ```md
   # Summary: <plain-language title>

   ## Outcome

   ## What changed

   ## Evidence

   ## Key decisions and limits

   ## Recommendation and follow-up

   ## Copy-ready update
   ```

   Explain what was delivered or learned in clear language. For implementation work, include only evidenced verification and review results; do not claim that a quality gate passed without the recorded evidence. For a spike, foreground the recommendation and link its outcome spec when one exists. The copy-ready update should be a short standalone paragraph suitable for a Jira comment, pull-request description, release note, or similar channel.
5. Preserve every context, lifecycle, tracker, and review record. Do not post or publish the summary. External publication remains an explicit `track` operation when a project has a configured destination and the user authorises it.

## Next

- Share or adapt the copy-ready update when the user asks.
- `track` — publish only with explicit authorisation and a configured destination.
