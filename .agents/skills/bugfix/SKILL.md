---
name: bugfix
specle_group: Alternatives
description: >-
  Fix bounded defects with abbreviated test-first work.
usage: >-
  Use for a clear, bounded defect that needs a reproduction and regression test; use change when the work introduces new behaviour or broader scope.
lifecycle:
  accepts:
    - defined
    - planned
    - building
  creates:
    - defined
    - planned

---

# Bugfix (abbreviated TDD)

Resolve a defect with a lightweight, reproduce-first flow without displacing unrelated active work.

A change name MUST be Unicode NFC-normalised and consist of non-empty components of Unicode alphanumeric characters or Unicode combining marks, separated by single ASCII hyphens (`-`); leading, trailing, and repeated hyphens are invalid. The entire name MUST NOT be `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, or `LPT1`–`LPT9`, case-insensitively. A new slug SHOULD be verb-led, for example `fix-`, `add-`, or `create-`, but this is a recommendation rather than a validity requirement.

## Preparation-only hand-off

When `activate` invokes this skill for an existing named item in preparation-only mode, read its status and existing artifacts, fill only missing or incomplete kind-specific specification and task prerequisites, and return the result to `activate`. Do not create another record, select a change, alter delivery relationships, invoke `build`, or execute tasks in this mode. Report an actionable failure if the prerequisites cannot be established. The caller resumes activation on success; an explicit user-directed `prepare` invocation still stops after preparation.

When the user explicitly requests joint delivery of an existing named item with the selected normal change, re-read both records and establish the reciprocal relationship as one recoverable update under lifecycle policy. Do not infer this request from activation or overwrite a conflicting relationship.

## Workflow

Before applying or recording a lifecycle transition, consult this skill's `lifecycle` frontmatter declaration.

1. Read `.specle/current-change` when present and preserve its selected change; this workflow must not replace it.
2. Read the relevant authoritative `.agents/project/` documents, then understand the bug from the description and inspect the codebase to find the relevant area.
   If the user names an existing active bugfix, locate its matching `status.json` and read its `spec.md` and `tasks.md` when present, complete missing preparation from steps 3 and 5 without replacing existing artifacts or creating a new status record, and continue at step 6. Do not create another directory or status record.
3. Create a change folder `.specle/changes/<slug>/` with a short `spec.md`, using a slug unique across active and archived changes, containing:
   - Bug description.
   - Expected behaviour and actual behaviour.
   - Steps to reproduce, if inferable.
   - Root-cause analysis and fix approach.
   - Regression-test evidence to establish during the work.
4. Add a matching versioned `status.json` with `kind: "bugfix"`, `status: "defined"`, `created_at` set to current Unix seconds as a JSON number, `activated_at: null`, empty progress, `not-run` verification/review, `delivery: null`, and empty relationships/dependencies. Do not change `.specle/current-change`.
   When selected parent work exists and the user intends concurrent delivery, record a reciprocal relationship in both records as one recoverable mutation: the parent names this change with `type: "bugfix"` and `delivery: "with-related-change"`; this sidecar names the parent with `type: "origin"` and the same delivery value. If both records cannot be updated, stop with an actionable diagnostic; do not execute a half-linked sidecar. Otherwise, do not execute unlinked abbreviated work in that worktree and direct the user to `prepare` it for later named execution in a separate worktree.
5. Create `tasks.md` (test-first):
   - Write a failing test that reproduces the bug.
   - Implement the fix.
   - Confirm existing tests still pass.
6. Before implementation while active work exists, require the user to establish the explicit relationship in step 4; otherwise prepare the bugfix without implementation and direct later named execution in a separate worktree.
7. If the user asks to prepare the bugfix without implementation, update only the matching status to `planned` with current Unix-second `updated_at`, then report its generated change name and stop. Later `activate`, `build`, and `verify` requests must name that bugfix explicitly.
8. Otherwise, once preparation is complete, set a `defined` record to `planned` with current Unix-second `updated_at`, preserve a `building` record, then invoke `build <change-name>`; build owns task completion, progress, and the `building` transition.

## Critical

- Write the failing test **first**, then fix. A bug fix without a regression test is incomplete.
- Run the regression test and the project's documented quality gates.
- A bugfix is non-selected work. Never replace `.specle/current-change`.

## Next

- `activate <change-name>` — commence a prepared named bugfix.
- `build <change-name>` — resume implementation.
- `verify` — verify the named bugfix against this abbreviated contract and update its status without selecting it.

`build` owns progression to verification after implementation.
