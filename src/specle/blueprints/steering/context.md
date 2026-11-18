# Context State

`.specle/context.json` is the compact, current instance state for spec work. It is not the source
of lifecycle policy: `.agents/steering/lifecycle.md` defines the permitted states and transitions.
Every skill that reads or writes context must follow both documents.

## Active issue record

`.specle/current-issue.json` identifies the active specification:

```json
{
  "spec_path": ".specle/specs/YYYYMMDDHHMM-slug"
}
```

## Required shape

```json
{
  "$comment": "optional explanation",
  "current_spec": {
    "name": "YYYYMMDDHHMM-slug",
    "path": ".specle/specs/YYYYMMDDHHMM-slug",
    "kind": "change",
    "status": "defined",
    "progress": {"tasks_completed": 0, "tasks_total": 0},
    "present_task": null,
    "verification": {
      "status": "not-run",
      "last_run": null,
      "gates": {}
    },
    "review": {
      "status": "not-run",
      "last_run": null,
      "findings": 0
    },
    "revision_note": "short current-state summary"
  },
  "recent_specs": [],
  "queued_specs": [],
  "python_checks": {},
  "commit_policy": {},
  "requirements_summary": {},
  "skills": {}
}
```

## Field rules

- `current_spec.name` and `path` identify the active spec recorded in
  `.specle/current-issue.json`; keep them aligned.
- `kind` identifies the work independently of lifecycle `status`. The initial recognised kinds are
  `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`; preserve an unknown non-empty kebab-case kind rather
  than rejecting it.
- A missing `kind` in an existing current, queued, or recent record means `change`.
- `progress` counts top-level implementation tasks unless the task format explicitly says
  otherwise. Nested checkbox counts are not substituted for this lifecycle progress field.
- `verification.status` is one of `not-run`, `stale`, `pass`, `fail`, or `not-applicable`. `gates` holds the most
  recent concrete gate results. A spike uses `not-applicable`.
- `review.status` is one of `not-run`, `stale`, `pass`, `findings`, `resolved`, or `not-applicable`. `findings` is the number of
  actionable review findings from that pass. `resolved` means every current finding has a recorded terminal no-action disposition or completed dispatched follow-up; preserve the finding history in `review-findings.json` and set `findings` to `0`. A spike uses `not-applicable`.
- `recent_specs` is a compact historical record. Older records may omit `verification` and
  `review` details when that evidence was not retained.
- Each `queued_specs` record has `name`, `path`, `kind`, `status`, and `next`; it may also include
  `depends_on`, a list of short spec slugs. Recent records retain `kind` when known.
- Preserve project-wide `python_checks`, `commit_policy`, `requirements_summary`, and `skills`
  unless the relevant source changes.

## Update rules

- State must be valid JSON and concise; never paste full requirements or test output into it.
- Do not infer a lifecycle transition from checked task boxes alone. Record the transition only
  when the owning skill in `lifecycle.md` completes its work.
- When the active spec changes, retain the prior record in `recent_specs` if it is complete, or
  retain it in `queued_specs` if it is unfinished.
- When a queued abbreviated spec becomes complete, move only its record from `queued_specs` to
  `recent_specs`; never change `current_spec` or `.specle/current-issue.json` for that transition.
- `context` refreshes known evidence without inventing verification or review results.
