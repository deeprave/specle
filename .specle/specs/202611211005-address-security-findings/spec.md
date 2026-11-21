# Address security findings

## Goal

Address the two accepted or varied findings in `.specle/report.json`: defer auto-merge credential use until the final privileged merge operation and ensure validation reads only regular resolved files.

## Scope

The change will refine the auto-merge workflow and validation input handling without changing the agreed Dependabot eligibility policy, trusted App bypass model, or support for user-chosen symlinked installation layouts. Installed-target integrity and blueprint lifecycle validation are independently specified by `support-blueprint-validate`.

## Decisions

The assessment is source analysis, not a durable workflow artifact. Its accepted and varied outcomes are fully translated into `requirements.md`; intentionally excluded proposals are recorded there as scope boundaries.

## Verification

Verify Dependabot metadata and required-check polling use the ordinary workflow token; the App token is created only for the final eligible, passing merge operation; and every validation read rejects a resolved non-regular file before reading it while accepting a symlink to a regular file. Run the project’s required Python quality gates and local Specle validation.
