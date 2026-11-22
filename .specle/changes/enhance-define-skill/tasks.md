# Tasks: Enhance define skill

- [x] 1. Refine the canonical definition workflow
  - [x] 1.1 Update `define` to report a non-blocking summary after creating a durable defined record, while preserving investigation, elicitation, and the defined-only boundary.
  - [x] 1.2 Stop and report conflicting change evidence for full coverage or a duplicate proposed slug.
- [x] 2. Add the sole pre-build confirmation
  - [x] 2.1 Restore ordinary activation and task progression without confirmation pauses.
  - [x] 2.2 Update `build` to restate the current specification and require explicit confirmation before a planned change's first implementation action.
  - [x] 2.3 Document the pre-build stop in decision-gated automation, lifecycle policy, and the human lifecycle reference.
- [x] 3. Synchronise managed guidance
  - [x] 3.1 Copy all changed canonical skills and policies to their matching `.agents/` paths unchanged.
  - [x] 3.2 Regenerate `.agents/skills/specle/index.json` and confirm its metadata remains accurate.
- [x] 4. Verify the guidance change
  - [x] 4.1 Review canonical and installed copies for exact agreement, normal preparation flow, and the sole pre-build confirmation boundary.
  - [x] 4.2 Validate the inventory and run applicable repository quality gates without adding tests for the Markdown skill documents.
