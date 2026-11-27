# Summary: Remove dead code

## Summary

Specle now detects unused production code locally before review and no longer retains the unreachable helpers that prompted the check.

## Outcome

The production package exposes only code required by its command-line behaviour. Vulture runs as a host-provided pre-commit hook at the confidence level that identifies unused functions, without a whitelist.

## What changed

- Removed the unreachable inventory, lifecycle, timestamp, change-state, and sidecar helper code.
- Preserved relevant inventory and lifecycle coverage through their actual consumers.
- Added full-tree Vulture scanning to the pre-commit configuration.

## Key decisions and limits

No helper had a concrete supported use outside tests, so no exception whitelist was added. Vulture remains outside project dependencies and CI.
