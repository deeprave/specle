# Estimate: Link sidecar completion

## T-shirt size

L

## Breakdown

- New files: ~0–2 production helpers, depending on whether sidecar relationship handling fits cleanly in the existing lifecycle module.
- Modified files: ~18–26 across the change-status schema, lifecycle/state helpers, focused production tests, lifecycle and layout documentation, and managed skills with their installed copies.
- Estimated tasks: 6–8 top-level tasks.
- Key risks: defining reciprocal links without partial durable records; ensuring completion includes only mutually declared, eligible sidecars; preserving immutable archived records; and keeping completion-PR/wrapup delivery evidence coherent for every jointly archived record.

## Confidence

High

## Recommendation

Use a detailed design. The work crosses the durable relationship contract, package-owned lifecycle validation, archival semantics, and several skill owners. Keep candidate discovery parent-driven and reject incomplete reciprocal records rather than inferring relationships from active directories.

## Similar past work

`add-wrapup-skill` introduced the archival completion-PR boundary and timestamp ownership. `fix-completion-stash` is the concrete related sidecar that exposed the remaining independent-completion problem. `restructure-spec-state` and `versioned-json-schemas` establish the state and schema-validation patterns to extend.
