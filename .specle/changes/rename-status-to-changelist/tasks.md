# Tasks: Rename status to changelist

- [x] 1. Rename the managed inventory skill
  - [x] 1.1 Rename canonical and installed `status` inventory skill directories to `changelist` and update their frontmatter, headings, and role-specific references.
  - [x] 1.2 Update managed workflow and lifecycle references that mean the pending-change inventory.
- [x] 2. Add current-work status guidance
  - [x] 2.1 Create matching canonical and installed `status` skills that report selection, lifecycle next action, and optional concise change summary.
  - [x] 2.2 Add compact primary-versus-linked worktree, branch, and working-tree-state reporting with read-only error handling.
  - [x] 2.3 Clarify safe verbose artifact handling, estimate-aware and unknown-state next-action derivation, and complete compact untracked-work reporting.
- [x] 3. Update human-facing documentation
  - [x] 3.1 Update applicable lifecycle and workflow references for the distinct changelist and status roles.
  - [x] 3.2 Assign pending and dependency-context inventory guidance exclusively to `changelist`.
- [x] 4. Synchronise the managed inventory
  - [x] 4.1 Regenerate `.agents/skills/specle/index.json` and confirm it lists `changelist` and the new `status` with distinct descriptions and usage.
- [x] 5. Verify the guidance change
  - [x] 5.1 Review renamed and new skills for role separation, lifecycle-next derivation, concise verbose output, read-only boundaries, and documentation alignment.
  - [x] 5.2 Validate the managed inventories and run repository quality gates without adding tests for the Markdown skill documents.
  - [x] 5.3 Add the Git `toplevel` term to the spell-check configuration so the documented portable command passes the repository gate.
  - [x] 5.4 Re-run documentation review and repository quality gates after the accepted external review corrections.
