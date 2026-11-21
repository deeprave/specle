# Summary: Address security findings

## Summary

Specle now rejects invalid installed skill files while retaining intentional symlinked regular-file layouts, and its Dependabot auto-merge workflow uses the privileged App credential only for the final merge action.

## Outcome

Validation reports non-regular or broken-link `SKILL.md` candidates instead of silently omitting them. Eligible Dependabot updates continue to require the established checks before the trusted App enables merge automation.

## What changed

- Added a shared regular-file boundary for validation inputs and applied it to installed skills, generated indexes, runtime selectors, and status records.
- Made installed-skill discovery distinguish a directory without `SKILL.md` from an invalid candidate file.
- Deferred GitHub App token creation until the final eligible auto-merge step.

## Key decisions and limits

Intentional symlinked installation layouts remain supported. The change does not add extra restrictions for user-selected symlinked directories or harden against a concurrent local pathname-replacement attack.
