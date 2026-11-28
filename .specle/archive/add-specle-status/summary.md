# Summary: Specle status command

## Summary

Specle now provides a concise status command for the selected change, locally active sidecars, Git worktree and optional hand-off context.

## Outcome

Developers and tools can see current work without changing it, using plain-text or Markdown output.

## What changed

`specle status` displays change and sidecar lifecycle state and dates, worktree counts, and grouped context milestones, todos and other lists. The status skill presents the same information. Context dates are parsed into calendar dates when possible. Git inspection avoids optional index updates.

## Key decisions and limits

Sidecar activity comes from the local registry. Status does not validate the selector or list changed paths.
