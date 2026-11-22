# Summary: Improve definition and build alignment

## Summary

Specle now creates and reports clearer evidence-led change definitions, while asking for explicit user alignment only immediately before implementation begins.

## Outcome

Defined changes can be reviewed, revised, or left queued without an unnecessary confirmation gate. Planned work now restates its current specification at build start so the developer can confirm the intended outcome before implementation proceeds.

## What changed

- Strengthened `define` with evidence gathering, material-uncertainty handling, duplicate-coverage checks, and duplicate-slug handling.
- Made `build` the sole confirmation boundary and kept normal activation and task progression uninterrupted.
- Aligned lifecycle and automation guidance with the new workflow.

## Key decisions and limits

`artifact` is the accepted project spelling for software-industry content.
