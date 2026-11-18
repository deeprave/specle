---
name: onboard
specle_group: Setup
requires: []
description: >-
  Establish or refresh a repository's project guidance overlay.
usage: >-
  Use when project guidance is missing or incomplete; inventory it, ask one question at a time, then write the completed overlay.
---

# Onboard a project overlay

Create or refresh `.agents/project/`. These repository-local Markdown documents are authoritative project facts for reusable skills and are managed by the user after onboarding.

## Workflow

1. Read `AGENTS.md`, `.agents/AGENTS.md`, `.agents/steering/*.md`, and every existing `.agents/project/` document. Inventory the required project documents: `README.md`, `product.md`, `tech.md`, `tracking.md`, `testing.md`, `security.md`, `logging.md`, `api-standards.md`, and `review.md`. Mark each as **present and complete**, **present but incomplete**, or **missing**. Treat placeholders, unsupported assumptions, and absent required facts as incomplete.
2. Inspect the repository's manifest, configuration, source layout, CI configuration, and existing developer documentation. Prepare evidence-backed defaults, but do not treat inference as fact.
3. Report the inventory and evidence-backed defaults to the user. Ask one focused question at a
   time for every missing or incomplete document. Wait for the answer before asking the next
   question, and retain each answer in the conversation until the overlay is written. Confirm or
   correct the observed defaults for:
   - product purpose, users, scope, and durable constraints;
   - languages, versions, frameworks, package/build management, architecture, dependencies, and implementation conventions;
   - issue tracking, connector, authentication, identifiers, links, and project scope;
   - test frameworks, organisation, methods, quality gates, and coverage expectations;
   - credentials, tokens, secret handling, sensitive code, and application-security requirements;
   - logging format, destinations, levels, PII, redaction, and retention; and
   - inbound and outbound APIs, authentication, validation, pagination, rate limits, retries, error policy, and data handling; and
   - review-finding presentation mode, any override of the steering presentation layouts, and whether any finding classes may be accepted or addressed automatically.
   Do not create or modify `.agents/project/` while collecting answers. Continue until every
   required topic is answered or explicitly recorded as not established.
4. After all answers are collected, create or refresh the project documents needed by the workflow:
   `README.md`, `product.md`, `tech.md`, `tracking.md`, `testing.md`, `security.md`, `logging.md`,
   `api-standards.md`, and `review.md`. In `review.md`, record the presentation mode, any steering-layout override, and automated-decision policy; severity and default layouts are defined by steering. Write only user-confirmed or source-supported facts. If a fact remains
   unknown, say that it is not established rather than inventing it.
5. Ensure the README identifies these documents as authoritative and maps each one.
6. Keep the portable `.agents/steering/` policy generic. Move repository facts out of steering rather than copying them into both locations.
7. Ensure the root `AGENTS.md` has a concise durable pointer to `.agents/AGENTS.md`; do not restate workflow or project documents in the root file.
8. After the project overlay exists and its README maps every project document it creates, remove only the `<!-- agents-onboard:start -->` through `<!-- agents-onboard:end -->` bootstrap block from the root `AGENTS.md`. Keep the durable `.agents/AGENTS.md` pointer.
9. Ensure the repository tracks `.agents/steering/` and `.agents/project/`. Establish the repository's separate commit policy for `.specle/`. Validate that the README maps every project document it creates.

## Boundaries

- Do not invent standards, external integrations, or tracker configuration.
- Do not alter application code, dependencies, CI, or project configuration as part of onboarding.
- Project guidance documents describe durable repository facts; individual feature requirements belong in `.specle/specs/`.
- Preserve supported local content when refreshing an existing overlay. Do not replace established facts with generic template text.

## Next

- `analyse` — compare the overlay with the codebase when conventions may have drifted.
- `spec` — begin a feature once the project context is established.
