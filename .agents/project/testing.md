# Testing guidance

Every accepted change must run the project's required quality gates:

- `pytest`
- `ruff check`
- `ruff format`
- `ty`

Run these tools through `uv` using the repository's configured invocations. Use test-first development for behaviour changes in accordance with the shared testing steering.
