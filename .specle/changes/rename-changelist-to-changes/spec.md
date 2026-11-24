# Bugfix: rename changelist to changes

## Bug

The pending-work inventory skill is named `changelist`, while its purpose is to show changes. The name is inconsistent with the repository's change terminology and with the concise command users should invoke.

## Expected behaviour

The inventory command is named `changes`. The installed skill and its source blueprint resolve under that name, the skill inventory advertises it, and all workflow guidance directs users to `changes` when they need the pending-work inventory.

## Actual behaviour

The command is exposed as `changelist` through `.agents/skills/changelist/`, its blueprint counterpart, and the skill index. Lifecycle, status, and public lifecycle documentation also refer to `changelist`.

## Reproduction

Inspect the installed skills or skill index and invoke the pending-work inventory by its documented name. The available command is `changelist`, not `changes`.

## Root cause and fix approach

The skill was introduced with a longer command name and its references were propagated into the distributed and source copies. Rename the installed and blueprint skill directories to `changes`, update the skill metadata and generated inventory entry, then replace command references across installed policy and skills, their source blueprints, and lifecycle documentation. References to the `.specle/changes/` filesystem directory are not command references and must remain unchanged.

## Regression evidence

Confirm the installed skill and source blueprint both resolve as `changes`, no managed command references still advertise `changelist`, and the generated skill inventory names `changes`. Validate the changed distributed artifacts with the repository's normal documentation and Specle checks; do not add literal-prose tests.
