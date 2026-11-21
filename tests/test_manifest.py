from __future__ import annotations

from pathlib import Path

import pytest

from specle import __version__
from specle.inventory import scan_managed_inventory
from specle.manifest import ManifestError, append_manifest, build_manifest_lines


def test_builds_stable_release_manifest_lines_from_shared_inventory() -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    lines = build_manifest_lines(scan_managed_inventory(blueprints), __version__)

    assert lines == tuple(sorted(lines))
    assert any(
        line.startswith(f"{__version__}:skill/define/SKILL.md:") for line in lines
    )
    assert any(
        line.startswith(f"{__version__}:policies/lifecycle.md:") for line in lines
    )
    assert all("/index.json:" not in line for line in lines)


def test_appends_missing_lines_without_rewriting_existing_entries(
    tmp_path: Path,
) -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    expected = build_manifest_lines(inventory, __version__)
    output.write_text(f"{expected[0]}\n")

    assert append_manifest(output, inventory, __version__) == len(expected) - 1
    assert output.read_text().splitlines() == list(expected)
    original = output.read_text()
    assert append_manifest(output, inventory, __version__) == 0
    assert output.read_text() == original


def test_rejects_conflicting_checksum_without_rewriting_output(tmp_path: Path) -> None:
    output = tmp_path / "manifest"
    output.write_text(f"{__version__}:policies/lifecycle.md:{'0' * 64}\n")
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    with pytest.raises(ManifestError, match="conflicting checksum"):
        append_manifest(output, scan_managed_inventory(blueprints), __version__)

    assert output.read_text() == f"{__version__}:policies/lifecycle.md:{'0' * 64}\n"


def test_rejects_malformed_existing_manifest_without_rewriting_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "manifest"
    output.write_text("not-a-manifest-entry\n")
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    with pytest.raises(ManifestError, match="invalid manifest line"):
        append_manifest(output, scan_managed_inventory(blueprints), __version__)

    assert output.read_text() == "not-a-manifest-entry\n"


def test_rejects_duplicate_identity_without_rewriting_output(tmp_path: Path) -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    entry = build_manifest_lines(inventory, __version__)[0]
    output.write_text(f"{entry}\n{entry}\n")

    with pytest.raises(ManifestError, match="duplicate manifest entry"):
        append_manifest(output, inventory, __version__)

    assert output.read_text() == f"{entry}\n{entry}\n"
