# Fast lane test

## Problem

The archival-finalisation update on an otherwise reviewed delivery PR changes only Specle runtime metadata, but the PR workflow currently reruns all language, package, and blueprint checks before auto-merge can proceed.

## Goal

Classify each new PR update independently. When its diff is strictly limited to active/archive Specle metadata, run `specle validate .` behind the existing `Verify` check; otherwise retain the full PR suite. Keep every `main` push on the full suite so a future publish workflow can require exact-merge-commit evidence.

## Scope

Update the GitHub Actions test workflow and its tests or documentation as needed to prove the classifier's conservative fallback, required-check continuity, metadata validation, and unchanged `main` coverage. Do not introduce publishing automation, alter the completion lifecycle, or bypass full checks for any code, workflow, documentation, configuration, or blueprint change.

## Verification

Verify the workflow structure for both paths, including the required aggregation result; test or otherwise deterministically exercise classification for eligible, mixed, and unclassifiable PR updates; and run the full local project quality gates.
