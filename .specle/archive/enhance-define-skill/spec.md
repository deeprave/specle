# Enhance define skill

## Problem

The existing `define` skill reliably creates the required files but mostly translates a request into a template. It does not explicitly direct an agent to investigate relevant project evidence, surface consequential unknowns, or clearly separate established facts from assumptions. It also records a change without presenting the completed intent to the user, while activation can start build immediately once planning artifacts exist.

## Goal

Make `define` a curious, evidence-led definition stage that produces a concise, useful contract for later design and implementation while remaining strictly unselected planning work. The only confirmation boundary is immediately before implementation begins.

## Direction

Reshape `define` around four activities: investigate applicable guidance, code, documentation, and related changes; ask focused user questions only where material uncertainty remains; create substantive durable artifacts; then report a concise non-blocking definition summary. Stop when existing work already fully covers the request; describe boundaries only for partial overlap. A proposed duplicate slug is blocking: identify the conflicting change and let the user rename or investigate it.

`activate` and `tasks` retain ordinary progression. Immediately before a planned normal change begins implementation, `build` restates the current specification and asks for explicit confirmation, including in decision-gated progression.

The blueprint remains canonical. Synchronise the installed `define`, `activate`, `tasks`, and `build` skills and relevant policy copies, then regenerate the installed index. Do not add a new skill or change the durable change schema.

## Verification

Check that the blueprint and installed copies agree; full overlap and duplicate slugs stop without creating a duplicate; definition reports but does not gate durable records; and build requires the sole pre-implementation confirmation. Validate the updated inventories and run the repository quality gates.
