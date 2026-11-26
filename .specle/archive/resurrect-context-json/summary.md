# Summary: Restored hand-off context

## Summary

Specle now provides an optional, local hand-off context that helps agents retain relevant current work across sessions without turning it into shared lifecycle state.

## Outcome

Agents can use an ignored `.specle/context.json` to keep concise milestones, todos, directives, and other relevant hand-off information. Projects can disable its maintenance or restrict updates by reviewing agents, while normal Specle workflow remains independent of it.

## What changed

- Added a permissive versioned context schema, portable policy, onboarding choices, and layout guidance.
- Established portable handling for untrusted external feedback and flexible agent-meaningful tracker locators.
- Preserved `vary` as a distinct review decision while allowing it to be routed through its recorded remediation workflow.

## Key decisions and limits

Context is optional, ignored, and non-authoritative: Specle does not read, validate, commit, merge, or use it to determine lifecycle or delivery facts.
