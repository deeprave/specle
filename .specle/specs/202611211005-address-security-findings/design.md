# Technical design: address security findings

## Overview

Make two bounded changes: use the ordinary workflow token for Dependabot classification and required-check polling, creating the App token only for the final auto-merge command; and centralise the validation rule that every target-supplied input resolves to a regular file before its text is read.

## Architecture

```text
Dependabot PR
  -> fetch metadata (ordinary GITHUB_TOKEN)
  -> wait for required checks (ordinary GITHUB_TOKEN)
  -> create App installation token (eligible, passing PR only)
  -> enable merge-commit auto-merge (App token)

specle validate <target>
  -> regular-file text reader
  -> installed skills / runtime state / generated index
  -> diagnostics instead of special-file reads
```

The workflow job will grant the ordinary token only read scopes needed by metadata and check polling. `dependabot/fetch-metadata` supports its default `github.token` when alert and compatibility lookup are disabled. The final App-token step will continue to use the existing secret and is the only step receiving it.

A small shared text-reading helper will check `Path.is_file(follow_symlinks=True)` before calling `read_text()`. It will allow a symlink resolving to a regular file and reject a directory, device, FIFO, broken link, or other non-regular target with a path-specific error. It will be used by installed-skill discovery, runtime state reading, and generated-index loading; package-resource reads and installation writes remain out of scope.

## API and data

No public CLI syntax or JSON record shape changes.

- `specle validate` continues to emit diagnostics and exit non-zero for invalid target inputs.
- Existing symlinked regular skill, selector, status, and index files remain accepted.
- GitHub workflow eligibility remains unchanged: uv patch/minor and GitHub Actions patch/minor/major.

## Error handling

| Condition | Behaviour |
| --- | --- |
| Validation input resolves to a non-regular file | Do not read it; emit a path-specific validation diagnostic and fail validation. |
| Regular-file read fails after the type check | Preserve existing path-specific unreadable-input diagnostic behaviour. |
| Metadata/check polling fails with the ordinary token | Fail the workflow; do not create an App token or enable auto-merge. |
| Required checks fail | Fail the workflow; do not create an App token or enable auto-merge. |

## Test strategy

- Add focused tests for a symlink to a regular file being accepted and a symlink to a non-regular target being rejected without reading it.
- Cover runtime records, installed skill reading, and generated-index validation through their public validation paths.
- Inspect the workflow to prove the secret is referenced only by the final App-token step, while metadata and check polling use the ordinary token and retain the existing eligibility conditions.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and `uv run --frozen specle validate . --verbose`.
