# Delivery guidance

## Model

Use a shared upstream with branch-and-pull-request peer review.

## Conventions

- Delivery branch: `main`.
- Branch naming: `<type>/<slug>`. Current types are `feature`, `chore`, and `bugfix`; use a slug that usually matches the current change. Additional types are not yet established.
- Commit title and message format: `<type>: <short description of the change>`.
- Required pre-delivery checks: every project test must pass and local Specle review must approve the change.
- Secret scanning: no separate delivery-time scanner is established; secrets must not be committed under `security.md`.
- Pull-request format: use the commit-title format for the pull-request title. No template or body convention is established.
- Final delivery event: the pull request is merged and the local `main` checkout is updated.
- Agent authority for external writes: agents may create branches, commit, push, create or update pull requests, merge approved pull requests, and synchronise local `main`; each external write still requires explicit user authorisation for the action.
