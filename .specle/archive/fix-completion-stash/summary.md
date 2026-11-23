# Summary: Fix completion stash

## Summary

Completion and wrapup now preserve tracked working-tree changes without unnecessarily stashing virtual environments and generated caches.

## Outcome

The completion workflows avoid routine large stash restoration failures while retaining the normal Git protection for tracked local work.

## What changed

- Replaced `git stash --all` with plain `git stash` in completion and wrapup guidance.
- Documented the deliberate acceptance of the rare ignored-file collision risk.
