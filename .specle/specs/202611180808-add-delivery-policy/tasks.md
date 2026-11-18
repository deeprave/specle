# Tasks: delivery policy and completion workflow

- [x] 1. Add portable `delivery.md` steering that defines the supported delivery models, model-specific lifecycle meanings, and project-customisation boundary; install it in the active steering inventory.
- [x] 2. Extend `onboard` and the project guidance inventory for `project/delivery.md`, collecting the delivery model and delivery conventions one question at a time while preserving unknown policy explicitly.
- [x] 3. Update lifecycle, context, review, triage, and resolve guidance so local review produces `approved`, branch-and-PR delivery records `committed`, and explicitly named submitted normal changes re-enter review work without replacing the active issue.
- [x] 4. Amend the `commit` skill to enforce approved-target, scoped-staging, required-check, authority, and model-specific delivery rules without requiring a future delivery-record schema.
- [x] 5. Amend the `complete` skill for committed branch-and-PR delivery to read and update the selected target's existing context record, while retaining its head-branch guard, authorised merge, safe target-branch synchronisation, recoverable stash handling, and already-merged confirmation.
- [x] 6. Extend behavioural coverage for no-action outcomes by delivery history, independent-spec hand-off without premature completion, named committed-normal re-entry, authority guards, branch mismatch, stash recovery, and context-record delivery evidence without a future-schema prerequisite.
- [x] 7. Synchronise the root schema documentation with the delivered workflow's context-record delivery evidence, removing the future-schema prerequisite while keeping README scope unchanged.
- [x] 8. Update Resolve, `spec`, and the root lifecycle diagrams so no-action and independent-spec routes restore `approved` or `committed` according to delivery history and queue independent normal work.
- [x] 9. Update `bugfix` to record an explicit origin and delivery relationship for a sidecar created from procedurally blocked active work, without linking independently created bugfixes.
- [x] 10. Update `status` and `commit` to report and deliver only declared approved sidecars with their related origin, recording shared delivery evidence and transitions together.
- [x] 11. Add focused coverage for explicit sidecar relationships, status reporting, joint delivery, and exclusion of unlinked queued bugfixes.
- [x] 12. Update abbreviated-work workflows so executing a bugfix or refactor during active work requires an explicit relationship to that active change; direct unlinked work to `prepare` and later separate-worktree execution.
- [x] 13. Extend focused coverage for the active-worktree execution guard and independent prepared abbreviated work.
- [x] 14. Move completed linked queued sidecars to `recent_specs`, retaining their relationship and delivery evidence.
- [x] 15. Make portable workflow guidance model-dependent after `commit` and remove stale language that treats local review as completion.
- [x] 16. Align `build` frontmatter usage with the supported named committed-target workflow and add focused coverage.
