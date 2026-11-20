# Estimate: add pre-commit

## T-shirt size

M

## Breakdown

- New files: 1 committed configuration file (`.pre-commit-config.yaml`).
- Modified files: 0 expected; Git hook installation is local Git state, not a repository file.
- Estimated tasks: 3.
- Key risks: remote hook releases must be checked immediately before implementation; the host-provided tool must be used without changing Python dependencies or CI; and the specified `ty check envex` entry does not match this repository's documented `uv run --frozen ty check` command or a visible `envex` path.

## Confidence

Medium

## Recommendation

Design the configuration and local-hook execution explicitly before implementation. Confirm how the requested Ty entry should map to this repository during design; do not silently substitute a different command. Keep the hook installation and any host-tool use out of tracked Python dependencies and CI.

## Similar past work

No archived Specle change establishes a pre-commit configuration pattern. `enable-automerge` demonstrates the project convention of verifying external-tool configuration immediately before delivery, but is not a technical dependency.
