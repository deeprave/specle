---
name: review
specle_group: Quality
requires:
  - verify
description: >-
  Review verified implementations for quality and policy compliance.
usage: >-
  Use only after verification passes to assess implementation quality, guidance compliance, coverage, and security; it records approval or findings but does not implement fixes.
---

# Review a verified implementation

Review a verified Specle target against the repository's standards. This is a distinct quality
gate, not a substitute for verification or a client-specific pull-request workflow.

## Workflow

1. Read `.specle/context.json`, `.specle/current-issue.json`, `.agents/steering/{context,lifecycle,testing,review,delivery}.md`, and the relevant authoritative `.agents/project/` documents.
2. Select the target. By default it is the active current spec, which must have `status: "verified"`. A non-active target must be explicitly named and have `status: "verified"`; it never replaces the active current issue. A spike does not enter review; report its findings and optional outcome spec instead. If the selected implementation target is not verified, stop and direct the user to `verify` (or `verify <spec-name>`); do not run verification implicitly.
3. Read the target's `spec.md` and `tasks.md`, plus `requirements.md` and `design.md` when present. For abbreviated work, use its abbreviated verification contract in `spec.md`.
4. Get the target changes with `git diff` and `git diff --staged`. Scope the review to files named by the target's task plan or explicitly named by the user; do not treat unrelated working-tree changes as part of the target.
5. Check compliance with the portable steering policy and applicable project architecture, API, security, and test guidance. Evaluate correctness, readability, test coverage, security, and performance.

## Output

`APPROVE` or `REQUEST_CHANGES`, with specific, actionable findings (cite `file:line`) and a P1–P6 severity. Keep findings concrete; separate must-fix from nice-to-have.

After reporting, record raw findings in `.specle/specs/<target>/review-findings.json`. Add a source record for this review with a stable local identifier and revision or diff fingerprint. Each raw finding records its source ID, severity, description, evidence, state `new`, and empty decision and route fields. Then record the review outcome in `.specle/context.json` as required by `lifecycle.md`:

- `APPROVE` records review `pass` and changes the selected target to `approved`, with `next: "commit"`. `REQUEST_CHANGES` records the finding count and changes it to `review-findings`, with `next: "triage"`.
- For a named non-active target, update only its matching record and never change the active current issue. A re-reviewed committed target must retain its delivery reference for the later `commit` update.

## Next

After an `APPROVE`, stop for commit authorisation. After `REQUEST_CHANGES`, read `.agents/project/automation.md`; in `decision-gated` mode invoke `triage <spec-name>`, which collects user decisions and stops at its final summary.

- `triage` — decide how to handle review findings before addressing them.
- `commit` — deliver an approved change according to the project policy.
