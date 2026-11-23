# Tasks: Fix approved review validation

- [x] 1. Add runtime validation coverage for an approved change with a terminally settled `review.status: "resolved"`, plus unresolved, missing, and unreadable findings records. (`tests/test_lifecycle.py`)
- [x] 2. Update the lifecycle validator to read the matching findings record for a resolved review and accept only terminally settled evidence, while retaining invalid-review diagnostics for unsupported states. (`src/specle/lifecycle.py`)
- [x] 3. Run focused regressions and project quality gates. (`tests/test_lifecycle.py`)
