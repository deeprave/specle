# Bugfix: use narrow completion stashes

## Bug

`complete` and `wrapup` instruct agents to run `git stash --all`. That captures ignored virtual environments and generated caches, making restoration noisy and prone to failure even when the meaningful local work is intact.

## Expected and actual behaviour

Completion should preserve tracked local work before branch changes without shuffling ignored caches or virtual environments. The current instructions preserve every ignored file and can fail restoring them over existing generated state.

## Reproduction

Run completion in a repository with an existing ignored `.venv` and caches. `git stash --all` captures them, and later restoration reports existing files and retains the stash.

## Root cause and fix approach

The workflow over-prioritises a rare ignored-file collision over routine local generated state. Replace `git stash --all` with plain `git stash` in complete and wrapup, and align the lifecycle guidance with tracked-work preservation.

## Regression evidence

This is a workflow-instruction correction, not production code. Validate matching blueprint and installed copies and run the existing Markdown and Specle validation gates; do not add workflow-prose tests.
