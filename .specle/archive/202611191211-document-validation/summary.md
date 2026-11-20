# Summary: Document validation

## Summary

Specle now checks its distributable documentation locally, before commits, and on pull requests for Markdown structure, spelling, prose guidance, and workflow consistency.

## Outcome

Source documentation has repeatable, repository-owned validation that catches common defects without checking generated installed copies or runtime work records. The skill index is portable across checkout locations.

## What changed

- Added Markdownlint, CSpell, and Vale configuration for the README, documentation, and blueprint package.
- Added the `document-validation` skill and matching staged-file pre-commit checks.
- Added pull-request validation with lifecycle consistency checks and scoped reporting permissions.
- Added project language guidance and onboarding support for language and spelling preferences.
- Simplified the generated skill index to grouped skill names, descriptions, and usage guidance.

## Key decisions and limits

Vale guidance remains advisory for local work. Pull-request Vale suggestions are visible without becoming a required repository check. Documentation validation intentionally covers source documentation only.
