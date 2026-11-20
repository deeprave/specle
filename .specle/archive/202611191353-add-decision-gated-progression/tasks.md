# Tasks: add decision-gated progression

- [x] 1. Add regression coverage for the managed inventory and policy surfaces (`tests/test_inventory_metadata.py`, `tests/test_inventory_index.py`, new focused blueprint-guidance tests).
  - [x] 1.1 Assert `implement` is absent from the packaged inventory and generated index, while the remaining direct dependencies remain valid.
  - [x] 1.2 Assert the automation steering/project guidance, onboarding inventory, and triage completion instructions expose the required policy and summary behaviour.

- [x] 2. Define the reusable and local automation policy (`src/specle/blueprints/steering/automation.md`, `.agents/steering/automation.md`, `.agents/project/automation.md`, project README copies).
  - [x] 2.1 Document manual fallback, decision-gated continuation, and the mandatory ambiguity, verification, triage-summary, and delivery-authority stops.
  - [x] 2.2 Select decision-gated progression for Specle itself and map the new project document in both project README copies.

- [x] 3. Update onboarding to establish automation policy (`src/specle/blueprints/skills/onboard/SKILL.md`, `.agents/skills/onboard/SKILL.md`).
  - [x] 3.1 Add `automation.md` to the required inventory and the one-at-a-time collection topics.
  - [x] 3.2 Require onboarding output to create and map the project-owned policy only after the user answers.

- [x] 4. Add decision-gated continuation guidance to lifecycle-owning skills (`src/specle/blueprints/skills/`, `.agents/skills/`).
  - [x] 4.1 Preserve direct-invocation preconditions while directing successful local estimate, design, tasks, build, verify, review, and resolve paths through the selected policy.
  - [x] 4.2 Preserve manual-mode next-step reporting and ensure failure, ambiguity, and external-delivery boundaries stop with actionable context.

- [x] 5. Make triage completion a mandatory user checkpoint (`src/specle/blueprints/skills/triage/SKILL.md`, `.agents/skills/triage/SKILL.md`).
  - [x] 5.1 Persist every decision and route, set `triaged`, then present the complete decision-and-route summary.
  - [x] 5.2 Stop for explicit `resolve` or a requested decision revision after that summary.

- [x] 6. Remove the `implement` shortcut and repair abbreviated-work routing (`src/specle/blueprints/skills/implement/`, `.agents/skills/implement/`, lifecycle and abbreviated-work skills).
  - [x] 6.1 Remove the managed skill directories and all workflow/index references.
  - [x] 6.2 Change prepared bugfix/refactor records and guidance to resume through their named owning skill.

- [x] 7. Reconcile reusable workflow guidance and active inventory (`src/specle/blueprints/AGENTS.md`, `.agents/AGENTS.md`, lifecycle documents, `.agents/skills/specle/index.json`).
  - [x] 7.1 Remove `implement` from the described workflow without adding project automation policy to AGENTS guidance.
  - [x] 7.2 Synchronise all affected blueprint files into `.agents/` and regenerate the local index.

- [x] 8. Verify the completed migration.
  - [x] 8.1 Run focused tests, then `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check`.
  - [x] 8.2 Check blueprint/active parity, the generated index, stale `implement` references, and the documented decision boundaries.

- [x] 9. Replace brittle policy-prose assertions with inventory behaviour checks (`tests/test_delivery_blueprints.py`).
  - [x] 9.1 Retain package inventory and generated-index coverage while removing literal workflow wording checks.

- [x] 10. Add explicit normal-spec activation and complete automatic handoff semantics.
  - [x] 10.1 Keep `spec` planning-only and add `activate <spec-name>` as the explicit commencement boundary.
  - [x] 10.2 Carry selected targets through all automatic planning, implementation, verification, review, triage, abbreviated-work, and revision handoffs.

- [x] 11. Make forced installation synchronise managed skill removals.
  - [x] 11.1 Identify obsolete `specle_group`-marked target skills during preflight and require `--force` to replace or remove them.
  - [x] 11.2 Recoverably remove obsolete managed skills with replacement backups, preserving unrelated skills on success and failure.
