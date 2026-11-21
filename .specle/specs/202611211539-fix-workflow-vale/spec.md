# Bugfix: keep the Vale report in document validation

## Bug description

The non-fork Vale job uses Reviewdog's `github-pr-check` reporter. It creates a second standalone `vale` Check Run in addition to the Document validation job. GitHub associates that generated report with the Test workflow's check suite, so the workflow graph misleadingly shows `vale` in both blocks.

## Expected behaviour

Vale runs once as the `vale` job in Document validation. Its findings are surfaced as annotations on that job, and `fail_level: any` continues to fail the job. Test and Verify retain only their Python quality jobs.

## Actual behaviour

The action executes in Document validation, but its separate Reviewdog Check Run is displayed with Test because the reporter creates an unscoped check for the same commit.

## Root cause and fix approach

The non-fork job selects `github-pr-check`, which creates the standalone report. Use `github-pr-annotations`, matching the fork-safe job, so Reviewdog reports through the running Document validation job instead.

## Regression evidence

Inspect the workflow to confirm both Vale paths use `github-pr-annotations`, retain `fail_level: any`, and do not introduce a Vale job or Verify dependency in `test.yml`. Workflow configuration is inspected directly; repository policy excludes tests for declarative workflows.
