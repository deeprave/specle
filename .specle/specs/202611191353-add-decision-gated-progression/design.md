# Design: decision-gated progression

## Overview

Add a portable automation policy without adding an orchestration skill or runtime service. Lifecycle-owning skills remain responsible for their own validation, state updates, and direct-invocation guards. After a successful outcome, they consult project automation guidance to decide whether to invoke the recorded next local skill or stop.

## Architecture

```text
selected lifecycle skill
  ├─ performs its full existing workflow and state transition
  ├─ failure, ambiguity, triage summary, or delivery authority boundary → stop
  └─ successful local next step
       ├─ manual policy → report next and stop
       └─ decision-gated policy → invoke the next owning skill
```

`steering/automation.md` defines the two modes and portable stop conditions. `project/automation.md` selects one mode and may document narrow project exceptions. Each lifecycle-owning skill reads that project policy directly; root `AGENTS.md` remains a short pointer rather than a duplicate policy surface.

## Lifecycle and triage

Decision-gated continuation covers the normal local path: estimate, design, tasks, build, verify, and review. It never bypasses a skill's preflight or records a transition on behalf of that skill.

A failed verification stops with evidence. A successful review stops at `approved` for explicit commit authority. Review findings automatically enter triage; triage collects and persists all decisions, then presents a complete severity, decision, rationale, and route summary at `triaged`. It must wait for explicit `resolve`. Once invoked, resolve may resume decision-gated continuation after it dispatches a route.

Prepared abbreviated work no longer uses `implement`: `prepare` records `next` as its owning `bugfix` or `refactor` skill, which continues named queued work without replacing the active normal issue.

## Inventory migration

Remove `implement` from the blueprint and active inventories. Update direct references in steering, `AGENTS.md`, `prepare`, `bugfix`, and `refactor`; regenerate the installed `specle/index.json`. Keep blueprint and active files synchronised.

## Error handling

An absent, malformed, or unsupported automation policy means manual progression. A skill never treats that condition as authority to automate. Agents stop when a material choice is not resolved instead of guessing. Existing delivery policy remains the sole authority for external writes.

## Test strategy

Extend inventory tests for removal of `implement` and regenerated index contents. Add focused checks for the automation-policy documents, onboarding inventory/output, and the required triage summary instructions. Run the established Python gates and inspect blueprint/active parity.
