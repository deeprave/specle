# Specle

`specle` is a collection of AI-agent skills for a lightweight, spec-driven development workflow. It helps agents and developers turn focused changes into clear, reviewable work without imposing heavyweight process.

The project primarily contains:

- Human-friendly Markdown documentation and workflow specifications.
- Agent skills that guide each stage of the spec-driven workflow.
- A small Python management script, available through `uvx`, for working with the project.

Python scripts in this repository are asynchronous, using `anyio` with the default `asyncio` runtime.

Markdown files created in this repo must not be hard-wrapped to an explicit width. Newlines should be used for paragraph endings only.

For Specle workflow guidance, read `.agents/AGENTS.md`.
