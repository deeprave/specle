"""Command-line entry point for Specle."""

from __future__ import annotations

import argparse
import json
from functools import partial
from importlib.resources import as_file
from pathlib import Path
from typing import cast

import anyio

from specle import __version__
from specle.file_reading import read_regular_text
from specle.inventory import (
    DistributionInventory,
    SkillInstallationError,
    SkillMetadataError,
    build_skill_index,
    compare_managed_inventories,
    initialise_distribution,
    managed_resource_checksums,
    packaged_distribution_root,
    scan_managed_inventory,
    update_distribution,
)
from specle.lifecycle import (
    LifecycleDiagnostic,
    read_runtime_snapshot,
    validate_runtime_records,
)
from specle.manifest import (
    ManifestError,
    append_manifest,
    detect_installed_version,
    read_manifest_generations,
)
from specle.schema_registry import (
    SchemaRegistryError,
    export_schemas,
    validate_instance,
)
from specle.update_models import UpdatePlan


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
    update = commands.add_parser(
        "update", help="Update a Specle deployment from the packaged blueprints."
    )
    update.add_argument(
        "target_directory", help="Existing directory containing the Specle deployment."
    )
    update.add_argument(
        "--dry-run", action="store_true", help="Report the update plan without writing."
    )
    update.add_argument(
        "--yes",
        action="store_true",
        help="Apply every confirmation-required action in the displayed update plan.",
    )
    update.add_argument(
        "--force",
        action="store_true",
        help="Replace all managed content, including locally modified resources.",
    )
    validate = commands.add_parser(
        "validate",
        help="Validate a Specle target or packaged blueprints without changing it.",
    )
    validate.add_argument(
        "target_directory",
        nargs="?",
        help="Existing directory containing the Specle runtime to validate.",
    )
    manifest = commands.add_parser(
        "manifest", help="Append release provenance lines to a manifest output."
    )
    manifest.add_argument("output", help="Manifest file to create or append.")
    validate.add_argument(
        "--blueprint",
        action="store_true",
        help="Validate the packaged blueprint inventory instead of an installed target.",
    )
    validate.add_argument(
        "--verbose",
        action="store_true",
        help="Report each completed validation area and its summary count.",
    )
    schemas = commands.add_parser(
        "schemas", help="Manage the packaged Specle JSON Schema resources."
    )
    schema_commands = schemas.add_subparsers(dest="schemas_command", required=True)
    export = schema_commands.add_parser(
        "export", help="Export all packaged schemas to a destination directory."
    )
    export.add_argument(
        "destination", help="Directory to create or replace with schemas."
    )
    export.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing schema destination after staging a complete export.",
    )
    return parser


async def main(args: list[str] | None = None) -> None:
    """Run the asynchronous Specle command-line application."""
    parser = build_parser()
    parsed = parser.parse_args(args)

    if parsed.command == "manifest":
        try:
            version = __version__
            with as_file(packaged_distribution_root()) as source_root:
                inventory = scan_managed_inventory(source_root)
                appended = await anyio.to_thread.run_sync(
                    partial(append_manifest, Path(parsed.output), inventory, version)
                )
        except (ManifestError, SkillMetadataError) as error:
            raise SystemExit(str(error)) from error
        print(f"appended {appended} manifest line(s) for {version}: {parsed.output}")
        return

    if parsed.command == "validate":
        if parsed.blueprint == (parsed.target_directory is not None):
            parser.error(
                "validate requires exactly one of TARGET_DIRECTORY or --blueprint"
            )
        if parsed.blueprint:
            try:
                with as_file(packaged_distribution_root()) as source_root:
                    inventory = scan_managed_inventory(source_root)
                    skills = tuple(record.metadata for record in inventory.skills)
                    diagnostics = list(inventory.lifecycle.diagnostics)
                    diagnostics.extend(
                        _diagnostic(message)
                        for message in inventory.package_diagnostics
                    )
                    index = build_skill_index(skills)
                    diagnostics.extend(
                        _diagnostic(f"unmanaged package skill: {path}")
                        for path in inventory.unmanaged_skill_files
                    )
            except SkillMetadataError as error:
                print(_diagnostic(str(error)).message)
                raise SystemExit(1) from error
            try:
                validate_instance(index)
            except SchemaRegistryError as error:
                diagnostics.append(
                    _diagnostic(f"invalid generated skill index: {error}")
                )
            if diagnostics:
                for diagnostic in diagnostics:
                    print(diagnostic.message)
                raise SystemExit(1)
            if parsed.verbose:
                _report_validation_summary(inventory, index_path=None)
                print("validated mode: blueprint")
            print("validated blueprint")
            return
        await _validate_installed_target(
            Path(parsed.target_directory), verbose=parsed.verbose
        )
        return

    if parsed.command == "update":
        target = Path(parsed.target_directory).expanduser().resolve()
        try:
            with as_file(packaged_distribution_root()) as source_root:
                blueprint = await anyio.to_thread.run_sync(
                    partial(scan_managed_inventory, source_root)
                )
                if blueprint.package_diagnostics:
                    raise SkillMetadataError(blueprint.package_diagnostics[0])
                if blueprint.lifecycle.diagnostics:
                    raise SkillMetadataError(blueprint.lifecycle.diagnostics[0].message)
                installed = await anyio.to_thread.run_sync(
                    partial(scan_managed_inventory, target / ".agents")
                )
                if installed.lifecycle.diagnostics:
                    raise SkillInstallationError(
                        installed.lifecycle.diagnostics[0].message
                    )
                generations = await anyio.to_thread.run_sync(
                    partial(read_manifest_generations, source_root / "manifest")
                )
                detection = await anyio.to_thread.run_sync(
                    partial(
                        detect_installed_version,
                        managed_resource_checksums(installed),
                        generations,
                    )
                )
                plan = await anyio.to_thread.run_sync(
                    partial(
                        update_distribution,
                        source_root,
                        target,
                        blueprint,
                        installed,
                        generations,
                        detection,
                        dry_run=True,
                    )
                )
                _report_update_plan(plan, force=parsed.force, dry_run=parsed.dry_run)
                if parsed.dry_run:
                    print("dry run: no changes made")
                    return
                result = await anyio.to_thread.run_sync(
                    partial(
                        update_distribution,
                        source_root,
                        target,
                        blueprint,
                        installed,
                        generations,
                        detection,
                        plan=plan,
                        force=parsed.force,
                        approve_conflicts=parsed.yes,
                    )
                )
        except (ManifestError, SkillInstallationError, SkillMetadataError) as error:
            raise SystemExit(str(error)) from error
        if not result.converged:
            print(
                "update requires --yes to apply every confirmation-required action; "
                "no changes made"
            )
            raise SystemExit(1)
        applied_actions = parsed.force or bool(result.actions)
        if applied_actions:
            await _validate_installed_target(target)
        if parsed.force or any(
            action.action in {"add", "upgrade", "remove", "replace-skill"}
            for action in plan.actions
        ):
            print("updated deployment")
        return

    if parsed.command == "schemas":
        try:
            destination = await anyio.to_thread.run_sync(
                partial(export_schemas, Path(parsed.destination), force=parsed.force)
            )
        except SchemaRegistryError as error:
            raise SystemExit(str(error)) from error
        print(destination)
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


