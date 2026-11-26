# Estimate: Resurrect context json

- **T-shirt size:** M
- **Breakdown:** new files (~1 schema); modified files (~10–14 across schema registration, runtime validation, guidance, layout documentation, and tests); estimated tasks (~6–8).
- **Key risks:** preserving the strict durable-state boundary while offering an explicit optional validation path; ensuring a missing, invalid, or stale ignored file never affects lifecycle validation or command selection; keeping the schema intentionally extensible.
- **Confidence:** High
- **Recommendation:** design the validation boundary and guidance before tasking. This is independent of the queued active-directory and manifest work because it uses the existing `.specle/` location and must not depend on their future behaviour.
- **Similar past work:** `.specle/archive/restructure-spec-state/` retired context as durable state; `.specle/archive/versioned-json-schemas/` established the packaged schema registry and validation conventions.
