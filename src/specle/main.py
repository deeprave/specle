"""Command-line entry point for Specle."""

from __future__ import annotations

import argparse
import json
from functools import partial
from importlib.resources import as_file
from pathlib import Path

import anyio

from specle.inventory import (
    SkillInstallationError,
    SkillMetadataError,
    build_skill_index,
    discover_installed_specle_skills,
    initialise_distribution,
    packaged_distribution_root,
)
from specle.lifecycle import (
    LifecycleDiagnostic,
    read_runtime_snapshot,
    validate_installed_skill_inventory,
    validate_runtime_records,
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
    validate = commands.add_parser(
        "validate", help="Validate an installed Specle target without changing it."
    )
    validate.add_argument(
        "target_directory",
        help="Existing directory containing the Specle runtime to validate.",
    )
    validate.add_argument(
        "--verbose",
        action="store_true",
        help="Report each completed validation area and its summary count.",
    )
    return parser


async def main(args: list[str] | None = None) -> None:
    """Run the asynchronous Specle command-line application."""
    parsed = build_parser().parse_args(args)

    if parsed.command == "validate":
        target = Path(parsed.target_directory)
        diagnostics = list(validate_installed_skill_inventory(target))
        try:
            skills = discover_installed_specle_skills(target)
        except SkillMetadataError:
            skills = ()
        else:
            runtime = read_runtime_snapshot(target)
            diagnostics.extend(validate_runtime_records(target, skills, runtime))
        resolved_target = target.expanduser().resolve()
        index_path = resolved_target / ".agents" / "skills" / "specle" / "index.json"
        try:
            index = json.loads(index_path.read_text())
        except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
            diagnostics.append(
                _diagnostic(f"invalid generated skill index: {index_path}")
            )
        else:
            expected_index = build_skill_index(
                skills, resolved_target / ".agents" / "skills"
            )
            if index != expected_index:
                diagnostics.append(
                    _diagnostic(f"invalid generated skill index: {index_path}")
                )
        if diagnostics:
            for diagnostic in diagnostics:
                print(diagnostic.message)
            raise SystemExit(1)
        if parsed.verbose:
            statuses = {
                transition.target.status
                for skill in skills
                if skill.lifecycle is not None
                for transition in skill.lifecycle.transitions
            }
            terminal = {
                status
                for skill in skills
                if skill.lifecycle is not None
                for status in skill.lifecycle.terminal
            }
            queued = runtime.context.get("queued_specs", []) if runtime.context else []
            queued_count = len(queued) if isinstance(queued, list) else 0
            print(f"validated managed skills: {len(skills)}")
            print(
                f"validated lifecycle graph: {len(statuses)} statuses, {len(terminal)} terminal"
            )
            print(f"validated skill index: {index_path}")
            print(
                f"validated runtime state: current spec + {queued_count} queued specs"
            )
        print(f"validated {resolved_target}")
        return

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


def _diagnostic(message: str) -> LifecycleDiagnostic:
    return LifecycleDiagnostic("invalid-index", message)


def run() -> None:
    """Run the application using AnyIO's default asyncio runtime."""
    anyio.run(main)


if __name__ == "__main__":
    run()
