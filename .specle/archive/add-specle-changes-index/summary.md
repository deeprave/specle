# Summary: Change listings and skill indexes

## Summary

Specle provides a concise view of active and archived changes and can regenerate an installed skill index independently of installation.

## Outcome

Developers can inspect change state and next actions in text, JSON, or CSV, and refresh an index from the installed managed skills.

## What changed

The listing reports valid change names, lifecycle context, dependencies, dates, and static diagnostics. Index regeneration reports lifecycle problems and supports an explicit override. Project directory preflight checks identify invalid path types, and S-sized normal changes can proceed without a design stage. Filesystem workflows use asynchronous AnyIO operations.

## Key decisions and limits

Index generation uses installed metadata, including valid local edits. Lifecycle issues block index regeneration unless explicitly overridden; the managed Specle skill must remain valid.
