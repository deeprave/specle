# Estimate: document-validation

## T-shirt size

L

## Breakdown

- New files: approximately 5–8: a local document-validation skill, Markdownlint, CSpell, and Vale configuration and rules, plus local invocation guidance.
- Modified files: approximately 3–6: onboarding/project language guidance, blueprint inventory or references, and focused tests where deterministic configuration behaviour needs coverage.
- Estimated tasks: 6–8.
- Key risks: tuning each checker to distinguish genuine defects from intentional skill and documentation conventions; keeping shared configuration coherent while allowing narrowly justified scope-specific rules; ensuring the skill uses the existing `specle validate` lifecycle command without duplicating its validation logic.

## Confidence

Medium

## Recommendation

Design is warranted. Establish the precise source-documentation inventory and configuration ownership before implementation, then tune against representative skills, policies, README content, and `docs/`. Keep the local validation skill separate from a later CI workflow.

## Similar past work

`add-specle-validate` already supplies deterministic lifecycle validation through `specle validate`; this change should invoke that capability rather than introduce a second lifecycle validator.
