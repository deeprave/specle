# Estimate: add decision-gated progression

## T-shirt size

**M**

## Breakdown

- New files: approximately 2 — reusable automation steering and this project's `automation.md`.
- Modified files: approximately 15–20 — onboarding, lifecycle-owning skills, triage, abbreviated-work skills, root workflow guidance, project README, and their active-inventory copies.
- Removed files: 2 — the blueprint and active `implement` skills, plus the generated index entry after regeneration.
- Estimated tasks: 8–10.
- Key risks: preserving direct-invocation guards while enabling continuation; making the stop boundaries unambiguous to agents; and routing prepared abbreviated work correctly after `implement` is removed.

## Confidence

**High.** The affected inventory and lifecycle references are known. The main design work is defining a concise reusable policy that does not create a second, competing lifecycle.

## Recommendation

Create a technical design before tasks. The policy touches several lifecycle-owning skills and must clearly separate automatic local continuation from user decisions and delivery authority.

## Similar past work

- `202611180808-add-delivery-policy` introduced reusable steering plus project-selected delivery guidance and updated lifecycle ownership.
- `202611171130-add-skill-blueprints` established the blueprint/active-inventory synchronisation model.
