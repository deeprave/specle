# Summary: Keep Vale reports in document validation

## Summary

Vale reporting now remains within the Document validation workflow, eliminating the misleading duplicate `vale` check that GitHub previously grouped with Test.

## Outcome

Pull requests show one Vale check under Document validation. Vale findings remain available as annotations and continue to fail that job at the configured threshold.

## What changed

- Changed the non-fork Vale reporter from a standalone Reviewdog check to GitHub annotations.
- Aligned the non-fork and fork reporting paths while preserving the existing files and alert settings.
