# Tasks: Fix approved review validation

- [x] 1. Add a failing runtime validation test for an approved change with `review.status: "resolved"`. (`tests/test_lifecycle.py`)
- [x] 2. Update the lifecycle validator to accept documented terminal resolved-review evidence for `approved` changes while retaining invalid-review diagnostics for unsupported states. (`src/specle/lifecycle.py`)
- [x] 3. Run the focused regression test and project quality gates. (`tests/test_lifecycle.py`)
