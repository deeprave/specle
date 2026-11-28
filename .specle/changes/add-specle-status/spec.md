# Add Specle status

## Motivation

The CLI already reports change inventories, but it has no concise equivalent of the agent `status` skill for orienting to selected work and local checkout state.

## Intended outcome

Add a read-only `specle status` command that reports selected change state, declared active sidecars, durable lifecycle milestones, the next lifecycle action, and compact Git status.

## Scope and impact

The command will build on existing change-state and lifecycle data rather than creating a new state store. Its initial milestone view is limited to timestamps already persisted in status records. Git reporting will provide counts only, preserving concise CLI output and avoiding path disclosure by default.

## Assumption

“Recent milestones” means the available lifecycle timestamps in a selected change’s durable status record. A later change can add richer milestone sources if needed.

## Verification direction

Behavioural CLI tests should cover valid, missing, and invalid selections; declared sidecars and invalid reciprocal links; lifecycle-timestamp rendering; clean and dirty Git summaries; detached HEAD; and partial Git-inspection failures.
