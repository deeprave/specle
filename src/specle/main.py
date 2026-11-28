"""Command-line entry point for Specle."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import UTC, datetime
from importlib.resources import as_file
from pathlib import Path
from typing import cast
from uuid import uuid4

import anyio

from specle import __version__
from specle.change_state import (
    ChangeIssue,
    ChangeRecord,
    read_active_sidecars,
    read_change_state,
)
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
    next_lifecycle_action,
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
    changes = commands.add_parser(
        "changes", help="List active or archived Specle changes."
    )
    changes.add_argument(
        "--archive", action="store_true", help="List archived changes instead."
    )
    formats = changes.add_mutually_exclusive_group()
    formats.add_argument(
        "--json", action="store_true", help="Render machine-readable JSON."
    )
    formats.add_argument("--csv", action="store_true", help="Render CSV output.")
    changes.add_argument(
        "--pretty", action="store_true", help="Indent JSON output with two spaces."
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
    index = commands.add_parser(
        "index", help="Regenerate an installed Specle skill index."
    )
    index.add_argument("target_directory", help="Existing deployment directory.")
    index.add_argument(
        "--force", action="store_true", help="Regenerate despite lifecycle diagnostics."
    )
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

    if parsed.command in {"changes", "init", "update", "index"} or (
        parsed.command == "validate"
        and not parsed.blueprint
        and parsed.target_directory
    ):
        target = (
            Path.cwd() if parsed.command == "changes" else Path(parsed.target_directory)
        )
        await _preflight_project(target)

    if parsed.command == "changes":
        if parsed.pretty and not parsed.json:
            parser.error("changes --pretty requires --json")
        await _report_changes(
            Path.cwd(),
            archived=parsed.archive,
            as_json=parsed.json,
            as_csv=parsed.csv,
            pretty=parsed.pretty,
        )
        return

    if parsed.command == "index":
        target = Path(
            await (await anyio.Path(parsed.target_directory).expanduser()).resolve()
        )
        try:
            await _regenerate_index(target, force=parsed.force)
        except (OSError, SkillMetadataError) as error:
            raise SystemExit(str(error)) from error
        print(target / ".agents" / "skills" / "specle" / "index.json")
        return

    if parsed.command == "manifest":
        try:
            version = __version__
            with as_file(await packaged_distribution_root()) as source_root:
                inventory = await scan_managed_inventory(source_root)
                appended = await append_manifest(
                    Path(parsed.output), inventory, version
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
                with as_file(await packaged_distribution_root()) as source_root:
                    inventory = await scan_managed_inventory(source_root)
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
                await validate_instance(index)
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
        target = Path(
            await (await anyio.Path(parsed.target_directory).expanduser()).resolve()
        )
        try:
            with as_file(await packaged_distribution_root()) as source_root:
                blueprint = await scan_managed_inventory(source_root)
                if blueprint.package_diagnostics:
                    raise SkillMetadataError(blueprint.package_diagnostics[0])
                if blueprint.lifecycle.diagnostics:
                    raise SkillMetadataError(blueprint.lifecycle.diagnostics[0].message)
                installed = await scan_managed_inventory(target / ".agents")
                if installed.lifecycle.diagnostics:
                    raise SkillInstallationError(
                        installed.lifecycle.diagnostics[0].message
                    )
                generations = await read_manifest_generations(source_root / "manifest")
                detection = detect_installed_version(
                    managed_resource_checksums(installed), generations
                )
                plan = await update_distribution(
                    source_root,
                    target,
                    blueprint,
                    installed,
                    generations,
                    detection,
                    dry_run=True,
                )
                _report_update_plan(plan, force=parsed.force, dry_run=parsed.dry_run)
                if parsed.dry_run:
                    print("dry run: no changes made")
                    return
                result = await update_distribution(
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
            destination = await export_schemas(
                Path(parsed.destination), force=parsed.force
            )
        except SchemaRegistryError as error:
            raise SystemExit(str(error)) from error
        print(destination)
        return

    try:
        with as_file(await packaged_distribution_root()) as source_root:
            installed = await initialise_distribution(
                source_root,
                Path(parsed.target_directory),
                force=parsed.force,
            )
    except (SkillInstallationError, SkillMetadataError) as error:
        raise SystemExit(str(error)) from error

    for path in installed:
        print(path)


def _diagnostic(message: str) -> LifecycleDiagnostic:
    return LifecycleDiagnostic("invalid-index", message)


async def _report_changes(
    target: Path,
    *,
    archived: bool,
    as_json: bool,
    as_csv: bool,
    pretty: bool = False,
) -> None:
    """Render one read-only deterministic view of durable change records."""
    snapshot = await read_change_state(target, tolerant_archive_dates=True)
    has_registry, active_sidecars, sidecar_diagnostics = await read_active_sidecars(
        target, snapshot
    )
    for diagnostic in snapshot.diagnostics:
        if "current-change" in diagnostic and (
            "unreadable selector" in diagnostic
            or "expected one stable change name" in diagnostic
        ):
            raise SystemExit("invalid or unreadable selector")
    records = snapshot.archived if archived else snapshot.active
    issues = snapshot.archived_issues if archived else snapshot.active_issues
    rows = []
    for record in records:
        timestamp, date, diagnostic = _report_timestamp(record, archived=archived)
        rows.append(
            {
                "name": record.name,
                "kind": record.status.get("kind"),
                "status": record.status.get("status"),
                "dependencies": record.status.get("dependencies", []),
                "timestamp": timestamp,
                "date": date,
                "next_action": await next_lifecycle_action(
                    record, snapshot.selected_name
                ),
                "diagnostic": _static_diagnostic(diagnostic) if diagnostic else None,
            }
        )
    rows.extend(_issue_row(issue) for issue in issues)
    if not archived:
        rows = [
            row
            for row in rows
            if row["diagnostic"] is not None or row["status"] != "complete"
        ]
    rows.sort(key=lambda row: str(row["name"]))
    include_diagnostics = any(row["diagnostic"] is not None for row in rows)
    if as_json:
        json_rows = [
            {
                key: value
                for key, value in row.items()
                if key != "date" and (key != "diagnostic" or value is not None)
            }
            for row in rows
        ]
        result: dict[str, object] = {
            "collection": "archive" if archived else "active",
            "changes": json_rows,
        }
        if has_registry:
            result["active_sidecars"] = active_sidecars
            result["sidecar_diagnostics"] = sidecar_diagnostics
        print(
            json.dumps(
                result,
                indent=2 if pretty else None,
                allow_nan=False,
            )
        )
        return
    for diagnostic in sidecar_diagnostics:
        print(diagnostic, file=sys.stderr)
    if as_csv:
        writer = csv.writer(sys.stdout, lineterminator="\r\n")
        headers = ["name", "date", "kind", "status", "dependencies", "next_action"]
        if has_registry:
            headers.append("local_active")
        if include_diagnostics:
            headers.append("diagnostic")
        writer.writerow(headers)
        for row in rows:
            values = [
                row["name"],
                row["date"] or "",
                row["kind"],
                row["status"],
                _format_dependencies(row["dependencies"], empty=""),
                row["next_action"] or "",
            ]
            if has_registry:
                values.append("yes" if row["name"] in active_sidecars else "")
            if include_diagnostics:
                values.append(row["diagnostic"] or "")
            writer.writerow(values)
        return
    if not rows:
        print("no archived changes" if archived else "no active changes")
        return
    headers = ["name", "date", "kind", "status", "dependencies", "next_action"]
    if has_registry:
        headers.append("local_active")
    if include_diagnostics:
        headers.append("diagnostic")
    print("\t".join(headers))
    for row in rows:
        dependencies = _format_dependencies(row["dependencies"], empty="—")
        next_action = row["next_action"] or "—"
        values = [
            row["name"],
            row["date"] or "—",
            row["kind"] or "—",
            row["status"] or "—",
            dependencies,
            next_action,
        ]
        if has_registry:
            values.append("yes" if row["name"] in active_sidecars else "—")
        if include_diagnostics:
            diagnostic = row["diagnostic"]
            values.append(_static_diagnostic(diagnostic) if diagnostic else "")
        print("\t".join(str(value) for value in values))


async def _preflight_project(target: Path) -> None:
    root = await anyio.Path(target).expanduser()
    for relative in (".specle/changes", ".specle/archive", ".agents", ".agents/skills"):
        candidate = root / relative
        if (
            await candidate.exists() or await candidate.is_symlink()
        ) and not await candidate.is_dir():
            raise SystemExit(f"{candidate}: expected a directory")


def _static_diagnostic(value: object) -> str:
    """Return a stable text-report cause without embedded source data."""
    message = str(value)
    for reason in (
        "invalid dependencies",
        "malformed JSON",
        "unreadable JSON",
        "invalid contract",
        "invalid created_at",
        "missing",
        "expected a JSON object",
    ):
        if reason in message:
            return reason
    return "invalid change record"


def _report_timestamp(
    record: ChangeRecord, *, archived: bool
) -> tuple[int | float | None, str | None, str | None]:
    """Validate one report timestamp before emitting output in any format."""
    field = "created_at"
    optional = False
    if archived:
        if record.status.get("status") not in {"complete", "cancelled"}:
            return None, None, None
        field = (
            "cancelled_at"
            if record.status.get("status") == "cancelled"
            else "archived_at"
        )
        optional = True
    timestamp = record.status.get(field)
    if timestamp is None and optional:
        return None, None, None
    if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
        return None, None, None if optional else _timestamp_diagnostic(record, field)
    try:
        finite = math.isfinite(timestamp)
    except OverflowError:
        finite = False
    if not finite:
        return None, None, None if optional else _timestamp_diagnostic(record, field)
    assert isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool)
    try:
        return (
            timestamp,
            datetime.fromtimestamp(timestamp, UTC).date().isoformat(),
            None,
        )
    except (OverflowError, OSError, ValueError):
        return None, None, None if optional else _timestamp_diagnostic(record, field)


def _timestamp_diagnostic(record: ChangeRecord, field: str) -> str:
    return f"{record.directory / 'status.json'}: invalid {field}"


def _issue_row(issue: ChangeIssue) -> dict[str, object]:
    """Render a discoverable malformed record without making it look valid."""
    return {
        "name": issue.name,
        "kind": None,
        "status": None,
        "dependencies": [],
        "timestamp": None,
        "date": None,
        "next_action": None,
        "diagnostic": _static_diagnostic(issue.diagnostic),
    }


def _format_dependencies(value: object, *, empty: str) -> str:
    """Render the schema-validated dependencies field in one output format."""
    if not isinstance(value, list) or not value:
        return empty
    return ",".join(str(item) for item in value)


async def _regenerate_index(target: Path, *, force: bool = False) -> None:
    """Atomically replace only an existing deployment's generated skill index."""
    inventory = await scan_managed_inventory(target / ".agents")
    if inventory.lifecycle.diagnostics:
        for diagnostic in inventory.lifecycle.diagnostics:
            print(diagnostic.message, file=sys.stderr)
        if not force:
            raise SkillMetadataError("lifecycle diagnostics prevent index regeneration")
    if not any(record.metadata.name == "specle" for record in inventory.skills):
        raise SkillMetadataError(
            "the installed managed skill inventory has no valid 'specle' skill"
        )
    destination = anyio.Path(target / ".agents" / "skills" / "specle" / "index.json")
    if not await destination.parent.is_dir():
        raise SkillMetadataError(
            f"installed skill index directory is unavailable: {destination.parent}"
        )
    if await destination.is_dir():
        raise SkillMetadataError(
            f"installed skill index destination is a directory: {destination}"
        )
    temporary: anyio.Path | None = None
    try:
        for _ in range(10):
            candidate = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
            try:
                handle = await candidate.open("x", encoding="utf-8")
            except FileExistsError:
                continue
            temporary = candidate
            async with handle:
                await handle.write(
                    json.dumps(
                        build_skill_index(
                            tuple(record.metadata for record in inventory.skills)
                        ),
                        indent=2,
                    )
                    + "\n"
                )
            break
        else:
            raise OSError(f"unable to create temporary skill index: {destination}")
        await temporary.chmod(0o644)
        await temporary.replace(destination)
    except BaseException:
        if temporary is not None:
            with anyio.CancelScope(shield=True):
                await temporary.unlink(missing_ok=True)
        raise


async def _validate_installed_target(target: Path, *, verbose: bool = False) -> None:
    """Validate one installed target without re-entering the CLI dispatcher."""
    resolved_target = Path(await (await anyio.Path(target).expanduser()).resolve())
    diagnostics: list[LifecycleDiagnostic] = []
    with as_file(await packaged_distribution_root()) as source_root:
        try:
            blueprint = await scan_managed_inventory(source_root)
            installed = await scan_managed_inventory(resolved_target / ".agents")
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
            runtime = await read_runtime_snapshot(resolved_target)
            diagnostics.extend(
                await validate_runtime_records(resolved_target, skills, runtime)
            )
    index_path = resolved_target / ".agents" / "skills" / "specle" / "index.json"
    try:
        index = await _read_index(index_path)
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
                await validate_instance(index)
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


async def _read_index(path: Path) -> dict[str, object]:
    """Read generated JSON for installed-target validation."""
    return cast(
        dict[str, object], json.loads(await read_regular_text(anyio.Path(path)))
    )


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
