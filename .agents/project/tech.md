# Technology guidance

Specle is a Python project requiring Python 3.13 or later. Python scripts are asynchronous and use AnyIO with the default `asyncio` runtime.

Use `uv` for Python environment and package management. Specle may be published to PyPI or distributed directly from GitHub.

The project uses a `src/` layout. The `specle` command is a small `argparse`-based management CLI for installing and updating the skill inventory.

Use UK/AU spelling except for established software-industry exceptions such as `license`, `artifact`, and `color`. Do not hard-wrap Markdown prose paragraphs.
