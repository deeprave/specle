# Estimate: Add release skill

## T-shirt size

M

## Breakdown

- New files: ~1 repository-local skill.
- Modified files: ~1–2 project guidance or inventory references if needed to make the local ownership boundary clear.
- Estimated tasks: ~5.
- Key risks: correctly distinguishing a selected active change from queued work; using the package's installed distribution version when generating the manifest after `pyproject.toml` changes; ensuring the deliberately broad release commit is visible and explicitly authorised before staging.

## Confidence

High

## Recommendation

Design the release skill around a strict read-only preflight, then an ordered preparation sequence. The skill should never be placed in managed blueprints or the generated inventory, and should stop before push or publishing. The explicit all-working-tree commit rule is intentional and should be stated plainly rather than approximated through change ownership detection.

## Similar past work

`add-specle-manifest` established the release-only, append-only manifest command and its blueprint-only ownership boundary. `add-delivery-policy` established this repository's branch-and-pull-request delivery conventions.
