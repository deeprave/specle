"""Command-line entry point for Specle."""

from __future__ import annotations

import argparse
from importlib.resources import as_file
from pathlib import Path

import anyio

from specle.inventory import (
    SkillInstallationError,
    SkillMetadataError,
    install_skill,
    packaged_skills_root,
    update_skills,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the synchronous command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="specle",
        description="Manage Specle agent skills.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser(
        "install", help="Install a managed skill and its dependencies."
    )
    install.add_argument("skill", help="The managed skill to install.")
    update = commands.add_parser(
        "update", help="Update one managed skill or all managed skills."
    )
    update.add_argument("skill", nargs="?", help="The managed skill to update.")
    return parser


async def main(args: list[str] | None = None) -> None:
    """Run the asynchronous Specle command-line application."""
    parsed = build_parser().parse_args(args)
    target_root = Path.cwd() / ".agents" / "skills"

    try:
        with as_file(packaged_skills_root()) as source_root:
            if parsed.command == "install":
                installed = await anyio.to_thread.run_sync(
                    install_skill,
                    source_root,
                    target_root,
                    parsed.skill,
                )
            else:
                installed = await anyio.to_thread.run_sync(
                    update_skills,
                    source_root,
                    target_root,
                    parsed.skill,
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
