# Tasks: Correct thread-wrapper abuse

- [x] 1. Confirm the existing behavioural coverage exercises the affected CLI filesystem command paths without adding a source-inspection test. Files: existing tests.
- [x] 2. Convert the affected production filesystem helpers and callers in place to `anyio.Path` and async file APIs, retaining established function names and observable command contracts. Files: `src/specle/`.
- [x] 3. Run the existing behavioural tests and all project quality gates. Files: project tooling.
