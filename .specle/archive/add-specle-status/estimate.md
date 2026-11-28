# Estimate: Add Specle status

- **T-shirt size:** M
- **Breakdown:** Approximately one new reporting module and three to five modified files; four implementation tasks.
- **Key risks:** Correctly reporting malformed selectors and reciprocal sidecar links, parsing Git porcelain safely, and retaining partial results when Git commands fail.
- **Confidence:** Medium.
- **Recommendation:** Design the reporting and error boundaries before implementation; the work is cohesive and does not need splitting. No dependencies are assumed.
- **Similar past work:** `add-specle-changes-index` and `allow-sidecar-activation` established shared change-state and lifecycle reporting.
