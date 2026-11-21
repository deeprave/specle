# Summary: Add blueprint manifest

## Summary

Specle now provides a release-only blueprint manifest that records the managed skill and policy inventory for each package version.

## Outcome

Maintainers can create an append-only provenance record before a release, making it possible to identify the managed resources present in a recorded package generation and compare their checksums over time.

## What changed

- Added `specle manifest <output>` for generating plain-text release entries.
- Added the initial blueprint manifest and release-preparation guidance.
- Centralised the package version through `specle.__version__`, resolved from distribution metadata.
- Made manifest generation preserve existing temporary files and report invalid UTF-8 input clearly.

## Key decisions and limits

The manifest is source-only release provenance. It is separate from the skill-discovery index and is neither installed into `.agents/` nor used as project runtime state.