async def _validate_installed_target(target: Path, *, verbose: bool = False) -> None:
    """Validate one installed target without re-entering the CLI dispatcher."""
    resolved_target = target.expanduser().resolve()
    diagnostics: list[LifecycleDiagnostic] = []
    with as_file(packaged_distribution_root()) as source_root:
        try:
            blueprint = await anyio.to_thread.run_sync(
                partial(scan_managed_inventory, source_root)
            )
            installed = await anyio.to_thread.run_sync(
                partial(scan_managed_inventory, resolved_target / ".agents")
            )
        except SkillMetadataError as error:
            diagnostics.append(_diagnostic(str(error)))
            skills = ()
        else:
            skills = tuple(record.metadata for record in installed.skills)
            diagnostics.extend(installed.lifecycle.diagnostics)
            diagnostics.extend(
                _diagnostic(message)
                for message in compare_managed_inventories(blueprint, installed)
            )
            runtime = await anyio.to_thread.run_sync(
                partial(read_runtime_snapshot, resolved_target)
            )
            diagnostics.extend(
                await anyio.to_thread.run_sync(
                    partial(validate_runtime_records, resolved_target, skills, runtime)
                )
            )
    index_path = resolved_target / ".agents" / "skills" / "specle" / "index.json"
    try:
        index = await anyio.to_thread.run_sync(partial(_read_index, index_path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        diagnostics.append(
            _diagnostic(f"invalid generated skill index: {index_path}: {error}")
        )
    else:
        expected_index = build_skill_index(skills)
        if index != expected_index:
            diagnostics.append(
                _diagnostic(f"invalid generated skill index: {index_path}")
            )
        else:
            try:
                validate_instance(index)
            except SchemaRegistryError as error:
                diagnostics.append(
                    _diagnostic(f"invalid generated skill index: {index_path}: {error}")
                )
    if diagnostics:
        for diagnostic in diagnostics:
            print(diagnostic.message)
        raise SystemExit(1)
    if verbose:
        _report_validation_summary(installed, index_path=index_path)
        selected = runtime.state.selected_name or "none"
        print(f"validated active changes: {len(runtime.state.active)}")
        print(f"validated archived changes: {len(runtime.state.archived)}")
        print(f"validated local selection: {selected}")
    print(f"validated {resolved_target}")


def _read_index(path: Path) -> dict[str, object]:
    """Read generated JSON in a worker thread for installed-target validation."""
    return cast(dict[str, object], json.loads(read_regular_text(path)))


def _report_validation_summary(
    inventory: DistributionInventory, *, index_path: Path | None
) -> None:
    """Print stable verbose summaries shared by validation modes."""
    print(f"validated managed skills: {len(inventory.skills)}")
    print(
        "validated lifecycle graph: "
        f"{len(inventory.lifecycle.statuses)} statuses, "
        f"{len(inventory.lifecycle.terminal)} terminal"
    )
    if index_path is None:
        print("validated generated skill index model")
    else:
        print(f"validated skill index: {index_path}")


def _report_update_plan(
    plan: UpdatePlan, *, force: bool, dry_run: bool = False
) -> None:
    """Render the stable, user-facing update plan without exposing implementation types."""
    version = plan.version or "unknown"
    print(
        "detected version: "
        f"{version} ({plan.confidence}; "
        f"{plan.matched}/{plan.compared} resources matched)"
    )
    actions = plan.actions
    if actions:
        for action in actions:
            prefix = "confirm " if action.requires_confirmation and not force else ""
            print(f"{prefix}{action.action}: {action.path}")
    else:
        print("deployment is already current")
    for guidance in plan.project_guidance:
        print(f"project: {guidance}")
    if force:
        if dry_run:
            print("force: normal update confirmations would be bypassed")
        else:
            print("force: normal update confirmations were bypassed")


def run() -> None:
    """Run the application using AnyIO's default asyncio runtime."""
    anyio.run(main)


if __name__ == "__main__":
    run()
