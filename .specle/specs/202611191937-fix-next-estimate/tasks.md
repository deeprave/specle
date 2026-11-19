# Tasks: fix next estimate

- [x] 1. Correct queued normal-change lifecycle guidance.
  - [x] 1.1 Make `activate` the only current-issue transition and define its next-stage selection from existing planning artifacts.
  - [x] 1.2 Allow explicit queued estimate/design/tasks planning without continuation; require design before tasks.

- [x] 2. Migrate queued normal runtime records and active inventory.
  - [x] 2.1 Change existing queued normal records to `next: "activate"` without altering their active state.
  - [x] 2.2 Synchronise blueprints to `.agents/`, regenerate the index, and inspect the activation boundary.

- [x] 3. Make activation preparation deterministic.
  - [x] 3.1 Require activation to fill missing estimate, design, and tasks artifacts in that order before it invokes build.
  - [x] 3.2 Ensure existing task plans without a design are reconciled through design and tasks rather than treated as build-ready.
