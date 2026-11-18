# Bugfix: handle forced replacement errors

## Bug

When `specle init <target> --force` encounters a filesystem failure while replacing a staged managed destination, the raw `OSError` escapes the CLI as a traceback.

## Expected behaviour

The command reports a concise `SkillInstallationError` that identifies the destination it could not replace. If a forced installation fails before it commits the complete distribution, every pre-existing managed skill directory, its resources, and the prior index remain available. Temporary staging and successfully restored backups are cleaned up where possible; an unrestored backup is retained and its recovery path is reported.

The workflow entrypoints explain that an explicit `next` instruction invokes the previously suggested next step automatically. The distributable source inventory is packaged under `src/specle/blueprints/`, with its portable `AGENTS.md`, `skills/`, and `steering/` together.

## Actual behaviour

`_replace_staged_destination()` originally called filesystem deletion and rename operations without translating their errors. The initial repair translates those errors, but then treats the `specle` skill specially to protect its nested index. Other skills may also carry resources and need the same failure guarantee.

## Reproduction

1. Initialise a target successfully.
2. Run a forced reinitialisation while a managed-destination deletion or rename raises `OSError`.
3. Observe an unhandled traceback instead of an actionable CLI failure, inject a failure while replacing any managed skill directory and observe its prior resources or the prior index disappear, or inject a rollback failure and observe its only recoverable backup disappear.

## Root cause and fix approach

The replacement phase needs destination-specific error handling and a resource-agnostic transaction. Stage every managed item, move existing destinations to temporary backups rather than deleting them, install staged replacements, and commit only after the index is installed last. On any pre-commit failure, restore every backup. If a restore operation fails, preserve that backup and report its path instead of deleting the remaining recoverable copy. Keep the package resources beneath one explicit blueprint root so installers cannot accidentally treat Python source as distributable content.

## Regression evidence

Add tests that inject failures while replacing both the index-hosting skill and another resource-bearing skill, assert the translated destination-specific error, and confirm every prior resource and the prior index are retained. Add a rollback-failure test that confirms the unrestored backup remains and the error reports its path.

Confirm the packaged resource resolver finds the moved blueprint inventory, and that the portable and active workflow entrypoints both define the `next` shortcut.
