# Requirements: add triage elicitation

## Introduction

Triage currently presents each review finding as free-form text followed by a terse decision prompt. Clients that support structured elicitation can present the standard decisions as native choices, while every other client needs an equally clear textual fallback.

## Glossary

- **Elicitation:** a client-supported structured request for a user decision.
- **Fallback prompt:** the textual request used when elicitation is unavailable.
- **Other:** a free-form response path for a variation, discussion, or another user-directed decision.

## Requirements

### Requirement 1: Present standard triage decisions consistently

**User Story:** As a developer reviewing findings, I want the available decisions presented consistently, so I can quickly choose a standard disposition or describe an alternative.

#### Acceptance Criteria

1. For each finding that requires a user decision, triage SHALL offer `accept`, `decline`, `defer`, and `other`.
2. The `other` choice SHALL allow the user to provide a variation, discussion, or another explicit disposition; it SHALL not be treated as an automatic acceptance.
3. The textual fallback SHALL ask: `Would you like to accept, decline, defer, or other (vary/discuss)?`

### Requirement 2: Use client elicitation when available

**User Story:** As a developer using a client with elicitation support, I want triage decisions presented through the client interface, so standard choices are direct and unambiguous.

#### Acceptance Criteria

1. IF the current client exposes an elicitation capability, THEN triage SHALL use it for a per-finding triage decision.
2. IF elicitation is unavailable or cannot be used, THEN triage SHALL present the fallback prompt without failing or blocking the workflow.
3. Client-specific elicitation syntax SHALL remain outside the portable decision semantics; the recorded disposition format remains unchanged.

### Requirement 3: Preserve decision-gated triage flow

**User Story:** As a developer, I want structured prompting to preserve deliberate review decisions, so it does not automatically modify work.

#### Acceptance Criteria

1. Triage SHALL continue to present findings one at a time by default, in the configured severity order and with the existing source, analysis, and recommendation fields.
2. Triage SHALL record a decision and route only after the user has supplied one, including an explicit interpretation of an `other` response.
3. Triage SHALL retain its final decision-and-route summary and wait for explicit `resolve`.

## Non-Functional Requirements

- This change updates portable workflow guidance, not project delivery policy or runtime state.
- It must work for clients with and without structured elicitation.
- It has no dependency on any queued change.
