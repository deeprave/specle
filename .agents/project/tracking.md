# External work guidance

## Sources

GitHub Issues are a read-only source of collected user reports, feature requests, and bug reports for Specle. Import only explicitly named issues through the configured GitHub connector; preserve their canonical links in the receiving spec's `tracker-links.json`.

An imported issue informs a specification. Checking it later for updates must report differences first and must not change the specification until the user confirms the proposed update.

## Destination

This project has no external delivery destination. Do not create, update, synchronise, or publish work records to GitHub or any other external system as part of tracking.

## Pull requests

When a pull request directly resolves a GitHub Issue linked as a source, its description must include `Close #<issue>`. Do not add a closing reference for an issue that the pull request merely mentions or partially relates to.
