# Summary: Rename changelist to changes

## Summary

The pending-work inventory skill is now named `changes`, giving the command the same concise language used throughout Specle’s change workflow.

## Outcome

Users can invoke `changes` to inspect pending and dependency-context work. The installed skill, distributable blueprint, and generated inventory all resolve that name consistently.

## What changed

- Renamed the installed and blueprint skill directories and metadata.
- Updated lifecycle, status, and public workflow references.
- Added inventory coverage that prevents the former `changelist` name from returning.
