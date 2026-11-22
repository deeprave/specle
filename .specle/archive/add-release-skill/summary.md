# Summary: Add release skill

## Summary

This repository now has a concise local `release` skill for preparing an authorised release commit with a version update and blueprint manifest record.

## Outcome

Release preparation has a defined, repeatable path that checks for active work and open pull requests, uses a canonical release version, starts from a synchronised delivery branch, and leaves publishing and other external release actions to separate explicit work.

## What changed

- Added repository-local release instructions for version selection, manifest generation, branch creation, and an authorised full-tree release commit.
- Added delivery-branch synchronisation and canonical PEP 440 plus manifest-format validation before release preparation.
- Kept the skill outside the distributed Specle inventory.

## Key decisions and limits

The release commit intentionally includes all tracked and non-ignored untracked working-tree changes after the developer reviews and authorises the full candidate. The skill does not push, open a pull request, tag, publish, or create a release.
