"""Command-line entry point for Specle."""

from __future__ import annotations

import argparse
from functools import partial
from importlib.resources import as_file
from pathlib import Path

import anyio

from specle.inventory import (
    SkillInstallationError,
    SkillMetadataError,
    initialise_distribution,
    packaged_distribution_root,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the synchronous command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="specle",
        description="Manage Specle agent skills.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    initialise = commands.add_parser(
        "init", help="Initialise the shared Specle distribution at a target directory."
    )
    initialise.add_argument(
        "target_directory",
        help="Existing directory that will contain the .agents distribution.",
    )
    initialise.add_argument(
        "--force",
        action="store_true",
        help="Replace existing distribution-managed destinations.",
    )
    return parser


async def main(args: list[str] | None = None) -> None:
    """Run the asynchronous Specle command-line application."""
    parsed = build_parser().parse_args(args)

    try:
        with as_file(packaged_distribution_root()) as source_root:
            installed = await anyio.to_thread.run_sync(
                partial(
                    initialise_distribution,
                    source_root,
                    Path(parsed.target_directory),
                    force=parsed.force,
                )
            )
    except (SkillInstallationError, SkillMetadataError) as error:
        raise SystemExit(str(error)) from error

    for path in installed:
        print(path)


def run() -> None:
    """Run the application using AnyIO's default asyncio runtime."""
    anyio.run(main)


if __name__ == "__main__":
    run()
