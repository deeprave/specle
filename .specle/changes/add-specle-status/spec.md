# Add Specle status

## Motivation

The CLI already reports change inventories, but it has no concise equivalent of the agent `status` skill for orienting to selected work and local checkout state.

## Intended outcome

Add a read-only `specle status` command and align the `status` skill with it that reports selected change state, locally registered active sidecars, available lifecycle timestamps, the next lifecycle action, compact Git status, and concise optional context.

## Scope and impact

The command will build on existing change-state and lifecycle data rather than creating a new state store. Context summaries group milestones, todos and other list entries by date and change or subject, with indented details and lines shorter than 80 characters. Git reporting will provide counts only, preserving concise CLI output and avoiding path disclosure by default.

## Assumption

Context is optional and read for display; no new validation or milestone store is introduced.

## Verification direction

Behavioural CLI tests should cover valid, missing, and invalid selections; locally active sidecars; lifecycle-timestamp and concise context rendering; clean and dirty Git summaries; detached HEAD; and partial Git-inspection failures.
